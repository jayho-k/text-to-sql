# Agent Strategy Lab 문서

> **확장형 경쟁군 갱신(2026-11-15):** [MuGI·QA-Expand/AMD·CSQE·LameR 비교](../../.codex/research/planning-decomposition-rewriting/26_expansion_competitor_comparison.md)·[QueryGym 후속 chapter](../querygym/01-reformulation/chapter-02-feedback-and-expansion.md)를 작성했다. 네 방법을 우선 비교로 변경해 현재 처분은 우선45·추가근거22·목적별15·근거자료43이다. E01 선택 45조건/90지표의 수치/질의 대응을 확인했으나 독립 실행 재현은 아니다. 현재 PDF72·조건 부분 정규화23개이며 아래 71/19 기록은 직전 단계다. 다음은 planning/decomposition 명세 갱신이다.

> **학습형 재작성 대조(2026-11-15):** [RQR](../tongsearch-qr/README.md)·[QueryGym](../querygym/README.md)의 선택 코드를 고정해 분석하고, [RL-QR/Q-PRM 포함 비교](../../.codex/research/planning-decomposition-rewriting/25_learned_rewriting_code_and_contracts.md)와 [재작성 명세](../../.codex/plan/agent-strategy-lab/01-4_rewriting.md)를 갱신했다. 보상/검색 지표·질의 결합·정리 버전·cache·분모를 구분한다. 실행 검증·최종 채택은 미완료다.

> **공식 코드 대조:** [QLASS](../qlass/README.md), [ARMAP](../armap/README.md), [비교 결론](../../.codex/research/planning-decomposition-rewriting/24_official_selection_code_audit.md). 학습 라벨·실제 종료 피드백·환경 replay·후보/시도 예산·집계를 정적으로 확인해 평가 계약을 갱신했다. 외부 코드 확보/분석이며 자체 구현 확장·실행 검증은 하지 않았다.

> **2026-11-15 현재:** [전체 후보 처분표](../../.codex/research/planning-decomposition-rewriting/22_candidate_decisions.md), [잠정 개발 순서](../../.codex/research/planning-decomposition-rewriting/23_provisional_development_order.md), [평가/선택 계약](../../.codex/plan/agent-strategy-lab/01-5_evaluation_and_integration.md). 출처 125개·PDF 71개, 세부 조건 일부 정규화 19개다. 첫 처분·명세 초안이며 최종 채택·실측·전체 정독 완료가 아니다. 아래 수집 합계는 이전 단계다.

> **현재 목표·활성 계획:** [전체 계획](../../.codex/plan/agent-strategy-lab/01_plan.md), [목표 정렬·후보 결정](../../.codex/plan/agent-strategy-lab/01-11_goal_alignment_and_decision_plan.md). 최종 목표는 성능 근거로 방법·조합을 선정해 구현하고 실제 모델 비교로 개선하는 것이다. 현재는 연구에서 후보별 결정·개발 명세로 수렴하는 단계다. 모델 호출·구현 확장은 보류한다.

> **현재 연구 결과:** [방법·성능·반례](../../.codex/research/planning-decomposition-rewriting/19_rewriting_formal_planning_memory_evidence.md), [개발 판단·비교 설계](../../.codex/research/planning-decomposition-rewriting/20_evidence_to_development_decisions.md). 출처 ID 121개·PDF 67개는 정독·최종 선정 수가 아니다. 초기 코드와 테스트 정의는 존재하지만 동작·성능·논문 재현은 미검증이다. 아래 82+18개·15편 등의 기록은 이전 진행 단계다.

> **성능 중심 후보 재평가 진행:** [survey·경쟁군 누락 대조](../../.codex/research/planning-decomposition-rewriting/16_survey_competitor_coverage_audit.md), [학습·탐색·세계 모델의 원문 성능 근거](../../.codex/research/planning-decomposition-rewriting/17_training_search_world_model_evidence.md). 기존 82개 출처에 원출처 18개를 추가 연결했다. 편수·난이도로 최종 후보를 제한하지 않으며 모델 테스트는 보류 중이다.

> **기존 분석 갱신:** [현재 사용 구조와 개발 판단](../../.codex/research/planning-decomposition-rewriting/13_current_usage_and_development_revision.md), [15편 원문·분석 색인](../../.codex/research/planning-decomposition-rewriting/papers/README.md). 기존 11편별 현재 역할을 보강하고 후속 네 편의 방법·주요 결과·선택 부록을 추가했다. 자체 코드의 동작·성능 검증이나 후속 저자 코드 감사가 완료됐다는 뜻은 아니다.

> **현재 우선 작업:** [방법론 변화와 현재 사용 구조](../../.codex/research/planning-decomposition-rewriting/12_current_methodology_evolution.md). 초기 실행 코드는 작성했으나 실제 모델 호출은 HTTP 502로 실패했다. 사용자 요청에 따라 테스트·구현 확장을 보류하고 최근 연구와 공식 구현의 구조 분석을 우선한다. 아래 준비 상태는 최초 문서 작성 당시 기록이다.

> **2026-11-14 주요 11편 1차 분석:** [원문·분석 색인](../../.codex/research/planning-decomposition-rewriting/papers/README.md), [종합 개발 방향](../../.codex/research/planning-decomposition-rewriting/11_paper_grounded_development_direction.md), [최소 실험 명세](../../.codex/plan/agent-strategy-lab/01-7_minimal_experiment_spec.md). 외부 저자 코드의 오프라인 경계 검사와 자체 전략 구현·성능 재현은 구분한다. 아래 준비 상태는 자체 실행 코드 기준이다.

- 준비일: 2026-11-08.
- 상태: 연구·개발 판단 문서와 초기 코드가 있다. 실제 동작을 검증한 코드 분석·성능 결과는 미완료다.
- [코드 프로젝트](../../code/agent-strategy-lab/README.md), [전체 계획](../../.codex/plan/agent-strategy-lab/01_plan.md), [기존 조사](../../.codex/research/planning-decomposition-rewriting/10_prompt_code_architecture_classification.md).

| 문서 디렉터리 | 역할 |
|---|---|
| [01-design](01-design/README.md) | 승인 구조·용어·구현 경계 |
| [02-planning](02-planning/README.md) | planning 코드의 동작·상태·검증 근거 |
| [03-decomposition](03-decomposition/README.md) | 분해·의존성·합성과 실패 경로 |
| [04-rewriting](04-rewriting/README.md) | 재작성·검색 연결·의미 보존 |
| [05-evaluation](05-evaluation/README.md) | 비교 조건·평가·Deep Agents 연결·실행 결과 |

후속 코드 분석은 주제별 chapter Markdown으로 작성한다. 역할·목적·사용법·Mermaid 흐름도, 함수 호출·입출력·상태·분기·실패·재시도·저장/조회 경계·관련 테스트를 실제 파일 경로와 연결한다. 아직 없는 코드의 동작을 확인 사실로 서술하지 않는다. 설치·배포 가이드는 작성 범위에서 제외한다.

새 외부 조사는 기존 `.codex/research/planning-decomposition-rewriting/` 주제 폴더를 재사용하고 URL·조사일·확인 수준을 기록한다. [용어집](01-design/chapter-00-glossary.md)을 공통 참조한다.
