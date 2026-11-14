# 02. Best-of-N·MCTS와 결과 집계

분석일 **2026-11-15**, 커밋 `411ad9dd7baaa6f66d31e416cd100214447bd5f3`. [용어집](../01-core/chapter-00-glossary.md), [보상 학습·점수 계약](../01-core/chapter-01-reward-learning.md). Best-of-N은 N개 경로에서 모델 점수로 하나를 고르는 방식이다. MCTS는 분기를 탐색하고 보상을 전파하는 방식이다.

## Best-of-N의 실제 입력·선택·성과

[WebShop calc_sample.py](../../../code/reference-implementations/armap/Eval/webshop/scripts/ARMAP-B/calc_sample.py:121)는 sample 경로의 runs.jsonl을 읽어 과업 index별로 모은다. N이 함수 인자 하나로 고정되는 것이 아니라 실제 수집된 하위 경로·유효 행 수에 따라 달라진다. 생성 설정과 후보별 실패 수를 함께 보존해야 한다.

```mermaid
flowchart LR
    A[실제 생성 경로 파일] --> B[과업 ID별 후보 모음]
    B --> C[대화·관측·이미지 변환]
    C --> D[보상 서비스 점수 배열]
    D --> E[최대 예측 점수의 후보]
    E --> F[선택 후보의 실제 reward]
    B --> G[평균/최대 실제 reward 진단]
```

[sel](../../../code/reference-implementations/armap/Eval/webshop/scripts/ARMAP-B/calc_sample.py:25)은 초기/마지막 관측과 응답·이미지를 평가 입력으로 구성한다. JSON 점수를 받아 최초 최대 점수 위치의 후보를 반환한다. 선택 자체는 실제 reward의 최대를 쓰지 않는다.

[집계](../../../code/reference-implementations/armap/Eval/webshop/scripts/ARMAP-B/calc_sample.py:156)는 sample avg, sample max, sample sel을 따로 출력한다. max는 실제 환경 성과를 안다고 가정한 후보 상한이며 sel과 다르다. ScienceWorld [집계](../../../code/reference-implementations/armap/Eval/sciworld/scripts/ARMAP-B/calc_sample.py:170)도 예측 점수/실제 성과 쌍을 과업별로 모아 같은 구분을 한다.

## 필터·실패·분모

WebShop은 파일 부재·JSON/필드 오류를 건너뛰어 유효 과업만 집계될 수 있다. ScienceWorld는 Task Description 판독·대화 형식·길이 10,000자 초과 등의 조건으로 경로를 제외하고 ID 산술식을 통해 과업을 묶는다. 반환 점수와 zip하는 경로에는 개수 일치 assert가 없어 누락 시 조용히 짧아질 수 있다. 누락의 실제 빈도·성능 방향은 확인하지 않았다.

HTTP 요청은 해당 스크립트에서 명시적 timeout·raise_for_status·재시도를 갖추지 않았다. 응답 길이·NaN/무한값·후보 순서도 명세할 필요가 있다. 오류 후보/과업을 분모에서 누락하는 집계와 전체 시도 기준 성능을 구분한다.

## MCTS는 실제 환경의 상태 복원을 전제로 한다

[안내 스크립트](../../../code/reference-implementations/armap/Eval/webshop/scripts/ARMAP-M/run_mcts.sh:3)는 seq_num=10, horizon=10, rollouts=10, temperature=1.5를 준다. 이를 Best-of-N의 N이나 QLASS의 단계 후보 수와 같은 예산으로 볼 수 없다.

[webshopEnv.transition](../../../code/reference-implementations/armap/Eval/webshop/src/mcts_agents/env_webshop_wrapper.py:85)은 원래 상태 저장→분기 상태 reset→행동 실행→종료 시 학습 점수 요청→원래 상태 복원 순서다. 실제 reward_gt와 모델 reward_pd를 별도 반환한다. 비종료 모델 보상은 0이다. 실제 환경을 되돌리는 경로이므로 모델 안의 미래 상태 예측과 구분한다.

[UCT.act](../../../code/reference-implementations/armap/Eval/webshop/src/mcts_agents/uct.py:133)→[mcts_procedure](../../../code/reference-implementations/armap/Eval/webshop/src/mcts_agents/mcts.py:37)는 분기 선택·확장·rollout·예측 보상 전파를 수행한다. [test_main](../../../code/reference-implementations/armap/Eval/webshop/src/mcts_agents/env_webshop_wrapper.py:550)은 rollout 경로·모델 점수·실제 점수 배열을 저장한다. 반환 행동을 실제 배포 환경에 최종 실행하는 것과, 이미 탐색한 경로의 성과를 선택·보고하는 것을 구분해야 한다.

[performance_analysis.py](../../../code/reference-implementations/armap/Eval/webshop/src/mcts_agents/performance_analysis.py:6)는 예측 최대 점수의 경로 성과를 보며, 예측 점수가 같은 최대 후보가 여러 개면 그 실제 성과를 평균한다. Best-of-N의 첫 최대 선택과 동률 규칙이 다르다. 실제 보상의 최대값은 별도 지표다. [save_trajectory_history](../../../code/reference-implementations/armap/Eval/webshop/src/mcts_agents/utils.py:239)는 tracks에 각 state가 아니라 전체 track_list를 반복 append하는 소스 형태여서 추적 파일의 내용·행 대응은 검증이 필요하다.

## 현재 개발 계약에 반영할 것

- 실제 생성 후보 수·필터 제외·실패를 과업별 manifest에 연결한다. 디렉터리에 있는 파일 수만으로 동일 예산을 선언하지 않는다.
- 모델 점수와 환경 보상을 별도 필드로 보존하고 avg/max/sel을 혼합하지 않는다.
- 원과업별 자료 분할·후보 ID/점수 개수·동률 규칙·실행 후 독립 평가를 고정한다.
- 환경 reset/복원 행동도 상호작용 예산에 포함한다. 라이브 환경에 그대로 옮길 수 있는지는 별도 판정한다.
- 논문 성능 재현에는 모델·checkpoint·데이터·script·결과 파일의 연결이 더 필요하다. 공개 코드가 있으므로 성능이 검증됐다고 하지 않는다.

관련 테스트는 실행하지 않았다. 후속 검증은 실패 분모·점수 개수/ID·환경 복원 전후 상태·동률 결과·추적 저장의 실제 shape에 초점을 둔다. 원문 성능 후보는 유지하며 코드의 재현 결손을 구현 난이도에 따른 후보 제외로 사용하지 않는다.
