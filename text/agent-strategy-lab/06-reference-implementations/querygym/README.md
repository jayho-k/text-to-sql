# QueryGym 공식 코드 분석

조사일 **2026-11-15**. E01 [재현 비교 연구 v1](https://arxiv.org/abs/2604.27421v1)이 연결한 [공식 저장소](https://github.com/ls3-lab/QueryGym)를 `code/reference-implementations/querygym/`에 확보했다. 커밋 `c6df804d1a3ac22d9774f17bb55be289cfbd8342`의 선택 경로만 분석한다. 현재 HEAD·저장 결과·논문 표는 동일한 버전이라고 가정하지 않는다.

- [용어집](01-reformulation/chapter-00-glossary.md)
- [방법 변형과 평가 자료의 경계](01-reformulation/chapter-01-variants-and-evaluation.md)
- [다중 생성·질문 분해·검색 문서 피드백](01-reformulation/chapter-02-feedback-and-expansion.md)
- [경쟁군 성능·E01 대응](../../.codex/research/planning-decomposition-rewriting/26_expansion_competitor_comparison.md)
- [계획](../../.codex/plan/querygym/01_plan.md) · [선택 소스 manifest](../../.codex/research/planning-decomposition-rewriting/official_rewriting_code_manifest.json)

모델·검색·테스트 실행·논문 수치 재현·전체 run 파일 감사는 하지 않았다. 설치·배포 안내는 범위 밖이다.
