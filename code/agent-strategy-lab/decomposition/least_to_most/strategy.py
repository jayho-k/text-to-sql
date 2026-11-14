import json
from shared.prompts import FINAL_INSTRUCTION, final_prompt


def run(client, question):
    decomposition = client.ask("ltm_decompose", (
        "Break the question into 1 to 3 simpler prerequisite questions in dependency order. "
        "Do not include the original question as a subquestion. "
        "Return ONLY a JSON array of strings, without markdown fences or other text.\n"
        f"Original question: {question}"
    ))
    tasks = json.loads(decomposition)
    if (not isinstance(tasks, list) or not 1 <= len(tasks) <= 3
            or any(not isinstance(q, str) or not q.strip() for q in tasks)):
        raise ValueError("invalid_decomposition: expected 1..3 nonempty question strings")
    history = []
    for task in tasks:
        answer = client.ask("ltm_solve", (
            f"Original question: {question}\nPrevious questions and answers:\n"
            + json.dumps(history, ensure_ascii=False)
            + "\nSolve this subquestion:\n" + final_prompt(task)
        ))
        history.append({"question": task, "answer": answer})
    return client.ask("ltm_final", (
        f"Answer the ORIGINAL question using the previous results when useful.\nOriginal question: {question}\n"
        "Previous questions and answers:\n" + json.dumps(history, ensure_ascii=False)
        + "\n" + FINAL_INSTRUCTION
    ))
