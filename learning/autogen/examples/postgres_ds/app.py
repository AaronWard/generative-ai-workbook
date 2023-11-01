"""
This is the UI component to the multi agent framework appication
using chainlit and Apache eCharts

Written by: Aaron Ward - October 2023.
"""
import json
import autogen
import chainlit as cl
from pathlib import Path
from datetime import datetime

from dotenv import find_dotenv, load_dotenv

from .agents import MultiAgent
from .data_dictionaries import dictionary

logs_filename = f"_logs/conversations_{datetime.now().timestamp()}.json"
output_folder = "/Users/award40/Desktop/example_output"
# Get the path of the script
# data_relative_path = './data/synthetic_covid_dataset_20230828.csv'
# data_path = str(Path(__file__).absolute().parent.joinpath(data_relative_path).resolve())
data_loc_context = f"\n\nHere is the path to data that you should import: {data_path}"
data_dict_context = f"\n\nHere is the data dictionary: {dictionary.PROMPT_STRING}"


TOTAL_COST = 0.0
MAX_ITER = 100
USER_NAME = "User"
USER_PROXY_NAME = "Code Runner Agent"
ASSISTANT_NAME = "Programmer Agent"
WELCOME_MESSAGE = f"""
BLUE 👾
\n\n
"""

load_dotenv(find_dotenv())

##########################################################

@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.on_chat_start
async def setup_agent():
    # Set up agent configuration
    settings = await cl.ChatSettings(
            [
                cl.input_widget.Select(
                    id="Model",
                    label="Model",
                    values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                    initial_index=2
                ),
                cl.input_widget.Slider(id="Temperature", label="Temperature (randomness)", initial=0.5, min=0, max=2, step=0.1),
            ]
    ).send()

    print(settings)

    # Initialize Agents
    agent = MultiAgent(work_dir=output_folder,
                       temperature=settings['Temperature'],
                       model=settings["Model"]
                    )
    agent.clear_history()
    coding_assistant, coding_runner = agent.instiate_agents()

    # UI Configuirations
    await cl.Avatar(
        name=USER_NAME,
        url="https://api.dicebear.com/7.x/thumbs/svg?seed=Callie&rotate=360&eyes=variant4W14&eyesColor=ffffff,000000",
    ).send()

    await cl.Avatar(
        name=USER_PROXY_NAME,
        url="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
    ).send()

    await cl.Avatar(
        name=ASSISTANT_NAME,
        url="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
    ).send()

    await cl.Avatar(
        name="chatbot",
        url="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Dusty&backgroundColor=ffb300",  # Change this to the desired avatar URL
    ).send()

    # Setting user session variables
    cl.user_session.set('agent', agent)
    cl.user_session.set(ASSISTANT_NAME, coding_assistant)
    cl.user_session.set(USER_PROXY_NAME, coding_runner)
    cl.user_session.set("total_cost", TOTAL_COST)

    await cl.Message(content=WELCOME_MESSAGE, author="chatbot").send()

@cl.on_file_upload(accept=["text/plain"], max_files=3, max_size_mb=2)
async def upload_file(files: any):
    """
    Handle uploaded files.
    Example:
        [{
            "name": "example.txt",
            "content": b"File content as bytes",
            "type": "text/plain"
        }]
    """
    for file_data in files:
        file_name = file_data["name"]
        content = file_data["content"]
        # If want to show content Content: {content.decode('utf-8')}\n\n
        await cl.Message(content=f"Uploaded file: {file_name}\n").send()
        
        # Save the file locally
        with open(file_name, "wb") as file:
            file.write(content)

def save_logs(logs_filename=logs_filename):
    logs = autogen.ChatCompletion.logged_history
    json.dump(logs, open(logs_filename, "w"), 
                indent=4)
    return logs

@cl.on_message
async def run_conversation(user_message: str):
    try:
        # check if user message changed
        if user_message == cl.user_session.get('user_message'):
            return
                
        print("Start logging...")
        autogen.ChatCompletion.start_logging()

        # Get agents and append termination notice if necessary
        agent = cl.user_session.get("agent")
        assistant = cl.user_session.get(ASSISTANT_NAME)
        user_proxy = cl.user_session.get(USER_PROXY_NAME)

        assistant_model_type = assistant.llm_config['config_list'][0]['model']   # Assuming single model in config list
        user_proxy_model_type = user_proxy.llm_config['config_list'][0]['model'] 

        # Context injection for alignment  
        user_message += data_loc_context + data_dict_context
        if assistant_model_type == "gpt-3.5-turbo" or user_proxy_model_type == "gpt-3.5-turbo":
            user_message += termination_notice
        
        # Variables for conversation loop
        cur_iter = 0
        final_response = None  
        naming_dict = {
            "User": "You",
            "user": USER_PROXY_NAME,
            "assistant": ASSISTANT_NAME,
        }

        if len(assistant.chat_messages[user_proxy]) == 0:
            user_proxy.initiate_chat(assistant, message=user_message, config_list=agent.config_list)
        else:
            user_proxy.send(recipient=assistant, message=user_message)

        while cur_iter < MAX_ITER:            
            original_message_history = assistant.chat_messages[user_proxy]
            last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)

            # Filter out messages with "TERMINATE"
            # Filter and modify messages with "TERMINATE"
            message_history = []
            for message in original_message_history:
                stripped_content = message["content"].strip()
                if stripped_content != "TERMINATE":
                    if stripped_content.endswith("TERMINATE"):
                        message["content"] = stripped_content.replace("TERMINATE", "").strip()
                    message_history.append(message)

            # TODO: Sometimes a message is just terminate, sometimes it stops with a full messages
            # with the word terminate in it. Therefore, in order check if hard problems are not completing
            # from a UI perspective it needs to have a check in the while loof for a TEMINATION status
            # for both of these conditions, then it can break out of the loop when a termination occurs.
            # I will need to move the conditions and stripping above down below as i need it
            # in the message history 

            # Check if message_history is not empty to avoid IndexError
            if message_history:
                # Identify the final response
                final_response = message_history[-1]["content"]
            else:
                final_response = "No valid messages found." 
            
            # Loop through and display the messages, excluding the final one
            for message in message_history[last_seen_message_index:-1]:
                if message['content'].rstrip() == "TERMINATE":
                    break

                await cl.Message(
                    author=naming_dict[message["role"]],
                    content=message["content"],
                    indent=1 
                ).send()
            
            cl.user_session.set('last_seen_message_index', len(message_history))
            cur_iter += 1

        if final_response:
            # Send the final message without indentation and with "chatbot" author, outside the loop
            await cl.Message(
                author="chatbot",
                content=final_response,
                indent=0  # No indentation
            ).send()
        else:
            await cl.Message(
                author="chatbot",
                content="Sorry, we got lost in thought...",
                indent=0  # No indentation
            ).send()

        # Display cost logs
        logs = save_logs()
        conversation = next(iter(logs.values()))
        cost = sum(conversation["cost"])

        TOTAL_COST = float(cl.user_session.get("total_cost", 0))
        cost += TOTAL_COST
        cl.user_session.set("total_cost", cost)

        cost_counter = cl.TaskList(name="Cost Counter", status="running")
        await cost_counter.send()
        cost_task = cl.Task(title=f"Total Cost in USD for this conversation: ${float(cl.user_session.get('total_cost', 0)):.2f}", status=cl.TaskStatus.DONE)
        await cost_counter.add_task(cost_task)
        await cost_counter.send()

    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()
