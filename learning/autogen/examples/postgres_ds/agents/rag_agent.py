"""
Class for QA Response scenarios.

TODO: Create this class
"""


def get_qa_response(model_type,
                    agents,
                    user_message,
                    config_list,
                    logs_filename):
    """ Function for getting answer from agents"""

    if model_type == "gpt-3.5-turbo":
        termination_notice = (
            '\n\nDo not show appreciation in your responses, say only what is necessary. '
            'if "Thank you" or "You\'re welcome" are said in the conversation, then say TERMINATE '
            'to indicate the conversation is finished and this is your last message.'
        )
        user_message += termination_notice

    autogen.ChatCompletion.start_logging()
    
    llm_config = agents[-1]
    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=12)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the first agent as this is the user proxy agent.
    agents[0].initiate_chat(manager, problem=user_message, n_results=3)
    # user_proxy.initiate_chat(assistant, message=user_message, config_list=config_list, silent=False)
    logs = autogen.ChatCompletion.logged_history

    if not os.path.exists("./autogen_logs/"):
        os.makedirs("./autogen_logs/")

    with open(logs_filename, "w") as file:
        json.dump(logs, file, indent=4)
    autogen.ChatCompletion.stop_logging()
    
    if logs:
        conversation = next(iter(logs.values()))
        cost = sum(conversation["cost"])
    else:
        raise ValueError("Logs are none.")

    # original_message_history = agents[1].chat_messages[agents[0]]
    
    # Filter and modify messages with "TERMINATE" and take last message
    # For simplicity, let's return the last message from the chat as the final response
    original_message_history = groupchat.messages[-1] if groupchat.messages else None

    message_history = []
    for message in original_message_history:
        stripped_content = message["content"].strip()
        if stripped_content != "TERMINATE":
            if stripped_content.endswith("TERMINATE"):
                message["content"] = stripped_content.replace(
                    "TERMINATE", "").strip()
            message_history.append(message)

    if message_history:
        # Identify the final response
        return message_history[-1]["content"], cost
    else:
        return "No valid messages found.", cost
