# Agent Strategy Lab

- 준비일: 2026-11-08.
- 상태: **디렉터리와 역할 문서만 준비됨. 실행 가능한 구현·프롬프트・테스트·설정·패키지 정의는 없음.**
- 목적: planning(실행 순서·조건 결정), decomposition(하위 문제 분해), rewriting(표현 변환)을 직접 구현하고 같은 조건에서 비교한다.
- 사용법: 분야 README → 방법 README 순서로 범위와 검증 목표를 확인한다. 현재 실행 명령은 없다.
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

각 방법의 내부에는 `prompts/`, `examples/`, `tests/unit/`, `tests/live/`만 마련했다. 빈 폴더의 `.gitkeep`은 Git에서 디렉터리를 보존하는 파일이다.

알고리즘은 방법별로 소유한다. 공통 계층에는 호출·도구·결과 기록을 두며, 재계획·분해·재작성 정책을 미리 한 인터페이스로 강제하지 않는다. LLMCompiler처럼 여러 분야에 걸치는 방법은 한 곳에 구현하고 조합 실험에서 재사용한다.

향후 구현 파일 후보는 방법별 `strategy.py`·`contracts.py`, 공통 `model_client.py`, 평가 `runner.py`다. 이번에는 생성하지 않았다. SDK 버전·모델·검색기·의존성이 확인되지 않아 `pyproject.toml`과 `config.yaml`도 생성하지 않았다. 의존성 설치·실제 모델 호출은 수행하지 않았다.
