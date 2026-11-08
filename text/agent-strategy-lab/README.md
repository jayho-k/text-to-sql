# Agent Strategy Lab 문서

- 준비일: 2026-11-08.
- 상태: 디렉터리 준비 문서만 있으며 구현 코드 분석·성능 결과는 없다.
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
