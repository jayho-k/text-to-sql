# 질문 재구성·질의 확장·벡터 검색·원문 보존

- 상태: 자체 RaR 초기 코드 존재·실제 동작 미검증. 외부 RQR/QueryGym 선택 소스 분석과 재작성 명세를 작성했다. 구현 확장·실모델 실행은 보류한다.
- 역할: 답변용 명료화와 검색 질의 재작성·확장, 학습 보상·과정 선택을 구분한다.
- [재작성 개발 명세](../../../.codex/plan/agent-strategy-lab/01-4_rewriting.md), [공식 코드 대조](../../../.codex/research/planning-decomposition-rewriting/25_learned_rewriting_code_and_contracts.md).
- [확장형 경쟁군 성능·반례·버전 대조](../../../.codex/research/planning-decomposition-rewriting/26_expansion_competitor_comparison.md): 네 방법을 우선 비교로 변경했고 E01 선택 45조건/90지표·TSV를 연결했다. 모델/검색 실행은 하지 않았다.
- 코드별 chapter: [TongSearch-QR](../../tongsearch-qr/README.md), [QueryGym](../../querygym/README.md). 공식 원본은 각각 같은 이름의 `code/` 폴더에 대응한다.
- [문서 색인](../README.md), [용어집](../01-design/chapter-00-glossary.md).
