# Agent Strategy Lab

> **2026-11-14 현재 상태:** 실제 `ChatOpenAI` 클라이언트, 직접 답변·PS·LtM·RaR의 초기 전략, 평가 실행기·라이브 테스트·의존성 잠금을 작성했다. 이전 실제 호출은 HTTP 502로 실패하여 동작·성능은 미검증이다. 현재는 [전체 계획](../../.codex/plan/agent-strategy-lab/01_plan.md)과 [후보 결정 계획](../../.codex/plan/agent-strategy-lab/01-11_goal_alignment_and_decision_plan.md)에 따라 성능 근거를 개발 후보·명세로 연결한다. 모델 호출·구현 확장은 보류 중이며 이번 계획 점검에서는 실행하지 않았다.

- 준비일: 2026-11-08.
- 상태: 초기 코드·프롬프트·실제 호출 테스트 정의·패키지와 의존성 잠금 존재. 실행 성공과 성능은 미검증.
- 목적: planning(실행 순서·조건 결정), decomposition(하위 문제 분해), rewriting(표현 변환)을 직접 구현하고 같은 조건에서 비교한다.
- 사용법: 전체 계획 → 후보 결정 계획 → 분야/방법 README 순서로 확인한다. 현재 연구·선정 단계에서 라이브 실행을 재개하지 않는다.
- [전체 계획](../../.codex/plan/agent-strategy-lab/01_plan.md), [문서 색인](../../text/agent-strategy-lab/README.md), [용어집](../../text/agent-strategy-lab/01-design/chapter-00-glossary.md), [기존 구현 분류 조사](../../.codex/research/planning-decomposition-rewriting/10_prompt_code_architecture_classification.md).

| 경로 | 책임 |
|---|---|
| [planning/](planning/README.md) | 계획·행동 선택과 실행 순서 |
| [decomposition/](decomposition/README.md) | 하위 문제 생성·의존성·합성 |
| [rewriting/](rewriting/README.md) | 질문 재구성·검색 질의 변환 |
| [optimization/](optimization/README.md) | 평가에 의한 프롬프트 개선 |
| [shared/](shared/README.md) | 모델 호출·기록·공통 도구·공통 데이터 계약 |
| [integrations/deepagents/](integrations/deepagents/README.md) | 직접 구현한 방법과 Deep Agents 실행 흐름의 연결 |
| [experiments/](experiments/README.md) | 기준선·개별 비교·조합 실험 |
| [evaluation/](evaluation/README.md) | 평가 데이터·판정기·동일 조건 실행 |
| [results/](results/README.md) | 실행별 설정·버전·결과·실패·비용·시간 |

방법별로 `prompts/`, `examples/`, `tests/unit/`, `tests/live/` 경로를 준비했고, 일부 방법에는 초기 `strategy.py`가 있다. 빈 폴더의 `.gitkeep`은 Git에서 디렉터리를 보존하는 파일이다. 폴더·파일 존재를 논문 재현 완료로 해석하지 않는다.

알고리즘은 방법별로 소유한다. 공통 계층에는 호출·도구·결과 기록을 두며, 재계획·분해·재작성 정책을 미리 한 인터페이스로 강제하지 않는다. LLMCompiler처럼 여러 분야에 걸치는 방법은 한 곳에 구현하고 조합 실험에서 재사용한다.

현재 초기 코드의 근거는 [모델 클라이언트](shared/model_client.py), [평가 실행기](evaluation/runner.py), [실모델 테스트 정의](evaluation/tests/test_live.py), [패키지 정의](pyproject.toml)다. 방법 선정 뒤 학습·검색·검증·상태 처리의 상세 명세를 갱신한다. SDK·검색기·과업별 요구사항 중 확인하지 않은 것은 명세에 별도로 표시한다.
