from shared.prompts import final_prompt


def run(client, question):
    return client.ask("direct", final_prompt(question))
