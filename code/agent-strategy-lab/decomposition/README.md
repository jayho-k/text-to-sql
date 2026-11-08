# Decomposition

- 상태: 역할과 디렉터리만 준비됨. 실행 가능한 구현 없음.
- 역할: 하위 문제·의존성·결과 합성을 직접 구현하는 방법.
- 설계 원칙: 분해 내용과 분해 실행·합성의 성공을 분리해 평가한다.
- 사용법: 아래 방법의 README에서 입력·출력과 검증 목표를 확인한다.
- [프로젝트](../README.md), [용어집](../../../text/agent-strategy-lab/01-design/chapter-00-glossary.md).

| 방법 | 구현 범주 |
|---|---|
| [Least-to-Most](least_to_most/README.md) | B: 프롬프트 + 실행 코드 |
| [Decomposed Prompting](decomposed_prompting/README.md) | B / C: 모듈 호출과 분해 실행 구조 |
| [ADaPT](adapt/README.md) | C: 프롬프트 + 실행 아키텍처 |

분류 A는 단일 호출 프롬프트, B는 호출·검색 등 실행 코드, C는 상태·의존성 등 실행 아키텍처, D는 평가 기반 최적화·학습 구성을 뜻한다. 이는 프로젝트의 구현 책임 분류이며 논문 성능 순위가 아니다.
