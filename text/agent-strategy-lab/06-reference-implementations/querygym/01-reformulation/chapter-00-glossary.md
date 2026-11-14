# 용어집

| 용어 | 쉬운 뜻과 이 코드의 의미 | 근거 |
|---|---|---|
| reformulation / expansion | 검색 표현을 바꾸기 / 관련 단어·내용을 덧붙이기 | `querygym/methods/` |
| GenQR | 같은 지시로 여러 번 확장어를 생성해 원질의와 연결 | `methods/genqr.py` |
| GenQREnsemble | 서로 다른 지시로 만든 확장어를 합침 | `methods/genqr_ensemble.py` |
| Q2K / Query2E | E01의 keyword 확장 이름 / 공개 코드의 관련 확장 클래스. 동일 실험 행의 직접 대응은 추가 확인 필요 | E01 §2.2.1·`methods/query2e.py` |
| QueryItem | 질의 ID `qid`와 원문 `text`의 입력 객체 | `core/base.py` |
| ReformulationResult | ID·원질의·검색용 최종 문자열·metadata를 담는 결과 | `core/base.py` |
| prompt bank | ID별 system/user/assistant 지시를 보관한 YAML | `querygym/prompt_bank.yaml` |
| qrels | 어떤 문서가 어떤 질의에 얼마나 관련 있는지의 평가 정답 | `examples/querygym_pyserini/evaluate.py` |
| run file | 문서 순위·점수를 저장한 검색 결과 | `reproducibility/data/runs/` |
| params_hash | 방법·모델·설정 JSON에서 계산한 짧은 해시. 코드/프롬프트 전체의 해시는 아님 | `reproducibility/lib/emit.py` |
| fallback | 재작성 실패 시 원질의를 반환해 검색을 계속하는 경로 | `methods/query2e.py` |
| MuGI | 여러 의사 문서를 생성하고 질의 길이와 결합을 조정하는 방식 | `methods/mugi.py` |
| QA-Expand | 질문 여러 개 → 의사 답변 → 검토/수정의 세 단계 확장 | `methods/qa_expand.py` |
| CSQE / KEQE | 검색 코퍼스 문장으로 확장을 보완 / 모델 지식만으로 글을 생성. CSQE의 원논문 명칭은 Corpus-Steered Query Expansion | `methods/csqe.py` |
| LameR | 초기 검색 문서를 읽고 새 글을 만들어 다시 검색 | `methods/lamer.py` |
| contextualized pooling | 원질의와 각 생성문을 함께 벡터화한 결과를 결합. 문자열 전체 한 번의 벡터화와 다름 | MuGI 원논문 §3 |
| RRF | 여러 검색 순위의 역수 점수를 더하는 Reciprocal Rank Fusion | QA-Expand 원논문 §4.2 |
| backfill | 과거 결과를 현재 자료 형식으로 옮긴 기록. 당시 환경/커밋 미상 가능 | `reproducibility/scripts/submit_run.py` |

근거는 [공식 소스](../../../code/reference-implementations/querygym/) 아래 경로다.
