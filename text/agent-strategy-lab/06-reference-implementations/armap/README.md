# ARMAP 공식 코드 분석

분석일 **2026-11-15**. [공식 페이지](https://armap-agent.github.io/)가 연결한 [저장소](https://github.com/heaplax/ARMAP)를 커밋 `411ad9dd7baaa6f66d31e416cd100214447bd5f3`로 고정했다. `code/reference-implementations/armap/`와 `text/agent-strategy-lab/06-reference-implementations/armap/`를 대응시킨다. [계획](../../.codex/plan/armap/01_plan.md), [선택 소스 해시](../../.codex/research/planning-decomposition-rewriting/official_selection_code_manifest.json).

- [용어](01-core/chapter-00-glossary.md)
- [쌍별 보상 학습과 점수 응답](01-core/chapter-01-reward-learning.md)
- [Best-of-N·MCTS와 결과 집계](02-selection/chapter-02-search-and-evaluation.md)

RM과 Eval의 필요한 소스를 확보해 학습 목적·점수 서비스·WebShop과 ScienceWorld의 선택·WebShop MCTS 일부를 정적으로 추적했다. 전체 데이터 생성·모든 과업·Reflexion·모델/환경 실행·성능 재현은 미완료다. 외부 소스는 수정하지 않았고 설치·배포 가이드는 작성하지 않는다.

[QLASS와의 비교·개발 계약 변경](../../.codex/research/planning-decomposition-rewriting/24_official_selection_code_audit.md)을 함께 본다. 공개 코드의 스크립트·점수·집계를 논문 표와 일대일로 연결한 것은 아니다.
