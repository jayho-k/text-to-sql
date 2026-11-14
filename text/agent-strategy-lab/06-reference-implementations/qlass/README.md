# QLASS 공식 코드 분석

분석일 **2026-11-15**. [공식 저장소](https://github.com/Rafa-zy/QLASS), 고정 커밋 `6f2cdf49f7f030c6604e9678d9db8ac4abe00fee`. 코드와 문서는 `code/reference-implementations/qlass/`·`text/agent-strategy-lab/06-reference-implementations/qlass/`로 대응한다. [계획](../../.codex/plan/qlass/01_plan.md), [소스 해시·확보 범위](../../.codex/research/planning-decomposition-rewriting/official_selection_code_manifest.json).

- [용어와 범위](01-core/chapter-00-glossary.md)
- [탐색 기록에서 QNet 학습까지](01-core/chapter-01-learning.md)
- [후보 실행·선택·집계와 재현 경계](02-selection/chapter-02-inference-and-evaluation.md)

필요한 경로만 sparse checkout으로 확보했다. Q값 데이터 구성·학습·선택·ALFWorld 일부 경로를 정적으로 읽었고, 저장소 전체·다른 환경·학습/모델 실행·성능 재현은 확인하지 않았다. 외부 소스는 수정하지 않았다. 공개 진입점과 게시 모델 모듈의 경로 불일치가 있어 함수 분석을 실행 성공으로 해석하지 않는다.

설치·배포 가이드는 범위 밖이다. [종합 개발 판단](../../.codex/research/planning-decomposition-rewriting/24_official_selection_code_audit.md)과 [평가 계약](../../.codex/plan/agent-strategy-lab/01-5_evaluation_and_integration.md)에 연결한다.
