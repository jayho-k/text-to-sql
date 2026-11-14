"""자체 작성 지시. 논문 부록 프롬프트 전사가 아님."""
PROMPT_VERSION = "lab-v1"
FINAL_INSTRUCTION = "End with a separate line in this exact format: FINAL: <answer>. Do not put punctuation after the answer."


def final_prompt(question):
    return f"Answer the following question. Give a brief explanation if needed.\n{FINAL_INSTRUCTION}\nQuestion: {question}"
