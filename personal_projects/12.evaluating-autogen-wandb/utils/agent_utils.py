"""
This script is contains helper functions
related to autogen. Update initiate_agents
with the appropriate agents interaction scenario to evaluate.

"""

import os
import json
import shutil
import chromadb

import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

def _is_termination_message(x):
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

def instantiate_agents(config_list, temperature):

    #NOTE: cache is deleted between each run to ensure
    # the agent cant cheat by seeing responses in
    # previous run memory
    if os.path.exists('.cache') and os.path.isdir('.cache'):
        print('Deleting cache...')
        shutil.rmtree('.cache')

    if os.path.exists('./output') and os.path.isdir('./output'):
        print('Deleting previous work...')
        shutil.rmtree('./output')

    llm_config = {
        "request_timeout": 100,
        "seed": 42,
        "config_list": config_list,
        "temperature": temperature,
    }

    boss = autogen.UserProxyAgent(
        name="Boss",
        is_termination_msg=_is_termination_message,
        human_input_mode="TERMINATE",
        system_message="The boss who ask questions and give tasks.",
        code_execution_config=False,  # we don't want to execute code in this case.
    )

    boss_aid = RetrieveUserProxyAgent(
        name="Boss_Assistant",
        is_termination_msg=_is_termination_message,
        system_message="Assistant who has extra content retrieval power for solving difficult problems.",
        human_input_mode="TERMINATE",
        retrieve_config={
            "task": "code",
            "docs_path": "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md",
            "chunk_token_size": 1000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": "groupchat",
            "get_or_create": True,
        }
    )

    coder = RetrieveAssistantAgent(
        name="Senior_Python_Engineer",
        is_termination_msg=_is_termination_message,
        system_message="You are a senior python engineer. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
    )

    reviewer = RetrieveAssistantAgent(
        name="Code_Reviewer",
        system_message="You are a code reviewer. Reply `TERMINATE` in the end when everything is done.",
        llm_config=llm_config,
    )

    return boss, boss_aid, coder, reviewer, llm_config

# def instantiate_agents(config_list, temperature):

#     #NOTE: cache is deleted between each run to ensure
#     # the agent cant cheat by seeing responses in
#     # previous run memory
#     if os.path.exists('.cache') and os.path.isdir('.cache'):
#         print('Deleting cache...')
#         shutil.rmtree('.cache')

#     if os.path.exists('./output') and os.path.isdir('./output'):
#         print('Deleting previous work...')
#         shutil.rmtree('./output')

#     assistant_config = {
#         "name": "coding_assistant",
#         "system_message": ("You are an intelligent assistant chatbot that replies with the correct answer. "
#                            "Reply `TERMINATE` in the end when everything is done."),
#         "llm_config": {
#                 "request_timeout": 1000,
#                 "seed": 42,
#                 "config_list": config_list,
#                 "temperature": temperature,
#         }
#     }
#     proxy_config = {
#         "name": "coding_runner",
#         "human_input_mode": "NEVER",
#         "max_consecutive_auto_reply": 5,
#         "is_termination_msg": _is_termination_message,
#         "code_execution_config": {
#                 "work_dir": "./output",
#                 "use_docker": False
#         },
#         "llm_config": {
#             "request_timeout": 1000,
#             "seed": 42,
#             "config_list": config_list,
#             "temperature": temperature,
#         },
#     }

#     coding_assistant = AssistantAgent(**assistant_config)
#     user_proxy = UserProxyAgent(**proxy_config)

#     return coding_assistant, user_proxy

# def get_qa_response(problem, agents, llm_config):
#     groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=12)
#     manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

#     # Start chatting with the first agent as this is the user proxy agent.
#     agents[0].initiate_chat(manager, problem=problem, n_results=3)

#     # For simplicity, let's return the last message from the chat as the final response
#     return groupchat.messages[-1] if groupchat.messages else None



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
