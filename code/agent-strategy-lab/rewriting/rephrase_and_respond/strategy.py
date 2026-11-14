from shared.prompts import FINAL_INSTRUCTION

REWRITE = ("Rephrase the question to make it clearer. Preserve all facts, numbers, units, "
           "negation, conditions and the requested output; do not add assumptions.")


def run_one(client, question):
    return client.ask("rar_joint", (
        f"{REWRITE} Then answer the question. Label the rephrased question REPHRASE.\n"
        f"Original question: {question}\n{FINAL_INSTRUCTION}"
    ))


def run_two(client, question):
    rewrite = client.ask("rar_rewrite", f"{REWRITE} Return only the rephrased question.\nOriginal question: {question}")
    return client.ask("rar_respond", (
        "Answer the original question with help from the rephrased version. "
        "If they disagree, follow the original question.\n"
        f"Original question: {question}\nRephrased question: {rewrite}\n{FINAL_INSTRUCTION}"
    ))
