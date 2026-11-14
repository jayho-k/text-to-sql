# Chapter 00. 아키텍처 문서의 용어와 예시

이 문서는 Auto-Ontology의 고유 개념과 일반 기술 용어를 구분해 설명한다. 각 chapter에서도 처음 등장할 때 필요한 뜻을 설명하며, 이 문서는 다시 찾아보기 위한 보조 자료다. 코드 식별자는 원문 표기를 유지한다.

- 작성일: 2026-11-07. 표 형식 정리: 2026-11-15.
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

가상 테이블 `customers(id, email)`의 같은 컬럼을 관점별로 구분한 예시다.

| 표현 | 관점·뜻 | 예시에서의 역할 |
|---|---|---|
| `customers.email` | 원본 DB의 물리 컬럼 | 실제 값이 들어 있는 컬럼 |
| Catalog column | 이름·자료형·설명을 앱에 기록한 객체 | 컬럼 구조를 내부 목록으로 관리 |
| `Customer` | 업무 개념인 Term | 데이터를 고객이라는 개념으로 해석 |
| `이메일` | 컬럼과 업무 개념을 연결하는 ColumnAttribute | 고객의 이메일이라는 의미 속성 |
| `PII` 태그 | 개인 식별 정보 관련 분류 표식 | 컬럼에 분류를 연결 |
| Embedding / vector | 구조·의미 설명의 숫자 표현 | 관련 질문으로 검색 |

## 2. PII는 무엇이고, 여기서는 무엇을 하는가

| 용어·객체 | 뜻·역할 | 예시·구분할 경계 |
|---|---|---|
| PII (Personally Identifiable Information) | 개인을 식별할 수 있는 정보 | 이메일 주소·전화번호·사람 이름. 이 프로젝트에서는 관련 컬럼의 분류 기능 이름이기도 하다. |
| `ColumnInput` | 분류에 넣는 컬럼명·테이블명·설명 | 이 입력 모델에는 실제 행의 샘플 값이 없다. 다른 profiling 경로의 원본 값 조회 여부와는 별개다. |
| `pii` / `not_pii` / `review` | PII로 판단 / 아니라고 판단 / 검토 필요 | 분류 결과의 세 상태다. |
| `PiiDecision` | 분류·신뢰도·이유·판단 출처를 담는 결과 | 자동 태그는 PII 판단과 신뢰도 기준을 함께 확인한다. |
| Tagging service | 자동 태그 기준·fallback을 확인해 내부 catalog에 태그를 연결 | 처리 여부도 기록한다. 기본 신뢰도 기준은 `0.9`다. |
| PII 태그 부착 | 예: 신뢰도 조건을 만족한 email 컬럼에 표식 연결 | 원본 이메일 값을 `***`로 바꾸는 마스킹·삭제 처리가 아니다. |

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

## 8. 검색 준비 단계의 기준점과 연결 복원

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
| --- | --- | --- |
| Anchor / anchor table | 질문의 기준 의미 속성 / 그 속성을 소유한 테이블. 고객 이름 속성이 기준이면 고객 테이블이 anchor table이다. | `_identify_anchor`는 속성 ID를 고른다. 테이블 자체를 속성 ID처럼 선택하는 것이 아니다. |
| Value anchor | 질문 표현이 저장 값과 일치한 위치의 단서. `human → race.race = Human` 같은 정보다. | 기준 의미 속성과 별도 구조다. 테이블 후보를 제안하지만 최종 필터 잔존·값 조건의 타당성을 보장하지 않는다. |
| Hub / sibling | 여러 테이블이 참조하는 중심 테이블 / 같은 중심을 참조하는 다른 테이블. orders와 invoices가 customers를 참조하는 경우다. | 발견 목록은 테이블 정보이며 실제 JOIN 컬럼 목록과 다르다. |
| Relevant tables | SQL 생성 모델에게 보여 주는 테이블·컬럼 문맥 | 최종 SQL이 모두 사용해야 하는 강제 목록은 아니다. 필터 뒤 연결 구조를 보충할 수 있다. |
| Pre-filter candidate IDs | 모델 관련성 필터 직전에 보관한 후보 테이블 ID 집합 | 두 테이블 사이 bridge 복원 범위를 제한한다. 이후 발견할 junction 전체를 미리 포함한 집합은 아니다. |
| Junction 확장 / bridge 복원 | 표시된 연결 테이블을 한 단계 새로 발견 / 원래 후보였던 경로의 중간 테이블을 되살림 | Junction은 `is_junction_table` 조건을 따르고, bridge는 중간 경로라는 역할을 따른다. 둘이 같은 분류일 필요는 없다. |
| Forced table | 모델 필터 뒤 코드가 추가하려는 테이블 | ID를 모은 뒤 catalog 재조회가 성공해야 실제 문맥에 들어온다. |
| Row scoping | 어떤 행이 답변 대상인지 제한하는 효과. 검사 기록과 연결되는 환자만 남기는 JOIN 등이다. | 출력 컬럼이 없어도 관련 테이블이 필요할 수 있다. 관련성 모델은 제거가 이 행 집합을 바꾸지 않는지도 보고해야 한다. |
| Metadata backfill | 빈 컬럼 정보를 catalog로 다시 읽어 채움 | 샘플·NULL 허용 여부·의미 FK 키 존재를 검사한다. 기존의 비어 있지 않은 값을 항상 최신 값으로 교체하는 것은 아니다. |

상세 호출·입출력·예시는 [기준 속성·경로](../07-retrieval/chapter-05-anchor-and-semantic-context.md), [hub 확장](../07-retrieval/chapter-05-1-hub-sibling-expansion.md), [테이블 선택·복원](../07-retrieval/chapter-06-table-selection-and-context-reconciliation.md)에 있다. 근거: [준비 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/candidates_preparation.py), [관계 조회](../../../code/auto-ontology/auto_ontology/dal/attributes.py), [값 단서](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/value_anchors.py).

## 9. SQL 생성의 요청·상태·실행 계약

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
| --- | --- | --- |
| Payload / TextToSQLPayload | 호출자가 보내는 요청 / 이 생성 경로의 요청 타입 | 타입상 생략 가능한 connectors도 실제 빌더는 비어 있으면 거부한다. |
| AgentState / path_state | 단계들이 공유하는 데이터 / 그 안의 중간 결과 사전 | 모델·검색기는 최상위에, 질문 종류·테이블·SQL 등은 주로 path_state에 있다. |
| TypedDict / NotRequired | 사전 키·타입의 선언 / 키 생략 가능 표시 | 실행 중 모든 값을 검사하거나 기본값을 채우는 기능과 다르다. |
| Node / edge / routing | 실행 단계 / 단계 연결 / 다음 단계 선택 | 분기마다 question_type·evidence·decision 등 서로 다른 상태를 읽는다. |
| Wrapper / failure_decision | 처리 함수를 감싼 공통 실행 코드 / 해당 agent의 실패 시 분기 값 | 입력 거부·잘못된 반환 타입·일반 실행 예외가 같은 방식으로 처리되지 않는다. |
| Shallow copy / snapshot | 바깥 컨테이너만 복사 / 특정 시점 자료 보관 | 내부 사전은 공유될 수 있다. RetryRestoreState라는 이름이 내부 객체의 변경 불가를 보장하지 않는다. |
| Resume / full pipeline retry | 중간 상태로 지정 지점부터 재개 / 원요청 경계로 돌아가 전체 재시도 | entry 분기표는 question_intent·reconstruct_sql 두 시작 값만 갖는다. |
| Node start event / node update | 노드가 시작했다는 알림 / 노드가 반환한 상태 갱신 | 시작 알림을 완료·성공으로 해석하지 않는다. |

상세 예시·실패 표는 [SQL 생성 Chapter 01](../08-sql-generation/chapter-01-request-state-and-graph-contract.md)에 있다. 근거: [상태 타입](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/state.py), [상태 빌더](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/main.py), [공통 래퍼](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/base.py), [그래프](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/text_to_sql_graph.py).

## 10. 의도 분류와 정보 응답의 반복

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
| --- | --- | --- |
| Information / prediction / calculation | 정의 설명 / 알 수 없는 결과 예측 / 저장 데이터 조회·계산 | “매출의 정의”와 “올해 매출 계산”을 다른 경로로 분류한다. 정보 응답도 후보 검색은 거친다. |
| Calculation subtype | 계산 요청의 하위 종류. 순위·비교·개수·집계·산술 등 아홉 개다. | subtype별 SQL template는 고정 예문이며 실행 SQL이 아니다. |
| Inline evidence | 질문 문장 안에 섞인 공식·해석 지시. “매출은 판매액에서 환불액을 뺀 값” 등이다. | 추출 문자열과 기존 최상위 evidence를 구분하며 부분 문자열 기준으로 중복을 줄인다. |
| Calculation-only / prediction override | 계산임을 전제한 요청 / 예측 강제·금지 설정 | 계산 전용이 우선하며 재작성·근거 분리·예시 선별 호출은 계속한다. |
| Action / observation | 다음 조회 또는 답변 선택 / 실행한 도구 결과 | InformationAgent는 매회 구조화된 행동을 받고 누적 관찰을 다음 프롬프트에 다시 넣는다. |
| Iteration / tool-call budget | 모델 판단 반복 1회 / 실제 새 도구 호출 한도 | 기본 8회 판단·6회 호출이다. 중복 호출은 도구 수를 늘리지 않지만 판단 횟수는 소모한다. |
| Call signature | 도구 이름과 인수를 키 정렬 JSON으로 만든 중복 비교 문자열 | 의미가 비슷하다는 판단이 아니라 구조가 같은 호출인지 비교한다. 실패한 호출도 서명에 남는다. |
| Source IDs / linked column IDs | 답변 근거라고 선택한 객체 ID / 그중 도구 결과에서 컬럼으로 수집한 ID | 알려진 ID와의 교집합은 답변의 모든 문장을 사실 검증하는 기능과 다르다. |

호출·상태·실패와 예시는 [의도 분류](../08-sql-generation/chapter-02-intent-and-information-routing.md), [정보 응답 반복](../08-sql-generation/chapter-02-1-information-agent-loop.md)에 있다. 근거: [QuestionIntentAgent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/question_intent.py), [InformationAgent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/information_agent.py), [도구 등록·디스패치](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/information_tools.py).

## 11. 정보 조회의 페이지·범위·표시 제한

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
| --- | --- | --- |
| Dataset / schema / parent ID | 등록 DB 객체 / 테이블 이름 공간 / 상위 객체 식별자 | 정보 도구의 dataset은 DB다. 스키마 ID 목록 조회는 database_name을 받아도 실제 DAL에서 무시한다. |
| Pagination / skip / limit | 구간별 조회 / 건너뛸 수 / 읽거나 반환할 수 | 컬럼은 페이지를 지원하지만 모든 목록 도구가 skip을 적용하지는 않는다. |
| Sentinel row | 초과 여부를 확인하려고 하나 더 읽는 행 | 컬럼·속성 100개 제한에서 101개를 요청한다. 속성 검색은 그 101개 안에서만 ID/이름을 찾을 수 있다. |
| Truncated | 일부 결과가 생략됐다는 응답 표시 | 전체 중첩 목록·SQL 길이·실제 DB 조회량까지 제한했다는 뜻은 아니다. 도구마다 판단 필드가 다르다. |
| ID resolution / name resolution | 식별자로 직접 읽기 / 이름에서 대상을 찾기 | ID 경로가 함께 준 DB 이름까지 재검증하지는 않는다. 이름 대소문자·모호성 규칙도 도구마다 다르다. |
| Zone scoping | 접근할 catalog 객체 범위를 zone_ids로 제한하는 처리 | DAL의 None은 범위 제한 없음이고 빈 목록은 허용 범위 없음이다. 정보 도구가 이 인수를 전달하는지 따로 봐야 한다. |
| Connected tables / semantic FK | 저장 table__join 이웃 / 컬럼의 의미 참조 관계 | 정보 표시의 이웃·의미 연결과 실제 SQL 경로에 선택된 관계는 같은 목록이 아니다. |

도구별 입력·반환·실패·DAL·테스트는 [정보 조회 Chapter 02-2](../08-sql-generation/chapter-02-2-information-tools-and-catalog-access.md)에 있다. 근거: [도구](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/information_tools.py), [구조 DAL](../../../code/auto-ontology/auto_ontology/dal/datasources.py), [범위 해석](../../../code/auto-ontology/auto_ontology/dal/users.py), [의미 상세](../../../code/auto-ontology/auto_ontology/dal/exploration.py).

## 12. 근거의 필드 연결과 값 보정

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
| --- | --- | --- |
| Schema grounding | 업무 표현을 실제 컬럼·조건으로 연결. “유료 계정”을 인용한 계정 flag 조건으로 바꾸는 등이다. | 모델의 전체 질문·근거 제안을 수용한다. 검사 함수는 모든 수식·문장의 보존을 증명하지 않는다. |
| Physical reference / quoting | 실제 컬럼의 한정 이름 / 이름을 인용해 한 항목으로 표현 | connector·방언으로 만든 정확한 문자열이 검사 기준이다. |
| Grounded evidence / refined evidence | 필드를 연결한 근거 / 그 뒤 값·연산자를 보정한 근거 | 2차 실패가 1차 연결까지 사용자 원문으로 되돌리는 것은 아니다. |
| Scalar / literal / predicate operator | 단일 값 / 직접 적은 값 / 비교 연산자 | 100·Active와 >= 같은 값을 보정한다. 수식 전체를 SQL 문법으로 검증하는 단계는 아니다. |
| Full-line repair / atomic application | 전체 행 교체 / 수정 묶음 전부 수용 또는 전부 거부 | 2차 입력 행에 대해 적용하며 원래 줄바꿈을 붙인다. DB 트랜잭션과는 다르다. |
| Value support | 값 단서·샘플·질문에서 수정값을 찾는 조건 | 단서 성공 때 샘플은 생략하지만 단서 불일치 뒤 샘플은 허용한다. 원본 DB를 재조회하지 않는다. |
| SequenceMatcher / changed span | 문자열 차이를 나누는 도우미 / 달라진 구간 | 최대 세 구간·문자 수·첫 비교식의 좌우를 검사하는 규칙이다. 의미 동등성 증명이 아니다. |
| Corrected question | 값 보정 모델이 함께 제안한 전체 질문 | 수용된 행이 있고 알려진 물리 필드 집합이 같으면 수용할 수 있다. 각 값이 정확히 같은 방식으로 바뀌었는지 대조하지는 않는다. |

호출·검사·실패·예시는 [필드 연결과 조율](../08-sql-generation/chapter-03-evidence-refinement.md), [행·값·질문 보정](../08-sql-generation/chapter-03-1-evidence-value-and-operator-repairs.md)에 있다. 근거: [보정 agent와 검사 함수](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/evidence_refinement.py), [이름 인용](../../../code/auto-ontology/auto_ontology/utils/sql_identifiers.py), [저장 샘플 변환](../../../code/auto-ontology/auto_ontology/utils/sample_values.py), [SQL 생성에서의 근거 지시](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/prompts.py).

## 13. SQL 후보·출력 모델과 생성 문맥

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
| --- | --- | --- |
| SQL candidate / constructable | 아직 검사 전인 SQL / 다음 검사로 넘길 수 있는 생성 결과 | 실행 성공·정확성 보장과 다르다. 결과 객체는 후속 검증 노드가 읽는다. |
| SQLGenerationModel | thought·sql_code·response 세 필드의 응답 계약 | SQL 필수·공백/점 대체 거부·추가 필드 금지다. 남은 텍스트 전용 호환 분기와 구분한다. |
| Thought / response | 짧은 방법·가정 요약 / 사용자용 설명 | SQL 성공 반환에 자연어 답변을 AIMessage로 즉시 붙이지 않는다. 비공개 내부 추론 전체를 요구하는 계약이 아니다. |
| Generation retry / reconstruction | 모델 응답 재시도 / 실패 SQL을 검사 결과로 고쳐 생성 | 기본 생성은 바깥 3회와 내부 최대 3회가 겹칠 수 있다. 전체 파이프라인 재시도와 별개다. |
| SQL template / reference query pattern | 계산 유형 예문 / 다른 질문·DB의 구조 참고 | 현재 DB의 저장 분석 SQL과 다르며 외부 이름·상수를 그대로 가져오지 말라고 지시한다. |
| Projection / row grain | 반환 컬럼 선택 / 결과 한 행의 의미 | shorten_answer는 단순한 문장 길이 설정보다 넓은 SQL 출력 규칙을 바꾼다. |
| Important columns / semantic hint | 의미가 맞은 컬럼 강조 / 기준 테이블·경로 안내 | 최종 스키마·구조 경로와 표시 조건이 다르다. 일부 필드의 대체 표시는 실제 존재 검증이 아니다. |
| Prompt precedence | 여러 자료가 충돌할 때 모델에게 준 우선순위 | 근거·현재 스키마와 질문이 참고 예시보다 우선하도록 지시한다. 코드가 생성 SQL의 모든 규칙을 강제한 것은 아니다. |

상세 호출·실패·반환은 [생성 조율](../08-sql-generation/chapter-04-sql-prompt-and-output.md), 입력 예시·문맥 구분은 [포맷터·규칙](../08-sql-generation/chapter-04-1-sql-context-and-prompt-rules.md)에 있다. 근거: [기본 생성 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_from_semantic.py), [응답 모델](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/models.py), [프롬프트](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/prompts.py), [포맷터](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/formatters_util.py).

## 14. 대상 DB·방언·이름 표기의 계약

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Canonical database name | 설정에 등록된 DB 표기. 요청 SALES를 sales로 돌려주는 등이다. | 명시 요청은 정확 일치 우선·유일한 casefold 일치다. 테이블 기반 연결 선택은 대소문자를 보정하지 않는다. |
| Connector routing | 관련 테이블의 DB 이름으로 사용할 연결 객체 선택 | target_db 인수나 SQL 파싱 없이 선택한다. 일부 누락은 건너뛰고 중복 연결 이름은 마지막 객체가 남는다. |
| Dialect / SQLGlot | DB별 SQL 문법 / SQL 분석·변환 라이브러리 | 연결의 dialect를 직접 전달한다. 전체 연결의 검증 방언 목록과 선택 연결의 실행 방언을 구분한다. |
| Catalog / schema namespace | 테이블을 구분하는 상위 이름 공간 | Databricks의 database_name은 catalog다. 프로젝트의 메타데이터 저장소인 catalog와 구분한다. |
| Qualified / quoted identifier | 상위 이름을 붙인 식별자 / 따옴표로 경계를 표시한 식별자 | connector.qualify는 조회용 인용 이름, qualify_table은 인용 없는 표시 문자열이다. 생성 지시까지 동일한 계약은 아니다. |
| Bare table name | schema·DB를 붙이지 않은 이름. orders 등이다. | SQLite·DuckDB 시스템 지시는 이를 요구하지만 표시 포맷터는 해당 방언에서 접두어를 무조건 제거하지 않는다. |
| Mixed-case identifier repair | 알려진 대문자 포함 이름에 인용을 추가하는 처리 | 정확한 철자만 수용하며 잘못된 대소문자나 모든 catalog/schema 접두어를 고치는 기능이 아니다. |
| Dialect sanitization | 실행 전 방언에 따라 문자열을 정리하는 처리 | 현재 실행 helper의 SQLite PUBLIC 접두어 정규식 제거는 일반 SQL 구조 변환과 다르다. |

예시·상태·실패·테스트 한계는 [SQL 생성 Chapter 05](../08-sql-generation/chapter-05-database-and-dialect-routing.md)에 있다. 근거: [라우팅](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/connector_routing.py), [연결 인터페이스](../../../code/auto-ontology/auto_ontology/connectors/base.py), [표시 포맷터](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/formatters_util.py), [시스템 지시](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/prompts.py), [실행](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_execution.py).

## 15. 전체 재시도·재개와 SQL 이벤트의 수명

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Full-pipeline attempt | 질문 의도부터 답변까지 한 번의 처리 | 지정 실패 노드·빈 답변 SQL·복원값·시도 수 조건으로 최대 두 전체 시도다. 모델 호출 횟수와 다르다. |
| Retry snapshot / shallow copy | 복원용 요청 묶음 / 바깥 사전·목록 복사 | immutable 주석과 중첩 객체의 실제 독립성을 구분한다. 원래 입력 경로에 명시 삭제 목록을 적용한다. |
| Resume seed / entry router | 중간 시작에 필요한 기존 상태 / 시작 노드 선택 | _resume_from으로 새 graph의 시작점을 고른다. 실행 checkpoint 복구가 아니다. coordinator가 사용 후 키를 제거한다. |
| Prior-round history / current budget | 이전 차례 참고 이력 / 현재 수정 횟수 | debug seed는 prior_round_failed_attempts와 failed_attempts를 분리해 새 한도를 확보한다. |
| Deterministic SQL fallback | 의도 검사에서 거부됐던 마지막 SQL을 대체 반환 | 반환 함수가 재검증·재실행하지 않는다. SQL과 저장 결과/설명이 같은 시점이라는 보장도 없다. |
| Recursion limit | graph 진행 단계의 상한 | 45는 실행 시간·모델 호출 수·SQL 재구성 횟수와 같은 단위가 아니다. |
| Step start / end | 단계 시작 / 완료 알림 | 시작은 custom 통로, 완료는 updates 통로에서 만든다. 예외 때 완료가 없을 수 있다. |
| SQL event / last_sql | 실행 직전 검사를 통과한 SQL 알림 / 호출자가 기억한 마지막 알림 SQL | 실행 성공 증거가 아니다. 최종 답변이 비어도 실패 기록용 SQL로 저장할 수 있다. |
| Partial answer / AgentRunError | 실패 이전 SQL·설명 일부 / 그 값을 가진 오류 타입 | 스트리밍 오류·비스트리밍 예외와 상태 반환 함수의 오류 사전은 다른 계약이다. |
| Buffer replay / graph resume | 이미 전송한 이벤트 다시 읽기 / 중간 노드부터 실행 시작 | 전송 재접속이 모델·DB 작업을 다시 시작한다는 뜻은 아니다. |

호출·삭제/보존·한도·재개 예시는 [Chapter 06](../08-sql-generation/chapter-06-full-retry-and-resume.md), 이벤트·부분 답변·저장 경계는 [Chapter 06-1](../08-sql-generation/chapter-06-1-streaming-and-caller-boundaries.md)에 있다. 근거: [실행 루프](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/main.py), [그래프](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/text_to_sql_graph.py), [대화형 coordinator](../../../code/auto-ontology/auto_ontology/retrieval/interactive/coordinator.py), [chat router](../../../code/auto-ontology/auto_ontology/server/chat/router.py).

## 16. SQL 구문·정적·의도 검사의 계약

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Static validation / 정적 검사 | 대상 DB에서 쿼리를 실행하기 전에 SQL 구조·메타데이터로 확인 | 내부 catalog 조회와 모델 호출은 있을 수 있다. 실제 원본 DB 성공·질문 정답을 보장하는 이름이 아니다. |
| Parse / AST | SQL 문자열을 SELECT·조건 등의 구조로 읽기 / 그 구문 트리 | SQLGlot은 입력 방언 목록 중 처음 구문 파싱에 성공한 것을 사용한다. 전체 컬럼 존재 검사를 강제하지 않는다. |
| CTE / Common Table Expression | WITH로 정의한 임시 이름. `WITH x AS (...) SELECT ... FROM x`의 x | 추출기는 임시 이름 자체를 원본 테이블로 세지 않고 실제 참조를 찾는다. |
| Catalog-resolved references | SQL에서 내부 catalog의 ID로 연결한 테이블·컬럼 | 일부 불명확한 이름을 생략할 수 있다. ID가 있는 것과 SQL의 모든 참조를 해결한 것은 다르다. |
| Qualify / qualified column | 컬럼에 소유 테이블 등을 붙이기 / `o.customer_id`처럼 소유를 적은 이름 | 추출기의 qualify 실패는 원래 트리로 대체하고 `validate_qualify_columns=False`를 사용한다. |
| Degenerate SQL | 데이터 답변을 만들지 않는 대체 SQL. 상수 출력·LIMIT 0 등 | 단순한 구조 검사다. 모든 불가능한 조건이나 UNION의 모든 분기를 증명하지 않는다. |
| Vacuous aggregation / 무효 집계 | 키별 한 행만 남아 의도한 여러 행 요약이 사라진 집계 | 기본 비활성인 `DETECT_VACUOUS_GROUP_BY`가 켜졌을 때 단일 테이블 SELECT와 키 정보로 추정한다. 질문을 직접 읽지 않는다. |
| Composite PK / 복합 기본 키 | 여러 컬럼의 조합으로 행을 구별. `(race, driver, lap)` 등 | 무효 집계는 전체 PK 포함을 검사하지만 집계 누락의 JOIN 유일성 판정은 개별 컬럼 포함을 사용한다. |
| Many side / 다수 쪽 | 한 기준 행에 여러 행이 연결될 수 있는 쪽. 고객에 대한 주문 등 | 이 정적 검사는 JOIN EQ와 PK·관찰 unique 목록으로 추정한다. 실제 원본 데이터의 연결 개수를 측정하지 않는다. |
| Projection / 투영 | SELECT가 내보내는 필드·표현식 목록 | 짧은 답변 모드에서 정확한 출력 일치를 모델에게 지시한다. AST 출력과 질문의 독립적인 결정 규칙 비교는 아니다. |
| Intent validation / 의도 검사 | SQL이 질문·근거에 맞는지 모델에게 판단시키기 | None·호출 오류·False인데 문제 목록 없음도 통과할 수 있다. 통과는 정답 인증이 아니다. |
| Structured output / 구조화 응답 | is_valid와 문제 목록처럼 정해진 필드에 맞춘 출력 | Pydantic은 형식을 검사한다. 내용의 정확성을 입증하지 않는다. 문제 목록의 빈 문자열은 빈 목록으로 보정한다. |
| Fail-open / 오류 시 허용 | 검증 서비스가 판단을 못 해도 다음 처리를 계속함 | 의도 helper의 None·로컬 호출 예외에 적용된다. catalog 조회·문맥 구성 예외 전체에 적용되는 정책은 아니다. |
| Hard cap / soft blocking limit | 강제 종료 상한 / 보조 검사의 차단 중단 기준 | invalid_sql은 재구성 이력 7개 이상에서 종료한다. soft router는 이력 5개 초과에서 통과시키며 의도 검사를 끄지는 않는다. |
| numeric_type_alignment | 평가용 숫자 표현 일치를 요청하는 옵션 | PostgreSQL cast 외에 NULL 비교·STRING_AGG 순서에 영향이 있고 DISTINCT ON을 거부하는 분기도 활성화한다. |
| Probe / 확인용 조회 | 특정 값·관계가 있는지 작은 SQL로 살펴보기 | 본문 구문·의도 검사에서 원본 DB probe를 수행하지 않는다. 별도 값 검사·precheck·빈 결과 보정의 범위다. |

순서·상태·검사 한계는 [구문·정적 검사](../09-sql-validation/chapter-01-parse-and-static-validation.md), 모델 판정표·상한·설정 수명은 [의도 검사와 분기](../09-sql-validation/chapter-02-intent-validation-and-routing.md)에 있다. 근거: [통합 검증](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_parse_validation.py), [추출기](../../../code/auto-ontology/auto_ontology/catalog/parsers/sqlglot_extractor.py), [키 조회](../../../code/auto-ontology/auto_ontology/dal/datasources.py), [그래프](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/text_to_sql_graph.py).

## 17. SQL 값 검사·증거와 probe cache

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Column-bound literal | 조건에서 특정 컬럼과 연결된 직접 값. `status='actve'` 등 | 비교·IN·BETWEEN·CASE 조건의 일부 형태를 추출한다. SQL의 모든 직접 값을 수집하지는 않는다. |
| Value checklist / check ID | 값별 확인 목록 / 그 SQL 안의 `value_1` 같은 순번 | 영구 컬럼 ID가 아니다. 변경 없는 finish는 전체 항목 확인 기록을 강제하지 않는다. |
| Substitution / 값 치환 | 확인한 literal을 다른 저장 값으로 교체 | 원문 문자열 치환 후 값 제거 AST·체크리스트를 다시 비교한다. 하나라도 실패하면 묶음 전체를 버린다. |
| Literal skeleton | 모든 literal을 같은 placeholder로 바꾼 SQL 구조 | 조건·JOIN 등의 구조 유지 검사다. SQL의 정답이나 evidence 문맥 보존을 증명하지 않는다. |
| Absence / proof query | 원값 조회 0행 / 대체 값이 반환된 성공 조회 | 컬럼·literal 언급은 텍스트 검사이고, proof는 행의 모든 값을 비교한다. 해당 컬럼의 정확 동등 존재 증명과는 경계가 있다. |
| Query cache / finding | 조회 결과를 기억한 사전 / 존재·보정 사실 요약 | connector 이름·방언과 SQL 또는 컬럼·값이 키다. 사용자 인증·데이터 버전·만료 조건을 키로 포함하지 않는다. |
| Observation window | 모델에게 반복해서 보여주는 최근 조회 요약 | 최근 8개·각 첫 컬럼 최대 5개 값이다. 생략된 조회의 증거는 query cache에 남는다. |
| Per-visit probe budget | 노드 한 번 방문에서 허용하는 새 조회 횟수 | 값 검사에서는 20회이며 재구성 후 새 executor에서 다시 시작한다. 질문 전체 공유 예산은 아니다. |
| LIMIT bounded / 결과 잘림 | LIMIT 보충 / 모델에게 보낼 행 수 자르기 | limit 단어가 이미 있으면 보충하지 않는다. 받은 DataFrame의 head 제한이 DB 전체 스캔·전체 반환량 제한과 같지는 않다. |
| Probe timeout | 확인용 DB 조회에 적용하는 시간 인수 | 이 경로는 공통 SQL timeout 기본 30초를 지원 connector에 전달한다. probe config의 5초 상수는 전달하지 않는다. |

입출력·캐시 수명·증거 판정·관련 테스트는 [값 검사와 probe](../09-sql-validation/chapter-03-value-validation-and-probe.md)에 있다. 근거: [값 검사 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_value_validation.py), [probe 실행기](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/db_probe/executor.py), [공통 SQL 실행](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/chat_sql.py).

## 18. 합성 precheck·직접 보정과 상태 수명

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Combined precheck | 값·JOIN·JSONB 검사를 묶은 실행 전 한 노드 | 값→JOIN→JSONB 순서다. JOIN invalid면 그 차례의 JSONB를 생략한다. |
| Working state / shallow copy | 하위 검사가 이어받는 작업 상태 / 바깥 사전만 복사 | 내부 객체는 공유할 수 있다. 전부 독립된 상태나 실패 때 자동 복원되는 transaction은 아니다. |
| Self-applied fix / 직접 보정 | helper가 모델 재구성 없이 SQL을 수정 | 합성 valid 후 전체 의도 검증을 재진입하지 않는다. 일부 bridge candidate에 세 정적 helper를 적용한다. |
| Bridge / hub / hop | 중간 연결 테이블 / 여러 테이블이 공통 참조하는 중심 / 관계 한 번 | 일부 한 중간 테이블 형태는 직접 삽입한다. 연결의 존재와 질문 의미·행 수 정확성은 별도다. |
| Integer division / numeric scale | 정수 나눗셈의 소수 손실 / 퍼센트와 비율 등 숫자 규모 | proactive 값 agent 안에서 검사한다. 모델 값 검사 flag로 이 하위 agent를 생략하면 함께 생략된다. |
| JSONB key/container | JSON 값의 이름 / 다른 키를 담은 상위 객체 | 점으로 뭉친 키를 중첩 경로로 바꾸는 직접 보정이 있다. 정확한 판정은 helper별로 확인해야 한다. |
| Case-dirty JOIN predicate | 추가 JOIN 조건이 대소문자·공백 차이로 행을 놓치는 문제 | agent는 진단을 모아 모델 재구성에 넘긴다. 조건을 무조건 삭제하는 처리가 아니다. |
| Repair attempts / mismatch | 문제 처리 횟수 / 검사에서 발견한 불일치 항목 | JOIN은 남은 문제가 있을 때만, JSONB는 직접 보정 포함 mismatch 처리 시 count를 늘린다. 문제 없는 모든 방문 횟수가 아니다. |
| error_known_fixable / stale flag | 현재 정보로 고칠 수 있다는 표시 / 이전 판단이 남은 상태 | 합성 노드는 invalid 시점의 공유 flag를 AND한다. 이전 True가 각 오류의 독립 판단을 대신할 가능성은 미재현 경계다. |

호출·분기·상태·테스트 범위는 [합성 precheck](../09-sql-validation/chapter-04-combined-precheck-and-state.md)에 있다. 근거: [합성 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/combined_precheck.py), [값 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/proactive_value_check.py), [JOIN agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/join_path_check.py), [JSONB agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/jsonb_path_check.py).

## 19. 저장 문자열·고유값 수와 수치 추정

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Cardinality / DISTINCT | 서로 다른 값의 개수 / 중복 제거 조회 | 기본 20개 이하를 작은 집합으로 본다. T+1개 조회의 rows가 잘리면 큰 집합 여부도 잘못 판단할 수 있다. |
| Near-miss / 유사 값 | `H1B`와 `H-1B`처럼 철자·간격이 비슷한 값 | 먼저 strip·casefold 형제를 보고, 없으면 difflib 최대 3개·cutoff 0.6을 사용한다. 의미 동일성 검사는 아니다. |
| Case sibling / 표기 형제 | `Certified`와 `CERTIFIED`처럼 정규화하면 같은 저장 값 | 업무 의미상 동일한 값인지·DB 문자열 비교 규칙이 같은지는 독립적으로 확인하지 않는다. |
| Point probe / 개별 값 조회 | 고유값이 많을 때 한 literal의 존재와 변형만 조회 | 실제 빈 결과를 나타내는 result_was_empty가 참일 때만 수행한다. 실행 전 경로에는 적용하지 않는다. |
| Collation | DB가 문자열을 정렬·같음 비교하는 규칙 | Python casefold·정규식 IGNORECASE 결과와 항상 같다고 가정하지 않는다. |
| LIKE regex approximation | 패턴을 정규식으로 바꿔 누락 값을 추정 | ESCAPE·DB별 비교 규칙 등을 완전히 재현하지 않고, 수리 안내의 ILIKE 권고는 방언별 분기가 없다. |
| MIN/MAX range / numeric scale | 저장값 최소·최대 / 숫자 기준의 단위 규모 | used가 범위 밖이고 ×100 또는 ×0.01이 안으로 들어오면 후보를 제안한다. 별도 거리 기준·질문 단위 확인·직접 보정은 없다. |
| Operand type / unknown | 분자·분모의 타입 / 정보를 몰라 확정하지 못함 | 한쪽 정수 True·다른 쪽 None도 나눗셈 검출 대상이다. 모든 식의 결과 타입을 계산하는 함수는 아니다. |
| Local cache / 짧은 이름 | helper 한 번 동안 기억하는 조사 결과 / schema 없는 테이블명 | 같은 executor 예산을 공유해도 문자열 cache와 범위 cache는 별개다. 동명 schema·별칭 충돌은 남는다. |

예시·조회 SQL·경계·20개 테스트 열람 결과는 [값·스케일·나눗셈 상세](../09-sql-validation/chapter-04-1-literal-scale-and-division-checks.md)에 있다. 근거: [literal helper](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/db_probe/literal_check.py), [helper 테스트](../../../code/auto-ontology/auto_ontology/tests/test_literal_check.py).

## 20. JOIN 경로 검사의 근거와 직접 보정

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Correlated subquery / 상관 하위 쿼리 | 안쪽 쿼리에서 바깥 테이블 컬럼을 참조 | JOIN 검사 추출은 ON뿐 아니라 모든 WHERE의 컬럼 EQ도 찾는다. alias 이름 공간은 전체 트리 사전이다. |
| FK participation / selected path edge | 의미 FK 관계에 참여 / 경로용으로 선택된 관계 | 참여 여부는 비선택 관계도 볼 수 있지만 실제 경로 edge는 use_in_join_paths=True로 제한한다. |
| Table BFS / shortest path | 가까운 테이블부터 찾아 관계 수가 가장 적은 경로 선택 | 입력 컬럼은 끝 테이블을 지정한다. 실제 JOIN 키는 반환 hop에 있으며 질문 적합성 순위는 아니다. |
| PK-gated reverse edge | 속성 소유 컬럼이 PK 배열에 있으면 반대 방향 허용 | helper 주석의 정방향 전용 설명과 달리 현재 DAL은 이 역방향을 만든다. 복합 PK 전체 유일성 판정은 아니다. |
| Overlap denominator / 방향성 | 서로 다른 비NULL 왼쪽 값이 분모인 겹침 비율 | 0.2 이상이면 유지한다. 유효한 낮은 비율이면 반대 방향을 다시 조회하지 않는다. |
| unverified / None overlap | 관계를 확정 못 한 판정 / probe가 비율을 못 구함 | 낮은 겹침뿐 아니라 조회 실패·빈 분모·예산 소진도 unverified로 갈 수 있다. |
| wrong_column / missing_bridge | 알려진 다른 연결 컬럼 / 필요한 중간 연결 테이블 후보 | 일부 모양만 직접 보정한다. 적합한 질문 의미·집계 단위·outer JOIN 보존을 인증하지 않는다. |
| Bridge AST insertion | SQL 구조 안에 중간 JOIN을 삽입 | 기존 JOIN 직전에 기본 JOIN을 넣는다. 중간 테이블 이미 사용·긴 경로·WHERE 암시적 JOIN은 직접 삽입 대상에서 제외한다. |
| Verified core / extra predicates | 의미 관계로 확인된 비교 / 같은 테이블 쌍의 나머지 비교 | case-dirty probe에서 각각 AND로 재구성한다. 원본의 모든 논리 문맥·필터를 그대로 실행하는 것은 아니다. |
| Casing-only rejects | 원문 비교에서 제외되지만 LOWER/TRIM 후 맞는 행 | 양수인 total_rejects와 전부 같을 때만 경고한다. NULL의 UNKNOWN까지 모든 제외 행을 포함하는 집계는 아니다. |

실제 조회·분기·AST 변경·테스트와 미확인은 [JOIN helper 상세](../09-sql-validation/chapter-04-2-join-path-overlap-and-repair.md)에 있다. 근거: [JOIN helper](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/db_probe/join_path_check.py), [경로 DAL](../../../code/auto-ontology/auto_ontology/dal/attributes.py), [컬럼 ID 조회](../../../code/auto-ontology/auto_ontology/dal/datasources.py).

## 21. JSONB 키 조사·타입 fallback과 점 키 보정

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Scalar extraction / JSON path | JSON 값을 문자열로 읽기 / 객체 안의 접근 경로 | 평면 `col->>'key'`와 한 단계 중첩만 분해한다. 단순 JSON 반환·배열·복잡한 경로 전체를 검사하지 않는다. |
| Container / sibling containers | 상위 객체 / 다른 최상위 섹션들 | 현재 container의 키 목록이 있고 하위 key가 없을 때 최상위 섹션을 보충한다. container 자체가 없으면 생략될 수 있다. |
| jsonb_object_keys / object filter | 객체의 키를 행으로 펼치는 함수 / 객체 행만 조사 | NULL·scalar·배열·빈 객체의 0행 결과는 키 부재가 아니라 미해결 None이다. |
| Available key union | 테이블 객체에서 발견한 서로 다른 키 모음 | 원래 질문의 필터별·모든 행의 존재 보장이 아니며 LIMIT 잘림도 확인하지 않는다. |
| wrong_type fallback | 키 조회 미해결 때 기존 비JSON 타입으로 오류 판단 | known_types 문자열에 json 포함 여부를 본다. 새 타입 조회·함수 지원 검증은 아니다. |
| Flattened dotted key | `profile.city`처럼 점으로 합친 단일 키 | 평면 키의 앞부분이 실제 상위 키와 맞으면 중첩 접근으로 원문 전체 치환한다. 하위 키를 추가 조회하지 않는다. |
| Exact text self-apply | 공백·인용이 같은 문자열을 찾아 직접 수정 | 컬럼 AST 위치·같은 패턴의 모든 등장 의미·수정 뒤 경로 검증을 구분하지 않는다. |

조회 SQL·예산·None/타입·직접 보정·테스트는 [JSONB helper 상세](../09-sql-validation/chapter-04-3-jsonb-key-path-validation.md)에 있다. 근거: [JSONB helper](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/db_probe/jsonb_path_check.py), [JSONB agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/jsonb_path_check.py), [관련 테스트](../../../code/auto-ontology/auto_ontology/tests/test_jsonb_path_check.py).

## 22. 재구성·원인 분류·수정 이력

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Reconstruction / 내부 재구성 | 실패 SQL을 오류와 함께 다시 만들기 | 일반 응답은 성공 decision을 새로 쓰지 않고 생성 결과를 바꿔 다음 검증으로 보낸다. |
| sql_correction / fast path | 실행 쪽이 준 보정 SQL / 모델 작업 생략 경로 | 특정 오류·다른 비어 있지 않은 보정일 때 모델 없이 채택한다. 실패 이력은 소비하며 실행용 sql_code를 이 자리에서 같이 쓰지는 않는다. |
| Error normalization / error_details | 오류를 안전한 문자열로 만들기 / 원문 보존 | 상세는 setdefault이므로 이전 상세가 있으면 현재 오류 원문으로 덮지 않는다. |
| missing_data / fixable | 새 데이터가 필요 / 현재 테이블로 고칠 문제 | 분류 응답 None이면 fixable로 대체한다. 새 데이터 분류 자체가 검색 성공·질문 해결을 보장하지 않는다. |
| error_analysis_done | 현재 재구성 흐름에서 첫 분류를 했다는 표시 | 호출 전에 True로 바꾸며 일반 수정에서 초기화하지 않는다. 새 오류마다 자동 재분류·재검색하지 않는다. |
| Discovery / 추가 테이블 발견 | 의미 검색으로 수정에 필요한 새 테이블 찾기 | 검색어마다 Table label·k=3·target_db로 요청한다. 기존 ID는 제외하므로 기존 컬럼 metadata 일반 refresh는 아니다. |
| Interpretation history | 이전 응답이 적은 질문 해석·가정의 누적 | 유효한 가정 유지·변경 이유를 모델에게 지시한다. 의미 보존을 코드가 독립 검사하지는 않는다. |
| Repair turn stripping | 이전 오류 HumanMessage를 현재 모델 입력에서 제거 | 정확 prefix로 필터링한다. 수정된 messages 사본을 state로 반환하지 않는다. |
| Current/prior-round attempts | 현재 수정 예산에 쓰는 실패 / 이전 차례 참고 실패 | 둘 다 프롬프트에 표시하지만 길이 상한은 현재 failed_attempts를 기준으로 계산한다. 항목 SQL·오류는 각각 600자 표시다. |
| Unconstructable response | 생성 불가 설명을 담는 최종 응답 | 모델 없이 final_response의 빈 SQL·기본/전달 설명과 AIMessage를 만든다. 상위 전체 재시도·SQL fallback은 별도다. |

입력·조회·프롬프트·상태·테스트는 [재구성 상세](../09-sql-validation/chapter-05-sql-reconstruction-and-failure.md)에 있다. 근거: [재구성 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_reconstruction.py), [생성 불가 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_unconstructable.py), [테이블 검색](../../../code/auto-ontology/auto_ontology/retrieval/data_access/relevant_tables.py).

## 23. SQL 실행·결과 표현과 숫자 제출 보정

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| QueryResponse / records JSON | 실행 결과 객체 / 행 객체 목록의 JSON 문자열 | 실제 path_state에는 객체 전체가 아닌 JSON 문자열 목록을 저장한다. 빈 결과도 `['[]']`다. |
| Result label / deduplication | 결과 컬럼 이름 / 중복 이름에 번호 붙이기 | 기존 이름을 예약해 `ID, ID, ID__2`를 `ID, ID__3, ID__2`로 바꾼다. SQL alias 수정은 아니다. |
| Statement timeout | DB 문장 실행 제한 시간 | 공통 helper는 지원 connector에만 인수를 전달한다. 전체 연결·취소의 시간 보장은 엔진별 계약이다. |
| Infrastructure marker / SQLSTATE | 접속 문제를 나타내는 문자열 / 드라이버 상태 코드 | 현재 분류는 문자열 marker를 사용한다. SQLSTATE 기반 분기가 아니다. SQL echo·literal을 제거한 뒤 검사한다. |
| Numeric kind / Decimal / float | 결과 표에서 관찰한 숫자 종류 / 십진수 / 부동소수점 | DB 선언 타입 전체를 조회하지 않는다. NULL 때문에 정수처럼 보이는 float는 None 처리할 수 있다. |
| SQL tag | 어느 SQL의 결과인지 붙인 문자열 표식 | 현재 SQL의 strip 결과와 일치해야 종류·digest를 재사용한다. 의미상 같은 SQL 판정은 아니다. |
| Values digest / SHA-1 | 결과 값을 정규화한 짧은 hash | 숫자는 소수 둘째 자리·시간은 날짜 단위다. 행·열 순서는 구분하고 컬럼 이름·원래 타입은 제외한다. |
| Numeric alignment / opposite type retry | 숫자 표현 통일 / 최초 제출과 반대 표현 시도 | 혼합 통일·DEBUG 재시도는 interactive caller가 직접 실행한다. 모두 실행 agent 자체 기능은 아니다. |
| Dominant kind | 최초 제출의 대표 숫자 종류 | 다수결이 아니라 decimal 우선, 다음 float다. 안정화 전 digest와 마지막 채택 결과의 kind는 시점이 다르다. |
| Tie-break / chronological order | 동률 순서를 정할 추가 키 / 기간순 정렬 | ID·rank·기간 접미사 규칙이다. 질문 의도·유일 키를 독립 증명하지 않는다. |
| same_values | 보정 전후 값 요약 비교 | SUM 정수 cast 단계에서 후보 실행 후 원문을 재실행한다. 다른 안정화 단계의 기본은 실행 성공만 확인이다. |
| SubmitSQLAction | interactive 호출자에게 제출할 최종 SQL | 보정 뒤 SQL과 기존 path_state의 결과 JSON·SQL tag를 일반적으로 모두 동기화하지 않는다. |

계약·예외·테스트는 [SQL 실행 상세](../09-sql-validation/chapter-06-sql-execution-and-result-contract.md), [숫자·정렬 제출 보충](../09-sql-validation/chapter-06-1-numeric-and-order-submission.md)에 있다. 근거: [실행 agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/sql_execution.py), [숫자 helper](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/numeric_types.py), [interactive coordinator](../../../code/auto-ontology/auto_ontology/retrieval/interactive/coordinator.py).

## 24. 빈 결과·전체 NULL과 실행 후 보정

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Empty result | 결과 행이 0개인 상태. 실행 결과 `['[]']` | 값이 0인 한 행·NULL 집계 한 행과 다르다. None은 결과 누락이므로 실제 wrapper 입력 검사에서 거부한다. |
| All-NULL JSONB alias | JSONB 출력 이름에 대응한 모든 관찰 값이 NULL | 정규식 alias·소문자 key로 찾는다. 경로 오류를 의심하는 신호이며 실제 데이터 NULL과 구분하는 증명은 아니다. |
| Essential / non-essential LIKE | 주 대상을 찾는 조건 / 부가 선호 조건 | 모델에게 보수적 분류와 정확 인용을 지시한다. 반환 조건의 SQL 존재·두 목록 교집합을 별도 검사하지 않는다. |
| Targeted value repair | 실제 값 후보·단위 증거를 붙이는 보정 요청 | 현재 SQL의 개별 테이블 probe다. JOIN/WHERE 전체에서 새 행이 나올 보장은 아니다. |
| High cardinality point lookup | 고유값이 많은 컬럼에서 특정 값만 조회 | 빈 결과일 때 equality/IN의 존재·대소문자/공백 변형을 추가 확인한다. 전체 철자 유사 탐색은 아니다. |
| Undiagnosed empty retry | 원인을 못 찾은 빈 결과에서 한 번 새 유도 요청 | 값 보정과 별도 flag다. probe 실패/생략도 같은 지시문에 도달할 수 있다. |
| One-shot guard | 같은 보정의 반복을 막는 시도 표시 | 값·NULL·LIKE·원인 미확인 표시가 각각 있다. generic 표시는 기존 DEBUG/후속 seed 삭제 목록에 없다. |
| Soft acceptance | 이력이 많으면 보조 검사의 invalid를 통과시키기 | 검사 이후 failed_attempts가 5 초과인지 본다. 실제 검사 성공이나 decision 필드 재기록을 뜻하지 않는다. |
| Deterministic SQL fallback | 마지막 의도 거부 SQL을 최종 응답에 넣는 상위 대체 | 두 전체 시도 실패 뒤 조건부 동작한다. 빈 결과의 자동 대체도, 새 실행/JSON 생성도 아니다. |

호출·상태·테스트·미확인은 [빈 결과 보정 상세](../09-sql-validation/chapter-07-empty-result-repair-and-fallback.md)에 있다. 근거: [LIKE/NULL agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/empty_like_result_check.py), [값/generic agent](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/agents/empty_result_value_repair.py), [상위 복원·fallback](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/main.py).

## 25. Chat 요청·사용자 헤더와 이력 준비

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Gateway / identity | 요청을 내부로 넘기는 인증 서버 / 사용자 식별 | Next.js가 사용자·권한을 확인하고 ID 헤더를 만든다. Python은 그 헤더를 독립 인증하지 않는다. |
| Internal user / subject token | 대화 소유권용 사용자 ID / DB 사용자 인증용 원 토큰 | 하나가 다른 하나를 대체하지 않는다. 대화 ID가 있으면 내부 사용자 필수이며 DB token은 연결 설정에 따라 요구된다. |
| Semantic readiness gate | 의미 계층이 존재하는지 확인하는 진입 조건 | semantic Term 하나의 존재를 본다. 선택 DB의 모든 compile 완료 보장은 아니다. |
| Canonical target DB | UUID/이름 요청을 catalog의 정식 이름으로 해석 | 목록 일치 검사다. 활성 연결·사용자 DB 권한·SQL 실행 검사가 아니다. |
| Conversation / stateless | 이력을 저장하는 대화 / 대화 ID 없는 단발 요청 | 무상태도 사용자 ID가 있으면 analytics를 저장할 수 있다. |
| Slot / worker | 진행 중 대화 작업 표식 / 별도 실행 프로세스 | worker 취득·slot 획득 이후 대화 소유권과 저장을 확인한다. 전체 자원 수명은 후속 분석이다. |
| ConversationTurn / history | 완료된 질문·설명·SQL 한 쌍 / 최근 쌍 목록 | 최근 5쌍·12,000자 상한이다. DB 메시지 조회 자체는 전부 읽고 결과/차트는 이력에서 제외한다. |
| Pending question | 아직 맞는 assistant를 만나지 않은 user 메시지 | 다음 user가 오면 교체한다. 별도 turn ID로 응답을 묶는 방식은 아니다. |
| Analytics / idempotency | 사용 통계 / 같은 요청의 중복 저장 방지 | 대화 준비는 질문과 통계를 함께 저장한다. 질문별 중복 요청 ID 검사는 이 함수에 없다. |
| Queue / SSE | 프로세스 간 데이터 통로 / 서버의 연속 이벤트 전송 | route는 ASK tuple을 넣고 스트림을 반환한다. 그 자리에서 SQL을 직접 실행하지 않는다. |

순서·상태·DB 경계·테스트는 [Chat 요청 상세](../10-chat-runtime/chapter-01-request-identity-and-conversation.md)에 있다. 근거: [chat router](../../../code/auto-ontology/auto_ontology/server/chat/router.py), [identity](../../../code/auto-ontology/auto_ontology/server/identity.py), [대화 DAL](../../../code/auto-ontology/auto_ontology/server/chat/conversation_dal.py), [웹 gateway](../../../code/auto-ontology/frontend/app/api/chat/completions/route.ts).

## 26. WarmPool·프로세스·작업 메시지

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| Prewarm / cold start | 요청 전 준비 / 요청 때 초기화 | 서버 시작은 background spawn을 시작한다. 첫 요청 전에 완전 준비됐다는 보장은 아니다. |
| Standby / WarmPool | 빌려줄 대기 worker / 대기 한 칸 재사용 객체 | 대기 한 칸이며 전체 동시 실행 수 제한이 아니다. 대화별 전용 프로세스를 영구 유지하지 않는다. |
| Spawn / daemon | 새 자식 초기화 방식 / 부모 종료 시 생존을 보장하지 않는 속성 | 부모 cache를 그대로 공유하는 방식이 아니다. 실제 OS 신호/정리 완료는 별도 검증이다. |
| Readiness / ready | 초기화 완료 신호 | DB/모델 실행 성공 신호는 아니다. drain은 메시지 한 개만 읽으며 pool이 bool을 검사하지 않는다. |
| ASK tuple | 질문 작업의 위치별 입력 묶음 | 질문·prediction·DB·token·history·evidence 6개다. 자식 unpack은 작업 try 밖이고 request ID는 없다. |
| event / error / done | 중간 결과 / 실패 / 작업 경계 | error에서 부모가 raise하므로 뒤 done이 남을 수 있다. 프로세스 alive와 queue가 깨끗함은 다르다. |
| Follow-up resolution | “그럼 다음 달은?”을 독립 질문으로 바꾸기 | 기존 이력을 모델 입력에 넣는다. 독립 질문은 코드가 원문 유지하고 의미 보존 전체는 모델 지시다. |
| Snapshot / per-user connector | 프로세스가 보관한 연결 목록 / 해당 요청 사용자용 연결 | 기본 목록이 비었을 때 재조회한다. 사용자별 목록은 작업용이며 기본 snapshot을 덮지 않는다. |
| Return / replace / refresh | 재사용 반환 / 강제 교체 / 설정 갱신 | return은 alive를 보고 standby에 넣는다. refresh는 대기 worker만 교체하며 진행 중 전체 목록을 순회하지 않는다. |
| Shutdown / queue cleanup | pool 종료 / 통신 자원 정리 | 현재 standby kill과 전체 활성/생성 중 worker 종료는 다르다. 명시 queue close/join_thread는 worker.py에 없다. |

실제 함수·메시지·테스트·미확인은 [worker 수명 상세](../10-chat-runtime/chapter-02-worker-pool-and-queues.md)에 있다. 근거: [worker.py](../../../code/auto-ontology/auto_ontology/server/chat/worker.py), [후속 질문 resolver](../../../code/auto-ontology/auto_ontology/retrieval/text_to_sql/follow_up.py), [연결 service](../../../code/auto-ontology/auto_ontology/server/connections/service.py).

## 27. Slot 관찰·연결 해제·취소와 스트림 종료

| 용어 | 쉬운 뜻과 예시 | 코드에서 구분할 경계 |
|---|---|---|
| client_alive | 원래 completions 연결의 생존 표시 | watch 소비자 수가 아니다. watch가 붙어 있어도 원래 연결이 끊겼으면 새 질문이 선점할 수 있다. |
| Claim / preempt | 대화 실행 자리 획득 / 기존 작업 선점 | 같은 key의 alive가 True면 409다. 사전/lock은 Python 프로세스 내부이며 서버 전체 공통 잠금이 아니다. |
| Replay buffer / tail | 누적 이벤트 목록 / 이후 새 이벤트 읽기 | 소비자마다 index=0부터 재생한다. 완료 release 뒤 새 watch에는 buffer를 제공하지 않는다. |
| Heartbeat / DONE | 연결 유지용 ping / 스트림 종료 문자열 | ping은 소비자마다 만들고 저장하지 않는다. result 자체는 종료가 아니며 차트가 뒤따를 수 있다. |
| Watch / reconnect | 진행 중 작업 관찰 재접속 | 실행 복원·새 worker 시작이 아니다. slot 없음은 DONE만 반환하며 완료/다른 서버/idle을 구분하지 않는다. |
| Disconnect / cancel | 연결만 끊김 / 실행 취소 요청 | watchdog은 alive만 clear한다. cancel은 worker 교체를 요청하지만 이미 시작한 부모 저장/차트는 별도다. |
| Tee / drain | 스트림 둘로 나누기 / 한 갈래 끝까지 읽기 | 웹 completions의 after drain 때문에 브라우저 이탈과 Python 연결 단절이 일치하지 않을 수 있다. |
| released / finished | pool 반환 시작 표시 / pump 종료 표시 | 별도 상태다. released check/set은 단일 lock으로 묶지 않았으며 동시 호출 보장은 미검증이다. |
| AbortController / Stop | 브라우저 요청 중지 객체 / 별도 cancel도 보내는 UI 동작 | local abort만으로 원격 종료를 확인하지 않는다. cancel helper도 응답 bool/status를 검사하지 않는다. |

코드·순서·검사 경계는 [스트림·취소 상세](../10-chat-runtime/chapter-03-slots-streaming-and-cancellation.md)에 있다. 근거: [router](../../../code/auto-ontology/auto_ontology/server/chat/router.py), [웹 API 소비자](../../../code/auto-ontology/frontend/api/chat.ts), [UI 상태](../../../code/auto-ontology/frontend/lib/useChat.ts).

## 28. 답변·결과 메시지와 통계 저장

| 용어 | 쉬운 뜻 | 코드 경계 |
|---|---|---|
| Message 1 / Message 2 | 설명·SQL / 차트 또는 결과 표 | 별도 assistant 행·별도 transaction이다. 공통 turn ID가 없다. |
| persisted | pump의 첫 답변 저장 완료 표시 | DB 함수 정상 반환 기준이며 analytics 영향 행 수는 확인하지 않는다. |
| last_sql | 마지막 스트리밍 SQL | 성공 실행 SQL 보장이 아니다. 저장에만 대체 사용하므로 live event와 다를 수 있다. |
| Partial persistence | 일부 메시지만 저장된 상태 | 질문·답변·결과는 요청 전체로 함께 commit하지 않는다. |
| Analytics / readback | 사용 통계 / 저장 데이터 재조회 | 통계에는 conversation_id·status·결과 행이 없다. 대화 삭제와 통계 삭제는 별개다. |
| Cascade / transaction | 부모 삭제에 따른 자식 삭제 / 함께 확정하는 DB 변경 | schema의 대화→메시지 cascade와 각 저장 함수의 transaction 범위를 구분한다. |

필드·쿼리·실패·UI 차이는 [저장 상세](../10-chat-runtime/chapter-04-conversation-results-and-analytics.md)에 있다. 근거: [대화 DAL](../../../code/auto-ontology/auto_ontology/server/chat/conversation_dal.py), [결과 helper](../../../code/auto-ontology/auto_ontology/server/chat/helpers.py).
