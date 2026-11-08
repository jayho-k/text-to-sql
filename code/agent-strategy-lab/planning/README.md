# Planning

- 상태: 역할과 디렉터리만 준비됨. 실행 가능한 구현 없음.
- 역할: 계획·행동 순서·조건을 생성하고 실제 실행 결과와 연결하는 방법.
- 설계 원칙: 계획 생성의 효과와 별도 실행 제어의 효과를 구분한다.
- 사용법: 아래 방법의 README에서 입력·출력과 검증 목표를 확인한다.
- [프로젝트](../README.md), [용어집](../../../text/agent-strategy-lab/01-design/chapter-00-glossary.md).

| 방법 | 구현 범주 |
|---|---|
| [Plan-and-Solve](plan_and_solve/README.md) | A: 프롬프트 중심 |
| [ReAct](react/README.md) | B: 프롬프트 + 실행 코드 |
| [LLMCompiler](llm_compiler/README.md) | C: 프롬프트 + 실행 아키텍처 |

분류 A는 단일 호출 프롬프트, B는 호출·검색 등 실행 코드, C는 상태·의존성 등 실행 아키텍처, D는 평가 기반 최적화·학습 구성을 뜻한다. 이는 프로젝트의 구현 책임 분류이며 논문 성능 순위가 아니다.
