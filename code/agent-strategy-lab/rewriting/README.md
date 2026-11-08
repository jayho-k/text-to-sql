# Rewriting

- 상태: 역할과 디렉터리만 준비됨. 실행 가능한 구현 없음.
- 역할: 질문 재구성과 검색 목적의 질의 변환 방법.
- 설계 원칙: 원문 보존·의미 손상·검색 품질·최종 답을 함께 비교한다.
- 사용법: 아래 방법의 README에서 입력·출력과 검증 목표를 확인한다.
- [프로젝트](../README.md), [용어집](../../../text/agent-strategy-lab/01-design/chapter-00-glossary.md).

| 방법 | 구현 범주 |
|---|---|
| [Rephrase and Respond](rephrase_and_respond/README.md) | A: 단일 호출 / B: 별도 재작성·응답 호출 |
| [Query2doc](query2doc/README.md) | B: 생성 프롬프트 + 검색 연결 |
| [HyDE](hyde/README.md) | B: 생성 프롬프트 + 임베딩·검색 연결 |
| [Multi-query](multi_query/README.md) | B: 프롬프트 + 복수 검색·결과 통합 |

분류 A는 단일 호출 프롬프트, B는 호출·검색 등 실행 코드, C는 상태·의존성 등 실행 아키텍처, D는 평가 기반 최적화·학습 구성을 뜻한다. 이는 프로젝트의 구현 책임 분류이며 논문 성능 순위가 아니다.
