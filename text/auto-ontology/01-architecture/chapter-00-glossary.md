# Chapter 00. 아키텍처 문서의 용어와 예시

이 문서는 Auto-Ontology의 고유 개념과 일반 기술 용어를 구분해 설명한다. 각 chapter에서도 처음 등장할 때 필요한 뜻을 설명하며, 이 문서는 다시 찾아보기 위한 보조 자료다. 코드 식별자는 원문 표기를 유지한다.

- 작성일: 2026-11-07
- 근거: 제공된 로컬 코드. 일반 용어는 기초 설명이며, 프로젝트에서의 쓰임은 아래 코드 링크로 연결했다.
- 예시는 이해를 돕기 위한 가상 데이터다. 실제 실행·LLM 출력·탐지 성공을 의미하지 않는다.

## 1. 이 프로젝트가 만드는 데이터의 의미

| 용어 | 쉬운 뜻 | 이 프로젝트에서의 쓰임·예시 |
| --- | --- | --- |
| Text-to-SQL | 사람의 질문을 데이터베이스 조회문인 SQL로 바꾸는 작업 | “이번 달 매출은?”을 집계 SQL로 만들고 실행·검증한다. |
| Ontology, 온톨로지 | 개념과 그 사이 관계를 정리한 모델 | Customer·Order 같은 업무 개념과 속성·연결 관계를 표현한다. 여기서는 Postgres에 저장하며 별도 그래프 DB를 뜻하지 않는다. |
| Semantic layer, 의미 계층 | 데이터의 물리적 이름에 업무 의미를 연결한 정의 모음 | `amount`가 무엇을 뜻하는지, 매출을 어떻게 계산하는지 질문 처리에 제공한다. |
| Metadata, 메타데이터 | 실제 값 자체보다 데이터의 구조·설명을 나타내는 정보 | 테이블명·컬럼명·자료형·설명·키 정보. `email`이라는 컬럼명과 실제 이메일 주소 값은 구분한다. |
| Catalog, 데이터 카탈로그 | 연결된 DB의 구조를 모아 둔 내부 목록 | 어느 DB의 어느 schema에 어떤 테이블·컬럼이 있는지 기록한다. |
| Term | 코드에서 관리하는 **업무 개념 객체** | `Customer`라는 Term에 설명·동의어와 연결된 속성을 둔다. 일반적인 ‘단어’보다 구체적인 저장 객체다. |
| ColumnAttribute | 실제 컬럼에 업무 의미를 붙인 **의미 속성 객체** | 물리 컬럼 `customers.email`을 Customer의 ‘이메일’ 속성으로 연결한다. 컬럼 자체와 같은 객체가 아니다. |
| SqlAttribute | Term에 연결하는 **재사용 SQL 표현 객체** | 집계나 파생 계산식을 저장해 질문마다 계산 의미가 달라지는 문제를 줄인다. 실제 SQL 형태는 해당 정의에 달려 있다. |
| CustomAnalysis | 사용자가 관리하는 분석 SQL 정의 | 전체 분석 SQL을 재사용 문맥으로 제공한다. SqlAttribute와 저장·조회 경로가 다르다. |
| PqlAnalysis | 예측 경로에서 관리하는 PQL 분석 정의 | 일반 SQL 검색 후보와 구분해 예측용 예시 등에 사용한다. |
| Semantic compilation, 의미 계층 컴파일 | catalog와 값의 특징 등을 분석해 업무 정의·관계를 구성하는 처리 | 프로그래밍 언어를 기계어로 바꾸는 컴파일이 아니라, 이 프로젝트의 정의 생성 파이프라인 이름이다. |
| Certified | 사람이 해당 정의를 검토·인증했다는 상태 표기 | 실제 데이터나 모든 답변의 정확성을 자동 보증하는 말은 아니다. |
| Edited | 사람이 수정한 내용임을 나타내는 필드 표기 | 재생성 시 보존 정책과 관련된다. 정확한 필드별 처리는 후속 데이터 모델 분석에서 확인한다. |

근거: [schema의 실제 객체](../../../code/auto-ontology/auto_ontology/dal/schema.py), [의미 객체 label·source](../../../code/auto-ontology/auto_ontology/semantic/constants.py), [컴파일 처리](../../../code/auto-ontology/auto_ontology/semantic/compile.py)

### 하나의 컬럼을 여러 관점에서 보기

가상 테이블 `customers(id, email)`이 있다고 하자.

- `customers.email`: 원본 DB에 있는 물리 컬럼이다.
- Catalog column: 그 컬럼의 이름·자료형·설명을 앱 안에 기록한 객체다.
- `Customer`: 해당 데이터를 해석할 업무 개념인 Term의 예시다.
- `이메일`: 원본 컬럼과 업무 개념을 연결할 ColumnAttribute의 예시다.
- `PII` 태그: 해당 컬럼을 개인 식별 정보와 관련 있다고 분류할 때 붙이는 표식이다.
- Embedding: 이런 구조·의미 설명을 관련 질문으로 검색할 수 있게 만든 숫자 표현이다.

즉 컬럼, 의미 속성, 태그, 검색용 vector는 같은 데이터를 둘러싼 서로 다른 표현이다.

## 2. PII는 무엇이고, 여기서는 무엇을 하는가

**PII(Personally Identifiable Information)는 개인을 식별할 수 있는 정보**를 뜻한다. 이메일 주소, 전화번호, 사람 이름 등을 예로 들 수 있다. 이 프로젝트에서는 해당 정보와 관련된 컬럼을 분류하는 기능 이름으로 등장한다.

이 프로젝트의 확인된 처리는 다음과 같다.

1. 분류 입력 `ColumnInput`에 **컬럼명·테이블명·설명**을 담는다. 이 입력 모델에는 실제 행의 샘플 값이 없다.
2. 분류 결과를 `pii`(PII로 판단), `not_pii`(PII가 아니라고 판단), `review`(검토 필요)로 구분한다.
3. `PiiDecision`은 분류·신뢰도·이유·판단 출처를 갖는다. 자동 태그 조건은 PII 판단과 신뢰도 기준을 함께 확인한다.
4. tagging service는 자동 태그 기준과 fallback 여부 등을 확인해 내부 catalog 컬럼에 `PII` 태그를 연결하고 처리 여부를 기록한다. 기본 신뢰도 기준은 `0.9`다.

예를 들어 `email` 컬럼을 PII로 분류하고 신뢰도 조건을 만족하면 내부 catalog에 태그를 붙일 수 있다. **이 태그 부착은 원본 이메일 값을 `***`로 바꾸는 마스킹·삭제 처리가 아니다.** 또한 위 입력 모델에 샘플 값이 없다는 사실을 프로젝트의 모든 기능이 원본 값을 조회하지 않는다는 뜻으로 확대하면 안 된다. 의미 계층 profiling은 별도 경로다.

| 함께 나오는 표현 | 뜻 |
| --- | --- |
| PII detection | 개인 식별 정보 관련 컬럼인지 분류하는 처리 |
| Tag / tagging | 객체에 분류 표식을 연결하는 작업. 예: 컬럼에 `PII` 태그 연결 |
| PII propagation | 관련 원본 컬럼의 태그를 의미 속성 등 연결된 대상에 반영하는 처리 |
| `pii_processed` | 해당 컬럼의 분류 처리를 수행했는지 나타내는 저장 표식. ‘PII임’과 다른 값 |
| confidence / threshold | 판단 신뢰도 / 자동 처리 기준값. 신뢰도 수치를 실제 정확도 측정값과 동일시하지 않는다. |

근거: [ColumnInput·PiiDecision·PiiStatus](../../../code/auto-ontology/auto_ontology/pii_detection/models.py), [detect_and_tag_pii·_apply_batch](../../../code/auto-ontology/auto_ontology/pii_detection/service.py), [태그 전파](../../../code/auto-ontology/auto_ontology/ingestion_service/pii.py)

## 3. 테이블 구조·관계를 설명하는 용어

| 용어 | 쉬운 뜻 | 예시·문서에서 읽는 방법 |
| --- | --- | --- |
| Schema | DB 안에서 테이블들을 나누는 이름 공간, 또는 문맥에 따라 데이터 구조 정의 | `public.orders`의 `public`은 이름 공간. `dal/schema.py`는 저장 구조를 정의하는 코드다. |
| PK, Primary Key, 기본 키 | 테이블의 행을 구별하는 키 | `customers.id`. 한 개 또는 여러 컬럼으로 구성할 수 있다. |
| FK, Foreign Key, 외래 키 | 다른 행을 참조하는 컬럼 관계 | `orders.customer_id → customers.id`. 선언된 FK는 DB 메타데이터에서 읽는다. |
| Semantic FK | 프로젝트가 의미 계층에서 표현하는 참조 관계 | 단순히 DB에 선언된 FK 목록과 같지 않다. 관계 추론·해석 결과를 포함하는 별도 경로다. |
| Join / join path | 여러 테이블을 잇는 SQL 연산 / 연결 경로 | 고객의 주문 금액을 계산하려면 customers에서 orders까지 어떤 키로 연결할지 알아야 한다. |
| Junction / bridge table | 다른 두 대상을 연결하는 중간 테이블 | `order_items(order_id, product_id, quantity)` 같은 주문·상품 연결. 코드의 순수 FK bridge와 payload 있는 junction 판단은 구분한다. |
| Payload-bearing junction | 연결 키뿐 아니라 별도 값도 가진 연결 테이블 | 위 예시의 `quantity`처럼 관계에 수량·가격 등이 붙는다. 여기서 payload는 HTTP 요청 본문이라는 뜻이 아니다. |
| Cardinality | 관계에 연결되는 개수 또는 값 종류 수 | 관계의 1:N과 `DISTINCT` 값 개수는 같은 단어를 다른 관점으로 쓰는 경우다. |
| Schema-qualified name | 소속 schema까지 포함한 이름 | `sales.orders`. 같은 테이블명이 여러 schema에 있을 때 구분한다. |
| Unique / cascade | 중복 금지 제약 / 연결된 데이터에 변경·삭제를 연쇄 적용하는 규칙 | 실제 적용 범위는 schema의 제약·외래 키 정의로 확인한다. |

근거: [관계형 schema](../../../code/auto-ontology/auto_ontology/dal/schema.py), [FK·junction 판단](../../../code/auto-ontology/auto_ontology/semantic/visit_enter.py), [bridge 처리](../../../code/auto-ontology/auto_ontology/semantic/bridge_tables.py)

## 4. 수집·저장 처리 용어

| 용어 | 쉬운 뜻 | 이 프로젝트에서의 맥락 |
| --- | --- | --- |
| Ingestion, 수집 | 원본 구조를 읽어 내부 catalog와 검색 자료로 반영하는 처리 | 원본 테이블의 모든 행을 복제한다는 의미는 아니다. |
| Connector | DB 종류별 접속·메타데이터 조회·SQL 실행을 담당하는 코드 | 서로 다른 DB를 공통 `SQLDatabase` 계약으로 다룬다. |
| Scheduler / trigger / pass | 반복 실행 관리자 / 실행 요청 / 대상들을 한 차례 처리하는 작업 | 요청이 수락됐거나 pass가 끝났어도 모든 연결의 성공을 뜻하지 않는다. |
| Profiling / sampling | 데이터의 특징을 조사하는 처리 / 일부 값을 뽑아 보는 작업 | 값 예시·유일성·날짜 형식 등을 알아내 의미 생성에 사용한다. |
| DISTINCT probe | 서로 다른 값들을 제한적으로 조회해 확인하는 작업 | 무슨 값이 있는지 확인하는 조회. 일반 row sampling과 별도 설정이다. |
| Diff / normalize | 이전 상태와의 차이 계산 / 형식을 일관되게 맞춤 | schema·테이블·컬럼 변경을 반영하기 전에 이름·필드 등을 맞춘다. |
| Upsert | 있으면 갱신하고 없으면 추가하는 저장 방식 | 어떤 필드를 덮어쓰거나 보존하는지는 각 함수의 조건에 달려 있다. |
| DataFrame | pandas에서 행·열로 데이터를 다루는 표 형태 객체 | `tables_df`, `columns_df`. 원본 DB 테이블 그 자체가 아니라 Python 메모리의 처리 데이터다. |
| Chunk / batch | 큰 작업을 나눠 처리하는 묶음 | embedding을 묶음별로 요청하고 성공한 chunk부터 기록한다. |
| DAL, Data Access Layer | 저장소 읽기·쓰기를 모아 둔 계층 | `dal/`에서 SQLAlchemy Core로 내부 Postgres에 접근한다. |
| Transaction / commit / rollback | 함께 성공·실패하도록 묶은 저장 단위 / 확정 / 되돌림 | 일부 FK 변경을 묶는 것과 전체 수집을 한 번에 묶는 것은 다르다. |
| Atomic, 원자적 | 변경이 전부 반영되거나 전혀 반영되지 않는 성질 | catalog 저장과 vector 기록의 전체 교체를 이 성질로 가정하면 안 된다. |
| Cache / pool | 재사용하려고 보관한 결과·객체 / 재사용할 자원 묶음 | connector cache, DB connection pool, worker pool은 각각 보관 대상이 다르다. |
| Best-effort / fallback | 실패를 허용하고 가능한 만큼 진행 / 실패·누락 시 대체 경로 | 실패를 무시해도 결과가 정확하다는 뜻은 아니다. |

근거: [수집 구현](../../../code/auto-ontology/auto_ontology/ingestion_service/ingest.py), [catalog writer](../../../code/auto-ontology/auto_ontology/catalog/write.py), [DAL transaction](../../../code/auto-ontology/auto_ontology/dal/session.py)

## 5. 검색·질문 처리 용어

| 용어 | 쉬운 뜻 | 이 프로젝트에서의 맥락 |
| --- | --- | --- |
| LLM, Large Language Model | 자연어와 코드를 해석·생성하는 대규모 언어 모델 | Term 제안, 질문 의도 판단, SQL 생성 등에 사용한다. |
| Embedding / vector | 의미를 비교하기 위한 숫자 목록으로 변환 / 그 숫자 표현 | 업무 설명과 질문을 숫자로 표현해 가까운 후보를 찾는다. |
| VDB, Vector Database | vector를 저장하고 유사 검색하는 저장소 | 이 프로젝트는 Postgres의 pgvector를 사용한다. |
| pgvector / collection | Postgres에서 vector를 저장·검색하는 확장 / 검색 데이터 묶음 | 물리 데이터용 `data_objects_layer`, 의미 객체용 `semantic_layer`를 나눈다. |
| Retriever / retrieval | 관련 자료를 찾는 객체 / 찾는 과정 | embedding 검색 결과를 후보로 돌려준다. 최종 답변 생성과 다른 단계다. |
| Candidate / label / distance | 검색 후보 / 객체 종류 표식 / vector 사이 거리 | ColumnAttribute·SqlAttribute 등 종류별로 검색한다. 가까움이 업무 의미의 일치를 보장하지는 않는다. |
| Entity / subject / intent | 질문에 나온 대상·개념 / 중심 대상 / 질문 의도 | “고객별 주문 금액”의 고객·주문·금액을 찾고, 정보 설명인지 계산인지 구분한다. |
| Coverage | 질문의 대상을 의미 후보가 얼마나 덮는지에 대한 평가 | 질문 가능 범위 추정이다. SQL 정답률과 다르다. |
| Evidence | 질문 해석을 돕기 위해 전달하는 추가 설명·근거 문맥 | `evidence` 문자열. 확인된 사실로 자동 보증되는 입력은 아니다. |
| Anchor / value anchor | 후보를 연결하거나 범위를 좁히는 기준 / 특정 값에 관한 힌트 | 무슨 테이블·컬럼·값을 기준으로 문맥을 구성할지 돕는다. 세부 조건은 검색 chapter에서 다룬다. |
| Agent / node / graph / edge | 한 단계의 처리 객체 / 실행 단계 / 단계 연결도 / 다음 단계 연결 | 여기의 agent는 보통 코드의 처리 객체다. 별도의 대화형 AI 작업자를 뜻하지 않는다. |
| State / `path_state` / `decision` | 처리 중 공유 데이터 / 중간 결과 dict / 다음 경로 선택 값 | 후보·SQL·실패 이력을 누적하며 조건에 따라 graph 경로를 바꾼다. |
| Payload / TypedDict / Pydantic | 전달 데이터 / dict의 타입 계약 / 입력 모델·검증 도구 | TypedDict 선언 자체는 런타임 검증을 실행하지 않는다. |
| Probe / precheck / soft check | 확인용 제한 조회 / 본 실행 전 검사 / 반복 실패 뒤 생략될 수 있는 보조 검사 | 검사 존재, 검사 실행, 검사 통과는 구분한다. |
| Reconstruction / full pipeline retry / resume | SQL 다시 작성 / 질문 분석부터 재시도 / 중간 상태에서 재개 | 서로 다른 수준의 재실행이다. |
| Snapshot | 특정 시점 상태의 복원용 보관본 | `restore_from`은 전체 재시도 때 최초 입력 경계로 돌아가는 데 사용한다. |
| SQL dialect / JSONB | DB마다 다른 SQL 문법 / Postgres의 이진 JSON 저장 형식 | SQL 생성·검증·경로 조회 시 DB별 차이를 고려한다. |
| PQL / Kumo | 예측 질의를 표현하는 언어 / 예측 경로에서 사용하는 모델·연동 계열 | 일반 SQL 실행과 구분되는 선택 기능이다. 모델·데이터 전달은 예측 chapter에서 확인한다. |

근거: [retriever](../../../code/auto-ontology/auto_ontology/utils/retriever.py), [VDB 구성](../../../code/auto-ontology/auto_ontology/vdb/__init__.py), [graph](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/text_to_sql_graph.py), [state](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/state.py), [probe 설정](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/db_probe/config.py)

## 6. Web·동시 실행·외부 인터페이스 용어

| 용어 | 쉬운 뜻 | 이 프로젝트에서의 맥락 |
| --- | --- | --- |
| API / REST / endpoint / route | 프로그램용 호출 창구 / HTTP 기반 자원 접근 방식 / 호출 주소 / 주소에 연결된 처리 | `POST /api/chat/completions`가 질문 처리 창구다. 모델 endpoint는 별도로 호출하는 모델 서버 주소다. |
| Gateway / proxy / upstream | 외부 요청의 관문 / 다른 서버로 전달하는 코드 / 전달받아 처리하는 상대 서버 | Next.js가 인증 후 Python Backend에 전달한다. upstream은 바라보는 쪽에 따라 달라진다. |
| MCP, Model Context Protocol | AI 도구·자료를 연결하는 표준 프로토콜 | 외부 에이전트에 `search_terms`, `ask_question` 같은 도구를 제공한다. |
| SSE, Server-Sent Events | 서버가 한 HTTP 응답에서 이벤트를 계속 보내는 방식 | 단계 시작·SQL·답변·차트가 순차적으로 전달될 수 있다. |
| Identity / token / SSO / RBAC | 호출자 신원 / 인증에 쓰는 문자열 / 통합 로그인 / 역할별 권한 제어 | 로그인 확인과 어떤 작업이 허용되는지 확인하는 처리는 구분한다. |
| Worker / subprocess / thread | 실제 작업 실행 담당 / 별도 프로세스 / 한 프로세스 안의 실행 흐름 | Chat은 worker subprocess를 쓰고, 이벤트 수집 등은 thread로 수행한다. |
| WarmPool / standby | 미리 초기화한 worker를 재사용하는 코드 / 유휴 대기 worker | 첫 질문의 초기화 비용을 줄인다. 대기 worker 1개가 전체 동시 질문 1개 제한이라는 뜻은 아니다. |
| Slot / queue / buffer | 진행 작업의 관리 객체 / 순서대로 전달할 통로 / 모아 둔 데이터 | `_Slot`은 대화별 실행·재접속 상태, queue는 프로세스 간 이벤트, buffer는 재생할 이벤트 목록이다. |
| Commit slot | 의미 처리에서 저장 차례를 제어하는 객체 | Chat의 `_Slot`과 다른 개념이다. 병렬 Term 추론 후 저장 순서를 맞춘다. |
| Gate / stateless / persistence | 실행 전 통과 조건 / 대화 이력 없는 요청 / 결과를 저장소에 남기는 처리 | stateless도 별도 analytics가 남을 수 있어 ‘아무것도 저장하지 않음’과 같지 않다. |
| Semaphore / inflight | 동시 실행 수를 제한하는 장치 / 진행 중인 호출 | worker 대기 수, 모델 동시 호출 수, 대화별 실행 제약은 서로 다른 한도다. |
| Circuit breaker, 차단기 | 반복 실패하는 호출을 일정 범위에서 중단하는 장치 | sampling breaker는 응답하지 않는 원본 DB에 테이블마다 샘플 요청을 반복하는 비용을 줄인다. |
| `tee()` / drain | 스트림을 둘로 나눔 / 한쪽 스트림을 계속 읽어 소비함 | Next.js가 브라우저 전달과 upstream 읽기를 분리하는 데 사용한다. |
| Health / readiness / liveness | 상태 확인 / 실제 작업의 의존 조건 확인 / 프로세스 생존 확인 | DB 의존 상태, 의미 계층 존재, 질문 범위 coverage는 서로 다른 검사다. |
| Assertion / mock | 테스트의 기대 조건 검사 / 실제 의존성 대신 쓰는 모형 | mock으로 흐름이 맞아도 실제 DB·모델 동작을 실행 검증한 것은 아니다. |

근거: [worker와 WarmPool](../../../code/auto-ontology/auto_ontology/server/chat/worker.py), [slot·SSE·gate](../../../code/auto-ontology/auto_ontology/server/chat/router.py), [Next.js gateway](../../../code/auto-ontology/frontend/app/api/chat/completions/route.ts), [commit slot](../../../code/auto-ontology/auto_ontology/semantic/pipeline.py), [MCP](../../../code/auto-ontology/mcp/auto_ontology_mcp/server.py)

## 7. 라이브러리·도구 이름을 읽는 법

| 이름 | 문서에서 필요한 최소 의미 |
| --- | --- |
| Next.js / React / TypeScript | 웹 화면과 서버 API를 구현하는 프레임워크 / 화면 구성 라이브러리 / 타입 표현을 더한 JavaScript 언어 |
| FastAPI / Uvicorn | Python HTTP API 프레임워크 / 이 앱을 실행하는 서버 |
| Postgres / PostgreSQL | 내부 catalog·의미 정의·대화 등을 저장하는 관계형 DB. 원본 질의 대상 DB와 역할을 구분한다. |
| Prisma / SQLAlchemy Core | TypeScript 쪽 DB 도구 / Python 쪽 SQL 구성·접근 도구 |
| Alembic / migration | DB 구조 변경 이력을 관리하는 도구 / 구조 변경 작업. 여기서는 설치 안내 대신 저장 구조의 소유권 맥락에서 나온다. |
| LangGraph / LangChain | 상태와 조건에 따른 처리 흐름 구성 / 모델·메시지·도구 연결을 돕는 라이브러리 계열 |
| Better Auth / FastMCP | 웹 인증에 쓰는 라이브러리 / MCP 서버 구현에 쓰는 프레임워크 |
| NVIDIA NIM | 모델 추론 서비스를 제공하는 NVIDIA의 서비스·배포 기술. 문서에서는 설정된 모델 호출 대상으로 등장한다. |
| Vault / pgAdmin | 자격 증명을 보관하는 도구 / Postgres 관리 화면 도구 |
| OpenAPI | HTTP API의 주소·입력·응답을 구조화해 기술하는 규격. MCP 도구 구성에도 활용한다. |
| ETL | Extract·Transform·Load, 데이터를 추출·변환·적재하는 작업. 이 코드의 수집을 원본 전체 복제 ETL로 단정하지 않도록 비교할 때 쓴다. |

기술 이름은 제공된 소스에서 사용하는 역할만 설명했다. 최신 버전 기능 비교는 이 문서의 범위가 아니다. [Python 의존성](../../../code/auto-ontology/pyproject.toml), [Frontend 의존성](../../../code/auto-ontology/frontend/package.json), [제품 설명](../../../code/auto-ontology/README.md)
