def format_chat_history(messages):
    history = ""

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        history += f"{role}: {content}\n"

    return history