import os
import json
import shutil

import autogen
from autogen import AssistantAgent, UserProxyAgent

def _is_termination_message( x):
    return x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")
    
def get_config(model_type, dotenv_path):
    config_list = autogen.config_list_from_dotenv(
        dotenv_file_path=dotenv_path,
        model_api_key_map={
            "gpt-4": "OPENAI_API_KEY",
            "gpt-3.5-turbo": "OPENAI_API_KEY",
        },
        filter_dict={
            "model": {
                model_type,
            }
        }
    )
    return config_list

def instiate_agents(config_list, temperature):

    #NOTE: cache is deleted between each run to ensure
    # the agent cant cheat by seeing responses in
    # previous run memory
    if os.path.exists('.cache') and os.path.isdir('.cache'):
        print('Deleting cache...')
        shutil.rmtree('.cache')

    if os.path.exists('./output') and os.path.isdir('./output'):
        print('Deleting previous work...')
        shutil.rmtree('./output')

    assistant_config = {
        "name": "coding_assistant",
        "system_message": ("You are an intelligent assistant chatbot that replies with the correct answer. "
                           "Reply `TERMINATE` in the end when everything is done."),
        "llm_config": {
                "request_timeout": 1000,
                "seed": 42,
                "config_list": config_list,
                "temperature": temperature,
        }
    }
    proxy_config = {
        "name": "coding_runner",
        "human_input_mode": "NEVER",
        "max_consecutive_auto_reply": 5,
        "is_termination_msg": _is_termination_message,
        "code_execution_config": {
                "work_dir": "./output",
                "use_docker": False
        },
        "llm_config": {
            "request_timeout": 1000,
            "seed": 42,
            "config_list": config_list,
            "temperature": temperature,
        },
    }

    coding_assistant = AssistantAgent(**assistant_config)
    user_proxy = UserProxyAgent(**proxy_config)

    return coding_assistant, user_proxy



def get_qa_response(model_type,
                    user_proxy,
                    assistant,
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
    user_proxy.initiate_chat(assistant, message=user_message, config_list=config_list, silent=False)
    logs = autogen.ChatCompletion.logged_history
    # json.dump(logs, open(logs_filename, "w"), indent=4)
    # logs = save_autogen_logs(logs_filename)
    autogen.ChatCompletion.stop_logging()
    
    if logs:
        conversation = next(iter(logs.values()))
        cost = sum(conversation["cost"])
    else:
        raise ValueError("Logs are none.")

    # Filter and modify messages with "TERMINATE" and take last message
    original_message_history = assistant.chat_messages[user_proxy]

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
