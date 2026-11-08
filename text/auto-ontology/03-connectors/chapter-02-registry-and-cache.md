# Chapter 02. Registry의 연결 선택·수집 범위·캐시 갱신

Registry는 연결 설정을 읽어 DB별 connector 객체를 만들고 재사용하는 모듈이다. **저장된 연결이 우선이며, 저장 목록을 만들지 못하거나 목록이 비었을 때만 `CONNECTION_STRINGS` 환경 변수로 대체한다.** 두 목록을 합치지 않는다. 설정 저장, 객체 재생성, 원본 DB 메타데이터 재수집은 각각 다른 단계이므로 저장 성공만으로 모든 단계의 성공을 판단할 수 없다.

이 문서는 로컬 코드의 정적 분석이다. DB 접속·서비스·테스트는 실행하지 않았다. 앞 장의 [공통 계약](chapter-01-common-contract.md), [저장 경계](../02-data-model/chapter-04-storage-boundaries.md), [용어집](../01-architecture/chapter-00-glossary.md)을 함께 참고한다.

## 1. 이 장에서 구분하는 개념과 책임

| 용어·컴포넌트 | 쉬운 뜻과 이 프로젝트의 역할 |
| --- | --- |
| 연결 설정 | 엔진 종류·주소·DB 이름·인증 정보·수집 범위를 담은 사전(dict). 아직 원본 DB 연결 객체가 아니다. |
| 연결 문자열(URL) | `postgresql://user:password@host:5432/sales`처럼 설정을 한 문자열로 표현한 값. 예시는 가상 값이다. |
| scheme | URL의 `://` 앞부분. 어떤 connector 클래스를 고를지 결정한다. |
| connector | 원본 DB 메타데이터 조회와 SQL 실행을 제공하는 `SQLDatabase` 구현 객체. 생성만으로 접속 확인이 끝나는지는 구현에 달려 있다. |
| Registry | scheme → 클래스 대응표 및 설정 로딩·객체 생성·재사용을 담당하는 `connectors/registry.py`. |
| cache(캐시) | 한 번 만든 객체를 메모리에 보관해 다음 호출에서 재사용하는 장치. 이 코드의 `_connectors`는 프로세스 내부 값이다. |
| invalidation(무효화) | 캐시가 가진 객체에 `close()`를 호출하고 보관 값을 `None`으로 바꾸는 작업. 새 객체는 다음 조회 때 만든다. |
| catalog | 원본 DB의 구조와 분석 결과를 저장하는 메타데이터 저장소. 원본 DB 자체와 구분한다. |
| DAL(Data Access Layer) | 저장소를 읽고 쓰는 계층. `dal/connections.py`가 catalog에서 연결 설정을 읽는다. |
| Vault | 비밀번호 등 비밀 정보를 별도 보관하는 외부 저장소. 연결마다 설정 사전 전체를 읽어오는 경로가 있다. |
| worker·standby | 질문을 처리하는 별도 프로세스와, 다음 질문을 위해 미리 준비해 둔 대기 프로세스. |
| allowlist·denylist | 포함할 대상 목록·제외할 대상 목록. 이 장에서는 schema 이름 목록과 테이블 이름 정규식으로 표현한다. |

책임은 다음과 같이 나뉜다.

| 파일·핵심 함수 | 입력 → 출력·작업 |
| --- | --- |
| `dal/connections.py::list_connections` | catalog DB 행 → Vault 또는 행에 저장된 연결 dict 목록 |
| `connection_string_factory.py::build_connection_string` | 연결 dict → 엔진별 URL |
| `registry.py::create_connector` | URL·schema 목록·테이블 필터 → connector 객체 |
| `registry.py::get_connectors` | 저장 설정 또는 환경 변수 → 캐시된 connector 목록의 복사본 |
| `server/connections/service.py` | 생성·수정·삭제 → 저장 후 캐시 갱신 및 필요한 수집 요청 |
| `catalog/table_filter.py` | 정규식 → 포함/제외 판정, 추출된 메타데이터 행 필터링 |

근거: [Registry](../../../code/auto-ontology/auto_ontology/connectors/registry.py), [DAL](../../../code/auto-ontology/auto_ontology/dal/connections.py), [문자열 변환](../../../code/auto-ontology/auto_ontology/connectors/connection_string_factory.py).

## 2. 연결 목록을 선택하는 실제 순서

`get_connectors()`는 `_connectors is None`일 때만 설정을 읽는다. 이미 캐시가 있으면 저장소와 환경 변수를 다시 확인하지 않는다.

```mermaid
flowchart TD
    A[get_connectors 호출] --> B{프로세스 캐시가 있는가}
    B -->|있음| R[목록 복사본 반환]
    B -->|없음| C[catalog 행 조회]
    C --> D[행마다 Vault 우선, 없으면 저장 JSON]
    D --> E[전체 목록의 URL과 필터 spec 생성]
    C -->|예외| F[저장 spec을 빈 목록으로 처리]
    D -->|예외| F
    E -->|예외| F
    E --> G{spec이 비었는가}
    F --> G
    G -->|예| H[CONNECTION_STRINGS 분리]
    G -->|아니오| I[선택한 spec으로 connector 생성]
    H --> J{환경 목록도 비었는가}
    J -->|예| K[캐시는 None 유지, 빈 목록 반환]
    J -->|아니오| I
    I -->|모두 생성| L[객체 목록을 캐시에 저장]
    L --> R
    I -->|생성 예외| X[호출 실패, 완성된 캐시 없음]
```

### 2.1 저장된 연결 안에서도 Vault가 우선한다

`list_connections()`는 `catalog_database`의 `name`, `connection`을 이름순으로 읽는다. 각 행에서 다음 순서를 따른다.

1. `read_secret(row.name)`이 값이 있는 dict를 반환하면 그 값을 사용한다.
2. 그렇지 않고 행의 `connection`에 값이 있으면 사용한다. 문자열이면 `json.loads`, 이미 객체이면 그대로 반환한다.
3. 둘 다 없으면 해당 행은 연결 목록에서 제외한다.

Vault 값과 catalog JSON을 필드별로 합치지 않는다. Vault 값이 있으면 그 객체 전체가 우선한다. 또한 **catalog 행을 순회하면서 Vault를 조회**하므로, Vault에만 존재하고 catalog DB 행이 없는 항목을 이 함수가 발견하지는 않는다.

여기서 “fallback(대체 경로)”은 값이 없거나 상위 로딩이 실패할 때 다른 출처를 선택한다는 뜻이다. Vault 예외 처리 자체는 Vault 구현에 달려 있으며, 여기서 확인한 것은 `list_connections()` 안에 행별 예외 격리가 없고 Registry가 저장 목록 생성 단계 전체의 예외를 받는다는 점이다. Vault 내부 통신·인증은 후속 장에서 다룬다.

### 2.2 환경 변수는 보충 목록이 아니다

| 상황 | Registry가 선택하는 목록 |
| --- | --- |
| 저장 연결 2개, 환경 연결 1개 | 저장 연결 2개만 사용 |
| 저장 연결 없음 | 환경 연결 사용 |
| 저장소 조회 또는 URL 변환 중 예외 | 저장 spec 전체를 비우고 환경 연결 사용 |
| 저장 spec은 완성됐지만 connector 생성 중 예외 | 그 예외를 전파. 이 단계에서는 환경 연결로 다시 시도하지 않음 |
| 어느 쪽에도 연결 없음 | 경고 후 `[]`. `_connectors`는 `None` 유지 |

저장 목록의 URL 변환은 한 개의 리스트 내포식으로 수행한다. 따라서 저장 연결 A는 정상이더라도 B의 필수 필드 누락으로 URL 변환이 실패하면, A만 살리는 처리가 아니라 저장 spec 전체를 버리는 경로다. 반대로 잘못된 테이블 정규식은 `_table_filter()`가 자체 처리하므로 이 단계의 전체 실패로 이어지지 않는다.

`parse_connection_strings()`는 쉼표·CR·LF(줄바꿈 문자)로 분리하고 공백·빈 항목을 제거한다. URL 문법 검사는 이 함수가 하지 않는다. URL 값 안에 구분자로 쓰일 문자가 있다면 문자열 분리와 혼동하지 않도록 인코딩되어 있어야 한다.

`server/connections/router.py::is_env_source()`는 환경 변수에 비어 있지 않은 값이 있는지만 보고한다. **실제 Registry가 환경 목록을 선택했다는 증명은 아니다.** 저장 목록이 우선되는 위 분기와 별개다.

근거: [Registry의 get_connectors·parse_connection_strings](../../../code/auto-ontology/auto_ontology/connectors/registry.py), [연결 API router](../../../code/auto-ontology/auto_ontology/server/connections/router.py).

## 3. 연결 dict는 어떻게 실행 객체가 되는가

### 3.1 문자열 변환과 클래스 선택은 서로 다른 단계다

`build_connection_string()`은 `type`을 소문자로 정리하고 엔진별 필드를 요구한다. `_require()`는 비어 있는 필드에 `ValueError`를 발생시킨다. `_enc()`는 사용자명·비밀번호·DB 이름 등의 URL 예약 문자를 percent encoding으로 바꾼다. 예를 들어 비밀번호의 `@`를 `%40`으로 표현해 주소 구분 문자와 구별한다.

| 변환 분기 | 이번 장에서 확인한 특징 |
| --- | --- |
| Postgres·MySQL | host·user·password·database 필수, 기본 port 적용 |
| Snowflake | account·warehouse·user·database 필수. private key가 있으면 키 인증 URL, 없으면 password 요구 |
| Databricks | host·http_path·database 요구. 사용자별 토큰 override 우선, 없으면 저장 password. override 사용 시 `auth=sso` 추가 |
| Kyuubi | host·user·password·database, 선택적인 인증 서버·인증서 저장 정보 전달 |
| Trino | host·user·database 필수, password 선택. 기본 schema와 통신 scheme 전달 가능 |
| ClickHouse | host·database 필수, user/password 선택. host에 포함된 port와 명시 port 조정 |
| HeavyDB | host·user·password·database 및 protocol |
| SQLite·DuckDB | Registry에는 있지만 이 dict→URL 변환 함수에 해당 분기가 없음 |

마지막 차이가 중요하다. **URL로 connector를 직접 만드는 지원 범위와 저장 dict를 URL로 변환하는 지원 범위가 같지 않다.** SQLite dict가 저장되어 있으면 현재 factory는 `Unsupported connection type`을 발생시킨다. SQLite URL을 환경 변수로 주거나 `create_connector()`에 직접 주는 경로와 구분해야 한다.

### 3.2 create_connector의 분기

1. `urlparse()`로 scheme을 얻는다. scheme이 없으면 예외다.
2. scheme을 `+` 앞에서 자르고 소문자로 바꾼다. 예컨대 `postgresql+psycopg`는 Registry에서 `postgresql` 클래스로 선택된다. 이후 전체 URL을 해석할 수 있는지는 해당 connector 책임이다.
3. `CONNECTOR_REGISTRY`에서 클래스를 찾는다. `postgres`, `postgresql`은 같은 클래스이며, MySQL·Databricks·DuckDB·Snowflake·ClickHouse·HeavyDB·Kyuubi·SQLite·Trino가 등록되어 있다.
4. schema 목록이 있고 클래스가 Databricks·Snowflake·Kyuubi·Trino이면 생성자에 `schemas=`를 전달한다. 그 밖의 클래스에는 전달하지 않는다.
5. 활성 테이블 필터가 있으면 생성된 객체의 `table_filter` 속성에 붙인다. 이 필터를 모든 생성자의 인자로 전달하는 구조는 아니다.

Registry의 scheme과 SQL parser가 사용하는 dialect(엔진별 SQL 문법 이름)는 다른 값이다. 예를 들어 HeavyDB의 scheme은 `heavydb`지만 해당 구현의 dialect는 `postgres`다. 이 구분은 [공통 계약](chapter-01-common-contract.md)의 SQL 문법 계약과 연결된다.

### 3.3 database_name은 질의 연결을 찾는 키다

Registry는 생성한 객체의 `database_name`을 모아 중복을 검사한다. 중복이면 **경고만 남기고 두 객체를 모두 목록에 추가**한다. 자동으로 하나를 제거하거나 이름을 바꾸지 않는다. 따라서 “중복 경고가 있다”와 “중복이 방지된다”는 다르다.

저장 연결 생성 함수는 기존 저장 설정의 DB 이름을 대소문자 구분 없이 비교해 중복을 거부한다. 그러나 Registry 중복 검사는 반환된 `database_name`의 정확한 문자열 비교다. 환경 연결이나 직접 생성 경로 전체를 같은 검증으로 보호한다고 볼 수 없다. 실제 SQL 대상 선택의 충돌 처리는 SQL 생성·실행 분석에서 추가 확인한다.

## 4. schema 필터와 table 필터가 적용되는 위치

schema는 DB 안에서 테이블을 묶는 이름 공간이다. 예를 들어 `sales.orders`에서 `sales`가 schema다. 정규식(regex)은 `^fact_`처럼 이름의 일정한 패턴을 표현하는 문자열이다.

| 구분 | schema allowlist | table allow/deny regex |
| --- | --- | --- |
| 설정 필드 | `schemas` | `table_allow_regex`, `table_deny_regex` |
| 정리 | 리스트일 때만 문자열·공백 정리. 결과가 비면 `None` | 공백을 제거하고 `re.compile()` |
| 객체 전달 | 위 4개 클래스 생성자에만 `schemas=` | 활성 필터를 connector 속성에 부착 |
| 적용 위치 | 엔진별 메타데이터 조회 구현 | 공통 `catalog/extract.py::create_dataframe()` |
| 환경 URL 경로 | Registry의 별도 schema 인자로는 전달되지 않음 | 연결 dict가 없어 비활성 필터 사용 |
| SQL 실행 제한인가 | 해당 Registry 인자는 수집 범위용 | 공통 필터도 수집 범위용 |

환경 URL에 엔진 자체의 schema 관련 query parameter가 있는지는 각 엔진에서 별도로 해석할 수 있다. 위 표는 Registry가 전달하는 `schemas` 인자와 테이블 필터에 대한 설명이다.

```mermaid
flowchart LR
    A[저장 연결 dict] --> B[schema 목록 정리]
    B --> C[지원 엔진 생성자]
    C --> D[원본 메타데이터 조회]
    A --> E[allow와 deny 정규식 생성]
    E --> F[connector.table_filter]
    D --> G[공통 create_dataframe]
    F --> G
    G --> H[tables와 columns와 views 필터]
    H --> I[남은 tables의 컬럼 존재 검사]
    I --> J[후속 catalog 처리]
```

공통 추출은 원본 조회가 끝난 뒤 tables·columns·views를 함께 필터링한다. 여기서 원본 조회 자체의 비용이나 예외를 막아 주는 것은 아니다. PK(Primary Key, 행을 식별하는 기본 키)·FK(Foreign Key, 다른 테이블을 참조하는 외래 키)·query history는 이 `apply()`의 인자가 아니다. 이들의 후속 저장 처리는 수집 chapter에서 별도로 추적한다.

`TableFilter.keep()`의 순서는 다음과 같다.

1. 테이블 이름이 빈 값이면 유지한다. 이 함수는 이름 누락 검증기가 아니다.
2. deny 패턴이 이름에 맞으면 제외한다.
3. allow 패턴이 있는데 이름에 맞지 않으면 제외한다.
4. 나머지는 유지한다.

매칭 대상은 `schema.table` 전체가 아니라 **한정되지 않은 테이블 이름**이다. `re.search()`라 부분 문자열도 맞으며 대소문자를 구분한다. 예를 들어 `stage`는 `orders_stage`를 제외하지만 `orders_STAGE`는 제외하지 않는다. `^orders$`는 정확히 `orders`에만 맞는다. 두 schema에 각각 `orders`가 있으면 이름 패턴만으로 둘을 구분할 수 없다.

설명용 설정 `allow=^fact_`, `deny=_deprecated$`의 결과는 다음과 같다.

| 테이블 이름 | 결과 | 이유 |
| --- | --- | --- |
| `fact_sales` | 유지 | allow 일치, deny 불일치 |
| `fact_sales_deprecated` | 제외 | deny 우선 |
| `dim_date` | 제외 | allow 불일치 |

따라서 필터는 catalog에 들어갈 후보를 줄이는 기능이다. 이 필터만으로 원본 DB의 SQL 권한이나 모든 직접 실행 경로를 제한한다고 해석해서는 안 된다.

근거: [table_filter](../../../code/auto-ontology/auto_ontology/catalog/table_filter.py), [공통 추출](../../../code/auto-ontology/auto_ontology/catalog/extract.py).

## 5. 캐시의 상태·수명과 자원 소유권

```mermaid
stateDiagram-v2
    [*] --> Unloaded
    Unloaded --> Unloaded: 설정 없음 또는 로딩 실패
    Unloaded --> Cached: connector 전체 생성 성공
    Cached --> Cached: get_connectors가 목록 복사본 반환
    Cached --> Unloaded: invalidate가 각 객체 close 후 None 설정
```

| 상태·작업 | 실제 동작과 의미 |
| --- | --- |
| 초기 `_connectors = None` | 미로딩 상태 |
| 설정이 전혀 없음 | 빈 목록을 반환해도 캐시에 `[]`를 저장하지 않음. 다음 호출에서 다시 로딩 |
| 로딩 성공 | 객체 목록을 모듈 전역에 저장. 시간 기반 만료는 이 코드에 없음 |
| 반환 | `list(_connectors)`로 바깥 목록만 복사. 내부 connector는 같은 객체 |
| 무효화 | 저장된 각 객체에 `close()` 시도. 한 객체의 close 예외는 기록하고 다음 객체 처리. 마지막에 `None` |
| 생성 도중 실패 | `_connectors` 할당 전 예외. 앞에서 만든 임시 객체를 일괄 close하는 정리 코드는 해당 루프에 없음 |

목록 복사본에서 항목을 삭제해도 Registry 목록은 바뀌지 않지만, 그 안의 connector를 직접 닫으면 공유 객체에 영향을 줄 수 있다. 공통 계약에서 `run_ingest()`가 빌린 connector를 소유자처럼 닫지 않는 이유와 연결된다.

Registry 모듈에는 로딩·무효화 전체를 감싸는 lock(동시에 한 작업만 수행하도록 하는 잠금)이 없다. **사실:** 현재 코드의 해당 함수에는 상호 배제 장치가 없다. **미검증 시나리오:** 같은 프로세스의 동시 수집·무효화가 공유 객체 사용과 겹치는 경우의 동작은 엔진별 연결 수명과 실행 실험이 필요하다. 실제 장애가 발생했다고 단정하지 않는다.

## 6. 연결을 변경하면 어디까지 갱신되는가

### 6.1 저장과 재수집 조건

| 작업 | 저장·검사 | 이후 작업 |
| --- | --- | --- |
| 연결 테스트 | 저장하지 않음. 정규식 검사 후 URL·객체 생성, `get_schemas()`가 있으면 호출하고 없으면 `ping()` | `finally`에서 임시 객체 close |
| 신규 생성 | `schema` 단축 필드 제거, 정규식·저장 이름 중복 검사. Vault 또는 catalog JSON 저장 | 캐시 3종 갱신 시도 후 수집 요청 |
| 수정 | 기존 DB 이름·type 유지, 빈 secret 필드는 기존 값 보충. 새 설정 저장 | 캐시 갱신. 수집 범위가 달라질 때만 수집 요청 |
| 사용자별 인증 전환 | `sso_federation` 플래그 저장 | 캐시 갱신, 재수집 요청 없음 |
| 삭제 | Vault 사용 시 secret 먼저 삭제, catalog의 connection을 비움 | 캐시 갱신 후 별도 수집 데이터 삭제 요청 |

`_ingest_scope()`는 정렬한 `schemas`와 allow/deny 정규식 값을 비교한다. 따라서 schema 순서만 바꾸는 것은 재수집 조건이 아니지만 테이블 필터 변경은 조건이다. 기존 docstring 일부는 schema만 언급하므로 실제 `_ingest_scope()` 호출을 기준으로 읽어야 한다. 주소·인증 정보만 바꾸는 경우에는 즉시 재수집하지 않는다.

수정은 기존 dict 전체와 새 dict 전체를 일반적으로 병합하는 함수가 아니다. 들어온 설정에 identity와 기존 secret을 보충한다. **일반 필드를 요청에서 생략하면 자동 보존된다고 가정할 수 없다.** 생성·수정 함수 자체는 연결 테스트 함수를 호출하지 않으므로, 저장 성공을 원본 DB 접속 검증 성공과 동일시할 수 없다.

Vault 저장 후 catalog 행을 기록하는 두 작업과 캐시 갱신·HTTP 요청은 하나의 트랜잭션(전부 성공하거나 전부 취소되는 묶음)이 아니다. Vault 성공 뒤 catalog 기록 실패, 또는 저장 성공 뒤 수집 요청 실패 같은 경계가 있다. 삭제 시 catalog 행 자체를 여기서 지우지 않는 것은 연결 해제와 수집 graph·embedding 정리를 분리하기 위해서다.

### 6.2 갱신은 프로세스별로 일어난다

```mermaid
sequenceDiagram
    participant U as 연결 변경 요청
    participant S as API 연결 service
    participant D as catalog 또는 Vault
    participant W as 대기 Chat worker
    participant I as ingestion service
    U->>S: 연결 설정 변경
    S->>D: 설정 저장
    S->>S: 이 프로세스 connector 캐시 무효화
    S->>W: standby 종료와 새 standby 생성 요청
    S->>S: SSO 플래그 캐시 무효화
    alt 생성 또는 수집 범위 변경
        S->>I: HTTP 수집 요청
        I->>I: 배경 thread 시작
        I->>I: 자체 캐시 무효화 후 저장 설정 재조회
        I->>I: 이름이 맞는 connector로 run_ingest
    end
    S-->>U: 설정 처리 결과
    Note over U,I: 응답은 배경 수집 완료를 기다리지 않음
```

`_refresh_connection_caches()`는 connector·Chat worker·SSO 플래그 캐시 갱신을 각각 `try/except`로 실행한다. 하나가 실패해도 다음 갱신과 후속 수집 요청을 진행한다. 이미 저장한 설정을 캐시 예외 때문에 되돌리는 구조는 아니다.

`refresh_chat_workers()`는 WarmPool의 **대기 worker 하나를 분리해 종료하고 새 대기 worker 생성을 요청**한다. 이미 실행 중인 모든 질문 worker를 찾아 교체하지 않는다. worker의 일반 질문 경로는 시작할 때 로딩한 connector 목록을 재사용한다. 시작 목록이 비었으면 질문 직전에 다시 조회하는 복구 경로가 있다.

다른 프로세스인 ingestion service의 `_connectors`는 API 프로세스가 직접 비울 수 없다. 수집 요청을 받은 서비스가 자신의 배경 thread에서 무효화하고 다시 읽는다. 요청 payload의 모든 필드를 그대로 즉석 connector 생성에 쓰는 것이 아니라 DB 이름으로 다시 로딩한 목록에서 대상을 찾는다. 정기 `DataScheduler`도 매 pass 시작에 자체 캐시를 비운다. 기본 간격은 앞 실행 종료 기준 24시간이다.

수집 요청용 HTTP proxy는 전송 실패를 기록하고 예외를 삼킨다. 배경 수집 thread도 예외를 기록한다. 따라서 설정 변경 응답 성공, 수집 요청 전달 성공, 수집 완료 성공은 구분해야 한다. 정기 수집이 나중에 재시도할 기회는 있지만 즉시 성공을 보장하지 않는다. 새 범위 밖의 기존 데이터가 실제로 제거되는지는 후속 수집 diff·삭제 분석에서 확인한다.

근거: [연결 service](../../../code/auto-ontology/auto_ontology/server/connections/service.py), [Chat worker](../../../code/auto-ontology/auto_ontology/server/chat/worker.py), [HTTP proxy](../../../code/auto-ontology/auto_ontology/server/ingestion/proxy.py), [즉시 수집](../../../code/auto-ontology/auto_ontology/ingestion_service/ingest.py), [정기 수집](../../../code/auto-ontology/auto_ontology/ingestion_service/data_scheduler.py).

## 7. 사용자별 인증은 공유 캐시와 어떻게 다른가

SSO(Single Sign-On)는 한 번 로그인한 사용자 신원을 다른 서비스에서도 쓰는 인증 방식이다. `subject_token`은 여기서 로그인 사용자의 신원을 전달하는 토큰이다. PAT(Personal Access Token)는 연결에 저장된 접근 토큰이며, 두 토큰의 사용자를 같은 사람으로 가정할 수 없다.

`get_connectors_for_subject_token()`의 책임은 Databricks의 사용자별 인증 대상만 별도로 만드는 것이다.

1. 저장 연결을 다시 읽는다. 이 조회의 예외는 로그 후 전파한다. 일반 `get_connectors()`의 환경 대체와 다르다.
2. `uses_sso_federation()` 대상이 없으면 공유 `get_connectors()`를 반환한다.
3. 대상이 있는데 subject token이 없으면 예외를 발생시킨다. 저장 PAT로 대신 실행하지 않는 동작을 fail-closed, 즉 필요한 인증이 안 되면 거부하는 방식이라고 한다.
4. 사용자 토큰을 교환하고 `access_token_override`를 넣어 URL·connector를 새로 만든다. schema·table 필터도 전달한다.
5. 새 객체들과, 그 `database_name`에 해당하지 않는 공유 캐시 객체들을 합쳐 반환한다.

이 함수 자체는 새 사용자별 객체를 `_connectors`에 저장하지 않는다. 다만 Chat worker는 `subject_token is not None`일 때 이 함수를 호출하고, 그 외에는 일반 connector를 사용한다. 토큰 없는 요청이 앞단에서 어떻게 거절되는지, 교환 토큰의 캐시·만료·정리까지는 인증 후속 장에서 확인한다. 이 함수 하나로 전체 요청의 인증 보장을 판단하지 않는다.

## 8. 실패 분기와 코드 설명의 차이

| 조건 | 확인한 코드 동작 | 해석·남은 확인 |
| --- | --- | --- |
| 저장 연결 하나의 필수 필드 누락 | URL 목록 생성 전체 실패 → 환경 목록 대체 | 정상 저장 연결만 부분 사용하지 않음 |
| connector 생성 하나 실패 | Registry 호출 예외 전파 | 정기 수집의 개별 `run_ingest` 예외 처리보다 앞 단계 |
| 중복 `database_name` | 경고 후 모두 유지 | 실행 연결의 유일성을 이 함수가 강제하지 않음 |
| 연결 없음 | 미로딩 상태 유지 | 이후 조회·빈 worker 복구 시 다시 읽을 수 있음 |
| connector close 실패 | 로그 후 나머지 close, 캐시 비움 | 실제 드라이버 자원 해제 성공과 캐시 제거는 별개 |
| 캐시 갱신 하나 실패 | 나머지 갱신과 후속 처리 계속 | 부분적으로 예전 설정이 남을 가능성, 실행 검증 없음 |
| 수집 HTTP 요청 실패 | proxy에서 기록하고 반환 | 설정 저장은 유지, 수집 완료 보장 없음 |
| 잘못된 정규식 | 테스트·신규 생성은 거부. Registry는 오류 기록 후 비활성 필터 | 아래 수정 경로 차이 참조 |

**정규식 검사 경로의 차이:** `_table_filter()`의 주석은 API가 저장 시 검증하므로 잘못된 패턴이 오지 않아야 한다고 설명한다. 실제로 `test_connection()`·`create_connection()`은 `from_connection()`을 호출하지만, 현재 `update_connection()` 본문에는 그 호출이 없다. router의 수정 body도 내부 필드를 자유로운 dict로 받는다. 따라서 테스트를 거치지 않고 수정 요청에 잘못된 패턴을 넣으면 저장을 통과하고, 다음 Registry 로딩에서 두 필터 모두 비활성인 `TableFilter()`로 대체될 수 있는 코드 경로가 있다. **이는 코드상 도출한 시나리오이며 실제 요청으로 재현하지 않았다.** 원본 코드는 수정하지 않았다.

또한 `_redact()`는 URL password와 `truststore_data`를 가리는 보조 함수지만 모든 비밀 필드를 완전히 정리하는 일반 도구는 아니다. query parameter 전체를 제거하지 않고, 예외 자체에 원문 URL이 포함되는 분기도 있다. 여기서는 “오류 로그가 항상 안전하게 정리된다”는 보장을 하지 않는다. 상세 인증·로그 경계는 후속 장에서 다룬다.

## 9. 관련 테스트에서 실제로 확인하는 것

아래는 테스트 소스의 assertion을 읽은 결과다. 테스트를 실행했다는 의미는 아니다.

| 테스트 파일·대표 함수 | 확인하는 기대 동작 |
| --- | --- |
| `test_registry_connection_strings.py::test_parse_connection_strings_accepts_commas_and_newlines` | 쉼표·줄바꿈·공백이 섞인 입력을 3개 URL로 분리 |
| `test_table_filter.py::test_deny_wins_over_allow` | allow와 deny가 겹치면 제외 |
| 같은 파일의 `test_patterns_are_unanchored_and_case_sensitive` | 부분 일치와 대소문자 구분 |
| 같은 파일의 `test_invalid_regex_raises_rather_than_being_ignored` | 필터 생성 자체는 잘못된 정규식에 예외 |
| 같은 파일의 `test_create_dataframe_applies_the_connectors_filter` | 추출 결과에서 table과 column을 함께 제외 |
| 같은 파일의 `test_get_connectors_passes_the_filter_to_every_connector` | 가짜 connector factory에 저장된 필터가 전달되는지 검사. 실제 모든 엔진 접속 검증은 아님 |
| `server/connections/tests/test_service.py`의 수정 테스트들 | 빈 secret 보존, schema 변경 시 수집 요청, worker 갱신 실패 후에도 수집 요청, type 변경 거부 |
| 같은 파일의 삭제 테스트들 | catalog 연결 해제·reset 요청, Vault 삭제 → 행 해제 순서 |
| `server/chat/tests/test_worker.py`의 재조회·재사용 테스트 | 부팅 시 빈 목록은 질문 전에 복구, 정상 목록은 재사용 |
| `test_registry_dialects.py` | 등록 클래스가 SQL parser가 아는 dialect를 보고하는지 검사. 연결 문자열의 전체 유효성 검증과 다름 |

근거: [URL 분리 테스트](../../../code/auto-ontology/auto_ontology/connectors/tests/test_registry_connection_strings.py), [필터 테스트](../../../code/auto-ontology/auto_ontology/catalog/tests/test_table_filter.py), [연결 service 테스트](../../../code/auto-ontology/auto_ontology/server/connections/tests/test_service.py), [worker 테스트](../../../code/auto-ontology/auto_ontology/server/chat/tests/test_worker.py), [dialect 테스트](../../../code/auto-ontology/auto_ontology/connectors/tests/test_registry_dialects.py).

## 10. 다음 분석으로 넘기는 질문

- schema 목록을 받은 4개 엔진이 실제 조회에서 어디까지 제한하는가? 다른 엔진의 system schema 제외·권한 부족·view 조회는 어떻게 다른가?
- 엔진별 생성자·execute·close가 연결을 언제 열고 닫는가? Registry 무효화와 실행이 겹칠 때 어떤 영향이 있는가?
- 수집 범위를 좁혔을 때 catalog·PK/FK·SQL 이력·의미 계층·embedding에서 기존 항목이 어떤 순서로 정리되는가?
- 사용자별 인증의 앞단 요청 검사, 토큰 교환·만료·캐시, 사용자별 connector 자원 정리는 어떻게 이어지는가?

다음은 엔진별 메타데이터 추출 분석이다. 엔진을 한 표로만 요약하지 않고 조회 방식·결과 필드·부분 실패를 묶음별 chapter로 나눈다. 범위는 [Connector 계획](../../../.codex/plan/auto-ontology/01-3_connectors.md)에서 이어간다.
