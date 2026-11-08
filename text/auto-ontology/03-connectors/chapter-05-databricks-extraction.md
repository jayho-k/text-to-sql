# Chapter 05. Databricks의 schema별 추출 경로와 부분 실패

Databricks connector는 **수집 schema가 정확히 하나이면 SHOW·DESCRIBE를 사용하고, 여러 개이거나 미지정이면 information_schema를 사용한다.** 단일 schema 경로는 테이블별 구조 조회 결과를 캐시해 컬럼·키를 함께 제공한다. 두 경로는 속도뿐 아니라 nullable·설명·view 정의·실패 처리에서도 차이가 있다.

이 장은 로컬 소스와 테스트의 정적 분석이다. 실제 Databricks·모델·테스트는 호출하지 않았다. [공통 계약](chapter-01-common-contract.md), [Registry](chapter-02-registry-and-cache.md), [용어집](../01-architecture/chapter-00-glossary.md)을 함께 참고한다.

## 1. 이름 공간과 connector의 책임

Databricks에서 catalog는 `main.sales.orders`의 `main`처럼 schema들을 묶는 상위 이름 공간이다. 이 프로젝트가 메타데이터를 보관하는 **catalog 저장소**와 같은 단어지만 다른 대상이다. 이 장에서는 원본 catalog와 저장소를 구분한다. schema는 `sales`, 테이블은 `orders`다.

SQL warehouse는 Databricks에서 SQL을 처리하는 실행 자원이다. 연결 URL의 host와 `http_path`가 접근 지점을 지정하며, URL 경로의 catalog가 connector의 `database_name`이 된다.

```text
설명용 URL:
databricks://token:EXAMPLE_TOKEN@example.databricks.com/main?http_path=EXAMPLE_PATH

connector.database_name = main
qualify("sales", "orders") = `main`.`sales`.`orders`
```

`qualify()`는 SQL에 쓸 테이블 전체 이름을 만든다. 각 이름의 backtick을 이스케이프하고 catalog·schema·table 세 부분을 포함한다. schema가 없으면 모호한 두 부분 이름을 만들지 않고 `ValueError`를 발생시킨다.

생성자는 URL을 파싱해 host·token·catalog·http_path를 검사하지만 **접속 쿼리를 실행하지 않는다.** 별도 `ping()`이 `SELECT current_catalog()`를 수행한다. Registry에서 객체가 생성되었다는 사실만으로 원본 접속 검증을 마쳤다고 할 수 없다.

근거: [databricks.py의 URL parser·생성자·qualify·ping](../../../code/auto-ontology/auto_ontology/connectors/databricks.py).

## 2. schema 개수로 조회 경로를 선택한다

allowlist는 수집을 허용한 이름 목록이다. 생성자는 전달된 `schemas`로 두 값을 보관한다.

| 값 | 용도 |
| --- | --- |
| `_schema_names` | 공백 제거·중복 제거·정렬한 원래 대소문자 이름 목록. SQL 생성과 단일 schema 판단 |
| `_schema_filter` | casefold한 이름 집합. 반환된 표를 대소문자 구분 없이 걸러 내는 보조 검사 |

casefold는 이름 비교를 위해 대소문자를 정규화하는 연산이다. 일반 Registry 경로는 그 전에 schema 입력 공백을 정리한다. 이 두 내부 값은 별도 구성되므로 직접 생성자에 주는 비정상 입력까지 같은 결과라고 일반화하지 않는다.

```mermaid
flowchart TD
    A[메타데이터 함수 호출] --> B{정리된 schema 이름이 정확히 하나인가}
    B -->|예| C[단일 schema 경로]
    C --> D[SHOW TABLES와 SHOW VIEWS]
    D --> E[대상별 DESCRIBE TABLE EXTENDED]
    E --> F[컬럼과 PK와 FK 캐시]
    B -->|아니오| G[information_schema 경로]
    G --> H{allowlist가 있는가}
    H -->|여러 개| I[SQL WHERE에 schema IN 조건]
    H -->|없음| J[tables와 columns와 views에서 information_schema 제외]
    I --> K[조회 결과에 schema 보조 필터]
    J --> K
```

이것은 **설정에 따른 경로 선택**이다. 한 경로에서 오류가 나면 다른 경로로 자동 재시도하는 fallback, 즉 실패 시 대체 경로는 이 분기에 없다.

단일 schema라는 조건은 `_schema_names` 길이로 판단한다. 예를 들어 원래 철자가 다른 `Sales`, `sales`를 두 이름으로 남겼다면 casefold 집합은 하나가 되어도 경로 판단용 목록은 둘일 수 있다. 일반 입력은 실제 schema 목록에서 고른 이름이지만 이 구분은 코드에 존재한다.

## 3. 단일 schema: get_tables가 컬럼·키까지 먼저 읽는다

### 3.1 단순 목록 조회로 끝나지 않는 이유

공통 추출기는 tables를 먼저 받고 columns를 다음에 받는다. `get_tables()`가 읽을 수 없는 테이블까지 반환한 뒤 columns에서만 제외하면, 공통 coverage 검사에서 “테이블은 있는데 컬럼이 없음”으로 전체 추출이 실패한다. coverage는 나열된 테이블마다 컬럼이 있는지 확인하는 검사다.

단일 schema 경로는 다음 순서로 이를 처리한다.

1. `get_tables()`가 실행 단위의 내부 캐시·성공 대상 집합을 초기화한다.
2. `_tables_via_show()`가 `SHOW TABLES IN catalog.schema`와 `SHOW VIEWS IN catalog.schema`를 실행한다.
3. view 이름 집합을 이용해 tables 표에 `view` 또는 `base table`을 붙인다.
4. 정리된 목록을 `_show_tables_cache`에 보관한다. 변수 주석의 raw라는 표현과 달리 실제 할당값은 `_tables_frame()`을 거친 공통 필드 표다.
5. `_describe_pass()`가 대상별 `DESCRIBE TABLE EXTENDED`로 컬럼·선언 키를 읽는다.
6. 컬럼을 확보한 `(schema, table)`만 `_described_relations`에 넣는다.
7. `_with_columns()`가 성공 집합에 속한 테이블만 반환한다.

```mermaid
sequenceDiagram
    participant E as 공통 추출기
    participant C as Databricks connector
    participant D as SQL warehouse
    E->>C: get_tables()
    C->>C: describe와 목록 캐시 초기화
    C->>D: SHOW TABLES, SHOW VIEWS
    loop 목록의 테이블과 view
        C->>D: DESCRIBE TABLE EXTENDED
        C->>C: 컬럼과 키 수집, 성공 대상 기록
    end
    C-->>E: 컬럼을 확보한 대상의 tables
    E->>C: get_columns()
    C-->>E: 캐시의 columns
    E->>C: get_views()
    C->>D: SHOW VIEWS 재조회
    C-->>E: 성공 대상에 속한 views
    E->>C: get_queries(), get_pks(), get_fks()
    C-->>E: 빈 queries, 캐시의 PK와 FK
```

조회 대상에 view도 포함된다. 단일 경로의 분류는 SHOW VIEWS 이름 집합에 있으면 `view`, 나머지는 `base table`이다. 이 분류에는 materialized view를 별도 타입으로 만드는 조건이 없다. 여러 schema 경로의 분류와 다르다.

### 3.2 컬럼 행과 메타데이터 구간을 분리한다

DESCRIBE EXTENDED 결과는 컬럼 행 뒤에 추가 메타데이터 구간이 붙는 형식으로 처리한다. `_describe_columns_only()`는 `col_name`이 빈 행 또는 `#`로 시작하는 첫 행 앞까지만 컬럼으로 사용한다.

| 입력·판단 | 반환 처리 |
| --- | --- |
| `col_name` | `column_name`으로 변환 |
| `data_type` | `data_type`으로 유지. 해당 필드가 없으면 결측값 |
| 컬럼 행 순서 | 1부터 연속 `ordinal_position` 생성 |
| `comment`가 있음 | `description`으로 전달 |
| nullable | 이 경로에서는 반환하지 않음 |
| schema 이름 | allowlist 철자 대신 SHOW TABLES가 보고한 행의 schema 사용 |

nullable은 NULL, 즉 값 없음의 허용 여부다. 단일 schema 경로에는 그 정보가 없으므로 `normalize_columns()`가 결측값으로 채운다. **결측은 nullable이 False라는 판정이 아니다.** 여러 schema 경로는 SQL에서 boolean을 직접 반환하므로 같은 테이블도 경로에 따라 확보되는 정보가 다를 수 있다.

schema 철자를 조회 결과에 맞추는 것은 tables와 columns의 연결 키를 동일하게 유지하기 위해서다. 테스트는 설정 `Sales`에 대해 원본이 `sales`를 보고해도 양쪽 결과가 같은 `(sales, orders)`를 갖도록 검사한다.

### 3.3 PK·FK는 Constraints 구간을 정규식으로 읽는다

PK(Primary Key)는 행 식별에 쓰는 기본 키, FK(Foreign Key)는 다른 테이블을 참조하는 외래 키다. 여러 컬럼을 함께 쓰는 복합 키도 처리한다.

`_describe_constraints()`는 이름이 `# Constraints`인 행을 대소문자 구분 없이 찾는다. 이후 빈 이름이나 다음 `#` 구간 전까지 `(제약조건 이름, 정의)`를 모은다. `_collect_constraint()`는 정의 문자열을 정규식으로 해석한다.

```text
설명용 정의:
PRIMARY KEY (`tenant_id`, `order_id`)
FOREIGN KEY (`tenant_id`, `customer_id`)
  REFERENCES `main`.`sales`.`customers` (`tenant_id`, `id`)

PK 결과: tenant_id 순번 1, order_id 순번 2
FK 결과: tenant_id → tenant_id, customer_id → id
```

| 로직 | 의미·한계 |
| --- | --- |
| PK 컬럼 목록을 1부터 나열 | 복합 PK 내부 순서 유지 |
| FK의 원본·참조 목록을 위치로 대응 | 두 집합의 모든 조합을 만들지 않음 |
| 참조 컬럼이 원본보다 적음 | 남은 참조 컬럼을 빈 문자열로 기록. 길이 불일치 예외 없음 |
| 참조가 table 이름뿐임 | 현재 schema로 보충 |
| `catalog.schema.table` 참조 | `_split_qualified()`가 마지막 두 부분만 반환. 참조 catalog는 결과에서 소실 |
| 정규식에 맞지 않는 정의 | 키 행을 추가하지 않음. 전체 추출을 실패시키지 않음 |

정규식은 전체 SQL 문법 parser가 아니다. 컬럼 목록은 쉼표로, 한정 이름은 점으로 단순 분리하고 backtick을 벗긴다. 이름 자체에 쉼표·점·공백·복잡한 인용이 포함되는 경우의 완전한 파싱은 보장하지 않는다. 이 장에서는 일반적인 테스트 정의에 대한 처리와 특수 식별자의 미검증 범위를 구분한다.

키 결과는 constraint 이름이나 참조 catalog를 반환하지 않는다. 그래서 선언된 관계의 모든 정보를 그대로 보존하는 교환 형식으로 볼 수 없다.

## 4. 읽지 못한 테이블과 전체 scope 권한 오류를 나눈다

scope는 여기서 catalog 또는 schema 전체처럼 권한이 적용되는 범위다. `_describe_pass()`는 Databricks SQL 라이브러리의 `Error`를 다음처럼 처리한다.

```mermaid
flowchart TD
    A[대상별 DESCRIBE] --> B{결과}
    B -->|컬럼 있음| C[컬럼과 키 수집, 성공 집합에 추가]
    B -->|컬럼 없음| D[경고 후 해당 대상 제외]
    B -->|Databricks Error| E{scope 권한 오류 패턴인가}
    E -->|예| F[즉시 예외 전파, 나머지 대상 조회 중단]
    E -->|아니오| D
    B -->|그 밖의 예외| F
    C --> G[다음 대상]
    D --> G
```

scope 오류 판별은 오류 타입의 세부 코드만 보는 방식이 아니라 **오류 메시지 정규식**이다. `PERMISSION_DENIED` 또는 `INSUFFICIENT_PERMISSIONS` 이후에 `USE CATALOG`, `USE SCHEMA`, `does not have USE` 같은 문구가 있는지 검사한다.

따라서 다음을 구분해야 한다.

- 개별 테이블 삭제·좁은 권한 등 일반 `Error`는 경고 후 제외한다.
- 위 메시지 패턴에 맞는 전체 scope 권한 오류는 실패로 전파한다.
- 모든 `Error`가 자동으로 테이블 단위 오류로 정확히 분류된다는 보장은 없다. 메시지 형식에 의존한다.
- 모든 대상이 일반 오류로 제외되어도 “성공한 대상이 0개이므로 실패”라는 추가 임계조건은 이 루프에 없다. 빈 표가 반환될 수 있다.

마지막 항목이 기존 catalog의 삭제·보존에 어떤 영향을 주는지는 후속 수집 diff 분석에서 확인한다. 이 장에서는 실제 데이터 손실을 재현했다고 말하지 않는다.

단일 schema의 `get_views()`도 describe 성공 집합으로 걸러 같은 실패 대상이 다시 들어오지 않게 한다. 다만 **`get_views()`를 먼저 단독 호출해 아직 describe cache가 없으면 이 필터를 생략**한다. 함수 호출 순서가 결과 범위에 영향을 줄 수 있다.

## 5. 메타데이터 캐시는 언제 새로 만들어지는가

```mermaid
stateDiagram-v2
    [*] --> Empty
    Empty --> Described: columns 또는 keys 조회가 describe pass 수행
    Empty --> Described: 단일 schema get_tables가 목록과 describe 수행
    Described --> Described: columns와 PK와 FK 재사용
    Described --> Empty: get_tables 호출 시 초기화
```

| 내부 값 | 내용·수명 |
| --- | --- |
| `_show_tables_cache` | get_tables가 만든 정리된 목록. describe에서 목록 재조회를 피함 |
| `_describe_cache` | `(columns, pks, fks)` 세 표. 한 번의 describe pass 결과 |
| `_described_relations` | 컬럼을 확보한 schema·table 쌍. tables·views 필터 기준 |

여기서 캐시는 Registry의 connector 목록 캐시와 별개다. **같은 connector 내부의 수집용 결과 캐시**이며 `get_tables()`가 초기화 지점이다. 따라서 get_columns·get_pks·get_fks만 반복 호출하면 시간이 지났다는 이유로 새로 읽지 않는다. 공통 추출 순서가 get_tables부터 시작한다는 전제와 연결된다.

대상 개수가 N개로 일정하고 오류·세션 재시도가 없으면, 공통 추출의 단일 schema 경로는 SHOW TABLES 1회·SHOW VIEWS 2회·DESCRIBE N회로 `N + 3`개 SQL을 수행한다. PK·FK는 describe cache를 사용하고 queries는 DB를 조회하지 않는다. 초기 접속·다른 계층의 쿼리·재연결은 이 계산에서 제외한다.

## 6. 여러 schema·미지정 경로: information_schema 조회

이 경로는 원본 catalog의 `information_schema`를 SQL로 읽는다. 각 메서드는 조회 후 `_filter_by_schema()`도 적용한다.

| 반환 표 | SQL·필드 처리 |
| --- | --- |
| tables | schema·name·type. `VIEW → view`, `MATERIALIZED_VIEW → materialized view`, 나머지는 base table |
| columns | schema·name·column, `full_data_type AS data_type`, `is_nullable = 'YES'`, ordinal |
| views | schema·name·view_definition |
| pks | key_column_usage와 table_constraints를 constraint catalog·schema·name으로 join, PK 조건 |
| fks | 위 메타데이터와 referential_constraints·참조 key_column_usage를 join, FK 조건 |

`full_data_type`은 원본이 제공하는 전체 타입 표기를 쓰기 위한 선택이다. 단일 schema 경로처럼 comment를 description으로 선택하는 필드는 이 쿼리에 없다. 결과적으로 한 경로는 description을 확보할 수 있고 다른 경로는 nullable·view 정의를 확보한다는 차이가 있다.

FK SQL은 `foreign_keys.position_in_unique_constraint = referenced_keys.ordinal_position`을 join 조건에 포함한다. 복합 키의 원본 컬럼을 참조 키 위치에 맞춰 연결하려는 조건이며, [Postgres 쿼리의 대응 조건 누락](chapter-03-postgres-and-mysql-extraction.md)과 다른 구현이다. 다만 최종 반환 필드는 참조 schema·table·column까지이고 참조 catalog는 반환하지 않는다.

### 6.1 schema 필터는 SQL과 Python 양쪽에 있다

- schema가 여러 개면 `table_schema IN ('a', 'b')`처럼 SQL에 조건을 넣는다. 이름 안의 작은따옴표는 두 개로 이스케이프한다.
- 미지정이면 tables·columns·views에서 `table_schema != 'information_schema'`를 사용한다.
- PK·FK의 `_schema_predicate()`는 allowlist가 있을 때만 `AND ...`를 추가한다. 미지정 시 별도 schema 제외 조건이 없다.
- 반환 후 Python에서는 schema 이름을 casefold해 allowlist와 비교한다.

SQL 조건에 `lower(table_schema)`를 씌우지 않는 것은 메타데이터 조회 범위를 서버에서 줄이려는 구현 의도다. 코드 주석의 과거 측정치를 이번 환경의 성능 보장으로 사용하지 않는다.

클라이언트의 대소문자 무시 필터는 **이미 반환된 행만** 처리한다. SQL의 원래 철자 조건으로 행이 빠졌다면 그 필터가 다시 가져오지는 못한다. 단일 schema 경로의 SHOW가 보고한 철자를 따르는 처리와도 구분한다.

### 6.2 단일 schema 경로와 실패 정책도 다르다

information_schema 경로에는 테이블별 DESCRIBE와 성공 집합 필터가 없다. 각 일괄 SQL이 실패하면 메서드 예외가 전파된다. 조회 성공 뒤 tables에 있는데 columns에 없는 대상은 공통 coverage 검사가 잡는다. 모든 컬럼·키의 완전성을 검사하는 것은 아니다.

schema를 하나 더 선택하는 변경은 단순히 같은 루프의 반복 횟수만 늘리는 것이 아니라 **조회 전략·필드·실패 정책을 바꾼다.** 두 설정의 결과가 완전히 같아야 한다고 가정해서는 안 된다.

## 7. view 정의와 SQL 이력의 명시적 미수집

단일 schema의 SHOW VIEWS 경로는 `view_definition = pd.NA`를 넣는다. view SQL을 다시 얻기 위한 `SHOW CREATE TABLE`을 추가 호출하지 않는다. 여러 schema 경로의 information_schema.views는 정의 필드를 선택한다.

`get_queries(hours=24)`는 어느 경로에서도 DB를 조회하지 않고 `end_time`, `query_text`가 있는 빈 표를 반환한다. 주석은 workspace 전체 이력 스캔의 비용을 피하려는 선택이라고 설명한다. 이는 **현재 connector의 비활성 기능**이며 원본 Databricks가 SQL 이력을 전혀 제공하지 않는다는 뜻이 아니다. hours를 바꿔도 결과 수집이 활성화되지 않는다.

## 8. 공유 연결·재시도와 추출의 경계

`ingestion_service/ingest.py::run_ingest()`는 `reuse_connection()` 훅이 있으면 `ingest_catalog()`를 그 안에서 실행한다. Databricks는 이 훅으로 `_shared_connection`을 열어 메타데이터 SQL에서 재사용한다. 블록이 끝나면 연결을 닫고 참조를 비운다. 같은 훅을 중첩 호출하면 바깥쪽이 소유한다.

직접 get_tables 등을 호출해 이 훅을 사용하지 않으면 목록 조회의 `execute()`는 작업별 연결을 사용한다. `_describe_pass()`의 테이블 루프 자체는 하나의 `_connect()` 블록 안에서 실행한다. “모든 호출이 항상 한 연결”이라고 일반화하지 않는다.

`execute()`는 공유 세션이 사라졌다고 `is_session_lost()`가 판단한 오류에 한해 재연결 후 `_run()`을 한 번 다시 실행한다. 임의의 SQL 오류를 무조건 재시도하지 않는다. 다만 **describe 루프는 execute가 아니라 `_run()`을 직접 호출하므로 그 재연결 분기를 통과하지 않는다.** 이 차이를 세션 복구 보장으로 확대하지 않는다.

메타데이터 호출에는 `timeout_s`를 주지 않는다. 명시적으로 제한을 주는 다른 SQL은 별도 세션을 열어 session configuration에 timeout을 설정하며, 접속·warehouse scheduling까지 그 제한으로 모두 묶이는 것은 아니다. 상세 오류·취소·자원 수명은 후속 실행 chapter에서 분석한다.

근거: [run_ingest의 공유 연결](../../../code/auto-ontology/auto_ontology/ingestion_service/ingest.py), [catalog 진입점](../../../code/auto-ontology/auto_ontology/catalog/ingest.py), [connector 실행·describe 구현](../../../code/auto-ontology/auto_ontology/connectors/databricks.py).

## 9. 테스트 근거와 아직 확인하지 않은 경우

| 테스트 함수 | 읽은 assertion |
| --- | --- |
| `test_single_schema_lists_tables_with_show_tables` | SHOW 두 종류 후 대상별 DESCRIBE, view 타입 구분, information_schema 미사용 |
| `test_single_schema_describes_each_table_on_one_connection` | describe pass의 연결 한 번, 추가 구간 제외, 타입·순번·설명 유지, nullable 필드 없음 |
| `test_multiple_schemas_still_use_information_schema` | 여러 schema의 tables·columns가 information_schema·ORDER BY 사용, LIMIT 없음 |
| `test_show_columns_skips_a_table_it_cannot_read` | 읽지 못한 대상을 tables·columns 양쪽에서 제외 |
| `test_described_columns_use_the_schema_name_the_warehouse_reports` | 설정 철자가 달라도 보고된 schema로 tables·columns 키 일치 |
| `test_schema_scope_permission_denial_aborts_after_first_table` | USE CATALOG 오류 후 두 번째 대상 조회 없이 예외 |
| `test_primary_key_is_read_from_the_describe_constraints_section`, FK 대응 테스트 | 정규식 결과의 필드·참조 대상 검사 |
| `test_composite_keys_pair_columns_positionally` | a·b를 x·y에 순서대로 연결 |
| `test_describe_pass_runs_once_for_columns_pks_and_fks` | 세 함수가 같은 describe 결과 사용 |
| `test_get_tables_resets_the_describe_cache` | 새 tables 조회 시 캐시 초기화 |
| `test_get_queries_returns_empty_without_querying` | DB 호출 없이 필드 있는 빈 이력 |
| `test_single_schema_lists_views_with_show_views` | view 목록·결측 definition 검사 |

이 테스트들은 주로 가짜 실행·연결을 넣어 SQL과 결과 변환을 검사한다. 실제 Databricks end-to-end 테스트는 명시적 활성화와 접속 설정이 필요하고 미설정이면 skip한다. 이번에는 어느 테스트도 실행하지 않았다.

추가 검증이 필요한 코드 경계는 다음과 같다.

- SHOW 결과에 `database` 또는 `namespace`가 없는 비정상 형태: 현재 fallback은 `frame.get(..., schema).astype(str)`이므로 대체 문자열에 `.astype()`를 호출할 수 있다. 주석만으로 누락 필드 복구를 보장하지 않는다.
- DESCRIBE 형식·구간 marker 변경, 특수 인용 이름, 원본/참조 컬럼 수 불일치, 교차 catalog FK의 식별 정보 소실.
- scope 오류의 다른 메시지 표현·일반 오류로 전 대상 제외·describe 중 공유 세션 소실.
- 동시에 같은 connector로 다른 추출이 진행되는 경우의 내부 캐시·공유 연결 상태. 해당 상태에 추출 단위 lock은 없다.
- 모든 대상이 제외된 결과를 저장할 때 기존 catalog·의미 계층·embedding이 유지되는지 또는 정리되는지. 수집 diff 분석으로 인계한다.

근거: [Databricks 테스트](../../../code/auto-ontology/auto_ontology/connectors/tests/test_databricks.py), [공통 정규화](../../../code/auto-ontology/auto_ontology/catalog/normalize.py).

다음은 ClickHouse의 HTTP·system 메타데이터·키 의미·SQL 이력이다. Snowflake는 사용자 요청으로 상세 분석에서 제외했다. [남은 엔진 추출 계획](../../../.codex/plan/auto-ontology/01-3-3_remaining-engine-extraction.md)에서 이어간다.
