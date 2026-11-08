# Auto-Ontology 코드 분석

제공된 `code/auto-ontology/`를 분석해 기능, 사용 방법, 컴포넌트 역할과 워크플로를 기록한다.

## 읽는 순서

1. [용어와 예시](01-architecture/chapter-00-glossary.md): PII 등 약어와 프로젝트 고유 개념을 찾아볼 때 사용한다. 각 본문에도 필요한 뜻을 함께 설명한다.
2. [전체 아키텍처와 주요 컴포넌트](01-architecture/chapter-01-overview.md)
3. [모듈과 기능 책임 지도](01-architecture/chapter-02-component-map.md)
4. [수집·컴파일·질의의 실제 호출과 상태](01-architecture/chapter-03-runtime-traces.md)
   - 보충: [메달리온과의 책임 경계](01-architecture/chapter-04-medallion-boundary.md). 원본 데이터와 메타데이터 저장·SQL 실행·교차 DB 경계를 확인한다.
5. [Catalog 엔티티와 식별자](02-data-model/chapter-01-catalog-entities.md): 저장 필드·계층·기존 ID 재사용·재수집·삭제·조회 경계를 분석한다.
6. [의미 계층의 객체·관계와 수정·인증](02-data-model/chapter-02-semantic-entities.md): Term·속성의 연결, 자동 생성과 수정·인증, 보존·삭제 경계를 분석한다.
7. [SQL·분석 정의의 저장과 재사용](02-data-model/chapter-03-sql-and-analysis-definitions.md): 중복 기준·참조 연결·CustomAnalysis·PqlAnalysis·생산자와 검색·삭제를 분석한다.
8. [저장소·연결 수명·트랜잭션 경계](02-data-model/chapter-04-storage-boundaries.md): catalog·vector·대화의 별도 연결과 부분 실패·reset·설정·종료를 분석한다.
9. [SQLDatabase 공통 계약과 수집·질의 연결](03-connectors/chapter-01-common-contract.md): 메타데이터 반환·추출 검사·이름 한정·timeout·연결 수명을 분석한다.
10. [Registry의 연결 선택·수집 범위·캐시 갱신](03-connectors/chapter-02-registry-and-cache.md): 저장·환경 연결의 우선순위, 필터 전달, 프로세스별 캐시와 변경·실패 경계를 분석한다.
11. [Postgres·MySQL의 메타데이터 추출](03-connectors/chapter-03-postgres-and-mysql-extraction.md): 조회 범위·권한·view·타입·키·SQL 활동과 정규화·실패 경계를 분석한다.
12. [SQLite·DuckDB의 메타데이터 추출](03-connectors/chapter-04-sqlite-and-duckdb-extraction.md): PRAGMA 반복 조회·필드 기본값·키 미수집·CSV SQL 예시와 완전성의 한계를 분석한다.
13. [Databricks의 schema별 추출과 부분 실패](03-connectors/chapter-05-databricks-extraction.md): 단일·다중 schema의 경로·정보 차이, describe cache·키 파싱·오류 분류를 분석한다.
14. [ClickHouse의 HTTP 메타데이터 추출과 키의 의미](03-connectors/chapter-06-clickhouse-extraction.md): 메타데이터 행 제한 해제·타입 기반 nullable·view fallback·인덱스 키·SQL 이력 오류를 분석한다.
15. [실행 DB 선택과 Chat SQL의 결과·오류 경계](03-connectors/chapter-10-sql-execution-boundary.md): DB 라우팅·timeout·결과 JSON·숫자 교정·오류 분류와 후속 보정을 분석한다.
16. [엔진별 SQL 실행·시간제한·연결 수명](03-connectors/chapter-11-execution-timeout-and-resources.md): 6개 엔진의 제한 범위·parameter·결과·취소·연결 재사용·종료와 테스트 한계를 분석한다.
17. [연결 비밀 정보와 사용자별 인증](03-connectors/chapter-12-secrets-and-user-auth.md): Vault·catalog 저장, 로그인/DB token 분리·교환·cache·오류·정리의 경계를 분석한다.
18. [Catalog 수집의 시작·예약·즉시 요청](04-catalog-ingestion/chapter-01-ingestion-scheduling-and-triggers.md): scheduler 상태·주기·단일 DB thread·동시 실행·상태/이력의 보장 범위를 분석한다.
19. [추출·정규화에서 catalog 저장 입력까지](04-catalog-ingestion/chapter-02-extraction-to-catalog-write.md): 여섯 표의 변환·기존 ID 결합·schema 분리·저장 순서·빈 입력·부분 실패와 반환 표를 분석한다.
20. [기존 catalog와 구조 비교·갱신·삭제](04-catalog-ingestion/chapter-03-catalog-diff-and-relations.md): 이름·ID·table 집합·column merge·변경 감지·설명 보존·범위 축소와 cascade·PII·의미 객체의 생존 경계를 분석한다.
21. [PK·FK 갱신과 SQL 이력의 저장·중복·실패](04-catalog-ingestion/chapter-03-1-keys-and-query-history.md): 키 reset·순서·last_seen, SQL 문법 분석·중복·관측 횟수·참조·연결별 저장과 고아 SQL 정리를 분석한다.
22. [검색용 텍스트·embedding 생성과 vector 교체](04-catalog-ingestion/chapter-04-embedding-and-vector-refresh.md): 입력 텍스트·ID·3종 batch·모델 요청·재시도·첫 유효 결과의 reset·append·부분 실패와 완료 로그를 분석한다.
23. [reset·보강·부분 실패와 복구의 경계](04-catalog-ingestion/chapter-05-reset-and-partial-failure.md): 중단·대기·삭제·재구성, 공유/사용자 객체·vector·연결·이력과 PII·규칙 재적용의 실패를 분석한다.
24. [의미 컴파일의 대상 선택·병렬 분석·저장 순서](05-semantic-compilation/chapter-01-compilation-targets-and-orchestration.md): Term 없는 대상·context·domain, worker·LLM 제한·저장 slot·count·부분 실패·취소를 분석한다.
25. [원본 표본 조회·분포 계산·저장과 실패](05-semantic-compilation/chapter-02-sampling-and-profiling.md): LIMIT·timeout·타입·고유성·DISTINCT·반환/저장 차이·breaker·소비자 입력을 분석한다.
26. [날짜 형식·혼합 경고와 JSON 표본 표현](05-semantic-compilation/chapter-02-1-date-formats-and-json-samples.md): 날짜 후보·모호성·자리수, JSON 경로·단위·예시·길이 제한과 저장/embedding 차이를 분석한다.
27. [테이블 역할·키 제안과 의미 속성 명세](05-semantic-compilation/chapter-03-table-roles-and-attribute-specs.md): PK 전달·FK 후보/보정·junction·설명 생성·명세 필드·모델 입력과 실패를 분석한다.
28. [Term 추출·컬럼 할당·응답 보정](05-semantic-compilation/chapter-04-term-assignment-and-persistence.md): 40개 입력·전체 후보 보충·label·중복·fallback·별칭·표시 이름을 분석한다.
29. [Term 이름 충돌·속성 식별과 실제 저장](05-semantic-compilation/chapter-04-1-term-and-attribute-writes.md): 이름과 소유·ID·5필드 key·설명/인증·transaction·부분 저장을 분석한다.
30. [의미 embedding·후속 단계와 실패 경계](05-semantic-compilation/chapter-05-semantic-embedding-and-failure-boundaries.md): 실제 재조회·텍스트·metadata·inline/bulk·append·타입 누락·0벡터·후속 단계·복구 한계를 분석한다.
31. [관계 종류·후보와 선언 FK 직접 연결](06-semantic-relationships/chapter-01-declared-and-semantic-foreign-keys.md): 소유/참조/관측 관계·미연결 조건·target 속성·자기 참조·DB 경계·중복·부분 실패·추론 인계를 분석한다.
32. [벡터 후보·모델 선택과 표본 SQL 검사](06-semantic-relationships/chapter-02-vector-candidates-and-reference-validation.md): 두 검색·고유성 필터 전달·중복·ID 검증·동명 표본 검사·실제 timeout·저장 거부와 재시도 경계를 분석한다.
33. [관계 정리·JOIN 기본 선택과 경로 소비](06-semantic-relationships/chapter-03-relationship-pruning-and-join-selection.md): 값 겹침·삭제/보존·그룹·모델/이름순 선택·transaction·PK 방향·BFS·검색/SQL 소비를 분석한다.
34. [이력 SQL의 표현식 추출·속성 제안](06-semantic-relationships/chapter-04-query-history-sql-attributes.md): Term/SQL 범위·출력 제외·추출 범주·0점 순위·top 10·모델 지시·원문 매칭·실행별 중복 예약을 분석한다.
35. [SQL 완성·검증·저장과 검색 반영](06-semantic-relationships/chapter-04-1-sql-construction-and-persistence.md): SELECT/JOIN 재구성·조건 손실·스키마·충돌·정적 검증 한계·원본 출처와 저장 SQL·부분 저장·임베딩·복구를 분석한다.
36. [Bridge·junction 분류와 JOIN 패턴 속성](06-semantic-relationships/chapter-05-bridge-and-junction-sql-attributes.md): 구조 후보·payload 차이·flag 선저장·target Term·재정렬·모델 SQL·부분 실패·검색 필터 생략을 분석한다.
37. 검색·후보 선택 → SQL 생성·검증 → chat → 관리 기능·외부 인터페이스·예측 순으로 상세 분석한다.

설치·배포 안내는 제외한다. Snowflake·Trino·Kyuubi·HeavyDB 상세 분석은 사용자 요청으로 건너뛴다. 예정 Chapter 07~09는 제외하고 공통 실행 문서를 Chapter 10부터 이어간다. 각 기능은 파일·함수, 데이터 구조, 상태 변화, 실패·재시도, Mermaid와 관련 테스트까지 추적한다.

## 진행 관리

- [전체 분석 계획](../../.codex/plan/auto-ontology/01_plan.md)
- [아키텍처 세부 계획](../../.codex/plan/auto-ontology/01-1_architecture.md)
- [데이터 모델 세부 계획](../../.codex/plan/auto-ontology/01-2_data-model.md)
- [Connector 세부 계획](../../.codex/plan/auto-ontology/01-3_connectors.md)
- [기본 4개 엔진 추출 계획](../../.codex/plan/auto-ontology/01-3-1_core-engine-extraction.md)
- [Databricks 추출 기록·Snowflake 제외](../../.codex/plan/auto-ontology/01-3-2_warehouse-extraction.md)
- [ClickHouse 추출 기록·나머지 엔진 제외](../../.codex/plan/auto-ontology/01-3-3_remaining-engine-extraction.md)
- [공통 SQL 실행·시간제한·자원·인증 계획](../../.codex/plan/auto-ontology/01-3-4_sql-execution-and-lifecycle.md)
- [Catalog 수집·diff·embedding·실패 분석 계획](../../.codex/plan/auto-ontology/01-4_catalog-ingestion.md)
- [Catalog 구조 diff·키·SQL 이력 상세 계획](../../.codex/plan/auto-ontology/01-4-1_catalog-diff-details.md)
- [의미 컴파일 상세 계획](../../.codex/plan/auto-ontology/01-5_semantic-compilation.md)
- [표본·날짜·JSON 상세 계획](../../.codex/plan/auto-ontology/01-5-1_profiling-details.md)
- [Term 추출·할당·저장 상세 계획](../../.codex/plan/auto-ontology/01-5-2_term-extraction-and-writes.md)
- [의미 관계·SQL 속성·bridge 상세 계획](../../.codex/plan/auto-ontology/01-6_semantic-relationships.md)
- [이력 SQL 속성 제안·완성·저장 상세 계획](../../.codex/plan/auto-ontology/01-6-1_query-history-sql-attributes.md)
- [검색·후보 선택·SQL 문맥 상세 계획](../../.codex/plan/auto-ontology/01-7_retrieval.md)
- 문서는 주제별 폴더에 chapter별로 작성하며, Mermaid 흐름도와 코드 근거를 포함한다.
- 현재 문서는 정적 코드 분석 결과다. 실제 서비스 실행 결과와 구분한다.
