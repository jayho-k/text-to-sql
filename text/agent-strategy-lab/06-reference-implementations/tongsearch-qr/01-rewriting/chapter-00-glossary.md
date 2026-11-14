# 용어집

| 용어 | 쉬운 뜻과 이 코드의 의미 | 근거 |
|---|---|---|
| RQR / TongSearch QR | 검색에 도움이 될 추론 내용을 생성하도록 학습하는 재작성기. 최종 사용자 답변의 정답 검증기는 아니다 | `scripts/train/train_grpo.py` |
| GRPO | 같은 질문에서 여러 출력을 만들고 상대 보상으로 정책을 갱신하는 강화학습 방법 | `GRPOConfig`·`GRPOTrainer` |
| BGE / embedding | 문장을 숫자 벡터로 바꾸는 모델/표현. 이 코드의 보상은 정규화 벡터의 내적 차이 | `scripts/train/reward.py` |
| 양성 문서 | 관련 있다고 주어진 학습 문서. 여기서는 교사 생성 내용 또는 답변 목록이 `pos_docs_list`로 전달됨 | `scripts/data_process/build_dataset.py` |
| rollout | 학습 중 현재 정책으로 생성한 후보 출력 | `num_generations` |
| BRIGHT | 단어 일치를 넘어 추론이 필요한 검색 평가 자료. 이 코드에서는 12개 하위 과업을 사용 | `scripts/evaluation/question_rewriting.py` |
| BM25 | 질의와 문서의 단어 빈도·문서 길이를 이용하는 검색 점수 | `scripts/evaluation/retrievers.py` |
| nDCG@10 | 관련 문서를 검색 순위의 상위 10개에 잘 놓았는지 측정하는 지표 | `calculate_retrieval_metrics` |
| checkpoint | 학습 도중 저장한 모델 가중치 | `GRPOConfig.output_dir` |
| cache | 이전 결과를 다시 읽어 계산을 생략하는 저장물. 내용 식별이 충분해야 잘못된 재사용을 피할 수 있음 | `scripts/evaluation/bright_eval.py` |

각 근거는 [공식 소스](../../../code/reference-implementations/tongsearch-qr/) 아래 경로다.
