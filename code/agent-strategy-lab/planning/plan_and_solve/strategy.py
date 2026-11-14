from shared.prompts import FINAL_INSTRUCTION


def run(client, question):
    solution = client.ask("ps_generate", (
        "Understand the problem, write a brief plan, then solve it following that plan. "
        "Keep the plan and explanation concise.\nQuestion: " + question
    ))
    return client.ask("ps_extract", (
        "Extract the final answer to the original question from this candidate solution.\n"
        f"Original question: {question}\nCandidate solution:\n{solution}\n{FINAL_INSTRUCTION}"
    ))
