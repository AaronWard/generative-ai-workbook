"""
This is the UI component to the multi agent framework appication
using chainlit and Apache eCharts

Written by: Aaron Ward - October 2023.
"""
import os
import json
import autogen
import chainlit as cl
from pathlib import Path
from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from agents.db_agent import DBAgent

output_folder = "_output/"
logs_filename = f"{output_folder}_logs/conversations_{datetime.now().timestamp()}.json"

TOTAL_COST = 0.0
MAX_ITER = 100
USER_NAME = "User"
USER_PROXY_NAME = "User Proxy"
ASSISTANT_NAME = "Data Engineer"
WELCOME_MESSAGE = f"""
BLUE 👾
\n\n
"""

# PROBLEM_TYPE = "COMPLEX"
PROBLEM_TYPE = "SIMPLE"

load_dotenv(find_dotenv())

##########################################################

# TODO: Make dynamic agent assigning capability, which will allow the agents to be picked dynamically
# into "tiger teams" to achieve a given task.
# TODO: Incorporate orchestration of groupchat conversations
# TODO: Intergrate multiple facets of direction: RAG, Database search

@cl.on_settings_update
async def update_agent_settings(settings):
    agent = cl.user_session.get("agent")

    agent.model = settings['Model']    
    agent.instantiate_groupchat()
    agent.instantiate_two_way_chat()


    print(agent.two_way_secondary_agent.llm_config)
    # agent.two_way_secondary_agent.llm_config.model.update(settings['Model'])
    # agent.two_way_secondary_agent.llm_config.temperature.update(settings['Temperature'])
    
    # agent.two_way_user_proxy.llm_config.model.update(settings['Model'])
    # agent.two_way_user_proxy.llm_config.temperature.update(settings['Temperature'])
    print(f"Settings updated {settings}")

async def setup_avatars():
    avatar_configurations = [
        {
            "name": "User",
            "url": "https://api.dicebear.com/7.x/thumbs/svg?seed=Callie&rotate=360&eyes=variant4W14&eyesColor=ffffff,000000",
        },
        {
            "name": "User Proxy",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "Data Engineer",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "chatbot",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Dusty&backgroundColor=ffb300",
        },
        {
            "name": "Function Call",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "assistant",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
    ]
    
    for avatar in avatar_configurations:
        await cl.Avatar(
            name=avatar["name"],
            url=avatar["url"],
        ).send()

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

    # Initialize Agents
    agent = DBAgent(
        work_dir=output_folder,
        temperature=settings['Temperature'],
        model=settings["Model"]
    )
    agent.clear_history(clear_previous_work=True)

    # UI Configuirations
    await setup_avatars()


    # User Session Variables
    two_way_secondary_agent_name = agent.two_way_secondary_agent.name.replace("_", " ")
    two_way_user_proxy_name = agent.two_way_user_proxy.name.replace("_", " ")
    # groupchat_secondary_agent_name = agent.groupchat_secondary_agent.name.replace("_", " ") # name
    # groupchat_user_proxy_name = agent.groupchat_user_proxy.name.replace("_", " ")  # admin_name

    # Setting user session variables
    cl.user_session.set('agent', agent)
    # cl.user_session.set(groupchat_secondary_agent_name, agent.groupchat_secondary_agent)
    # cl.user_session.set(groupchat_user_proxy_name, agent.groupchat_user_proxy)
    cl.user_session.set(two_way_secondary_agent_name, agent.two_way_secondary_agent)
    cl.user_session.set(two_way_user_proxy_name, agent.two_way_user_proxy)    
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
    # Make sure the directory exists
    os.makedirs(os.path.dirname(logs_filename), exist_ok=True)

    # Now save the logs
    logs = autogen.ChatCompletion.logged_history
    with open(logs_filename, "w") as log_file:
        json.dump(logs, log_file, indent=4)

    return logs


@cl.on_message
async def run_conversation(user_message: str):
    try:
        # Ensure user message is not repeating
        last_user_message = cl.user_session.get('user_message')
        if user_message == last_user_message:
            return
        else:
            cl.user_session.set('user_message', user_message)

        # Initialize conversation variables
        cur_iter = 0
        final_response = None  
        termination_flag = False
        

        print(f"Problem type: {PROBLEM_TYPE}")

        # Get the correct agents based on the problem type
        agent = cl.user_session.get("agent")
        assistant = cl.user_session.get(agent.two_way_secondary_agent.name.replace("_", " "))
        user_proxy = cl.user_session.get(agent.two_way_user_proxy.name.replace("_", " "))

        naming_dict = {
            "user": user_proxy.name.replace("_", " "), 
            "assistant": assistant.name.replace("_", " "),
        }

        print("Start logging...")
        autogen.ChatCompletion.start_logging()

        # Run the agent to get initial or continued response
        if len(assistant.chat_messages[user_proxy]) == 0:
            await cl.make_async(agent.run)(problem_type=PROBLEM_TYPE, prompt=user_message)
        else:
            await cl.make_async(agent._continue)(problem_type=PROBLEM_TYPE, prompt=user_message)

        while cur_iter < MAX_ITER and not termination_flag:
            # Retrieve and filter message history
            original_message_history = assistant.chat_messages[user_proxy]
            last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)

            print(f"Original message history: {original_message_history}")

            # The new message history list should only include new messages
            new_message_history = original_message_history[last_seen_message_index:]

            print(f"New message history: {new_message_history}")

            # Process messages, checking for TERMINATE condition
            for i, message in enumerate(new_message_history):
                function_call = message.get("function_call", None)
                content = message.get("content", "")
                if content is None:
                    continue  # Skip this iteration if content is None
                
                content = content.strip()
                is_last_message = (i == len(new_message_history) - 1)

                # Check for TERMINATE condition
                if "TERMINATE" in content:
                    if is_last_message:
                        # If TERMINATE is in the last message, strip it and set termination_flag
                        termination_flag = True
                        final_response = content.replace("TERMINATE", "").strip()
                        break  # Stop processing messages, as we have reached the end
                    else:
                        # If TERMINATE is not in the last message, strip it and continue
                        content = content.replace("TERMINATE", "").strip()

                # Only send non-empty contents
                if content:
                    await cl.Message(
                        author=naming_dict.get(message["role"], message["role"]),
                        content=content,
                        indent=1
                    ).send()

                if function_call:
                    await cl.Message(
                        author=naming_dict.get(message["role"], "Function Call"),
                        content=function_call,
                        indent=1
                    ).send()

            # Update the last seen index
            cl.user_session.set('last_seen_message_index', len(original_message_history))

            if termination_flag:
                final_response = new_message_history[-1].get("content", "").strip() if new_message_history else "No valid messages found."
                break

            cur_iter += 1

        print(f"Final response: {final_response}")

        # Send the final message
        if final_response:
            await cl.Message(
                author="chatbot",
                content=final_response,
                indent=0
            ).send()
        else:
            await cl.Message(
                author="chatbot",
                content="Sorry, we got lost in thought...",
                indent=0
            ).send()

        # Display cost logs and update total cost
        logs = save_logs()
        autogen.ChatCompletion.stop_logging()
        conversation = next(iter(logs.values()))
        cost = sum(conversation["cost"])
        TOTAL_COST = cl.user_session.get("total_cost", 0.0) + cost
        cl.user_session.set("total_cost", TOTAL_COST)

        # Display cost counter
        cost_counter = cl.TaskList(status="Done")
        await cost_counter.send()
        cost_task = cl.Task(title=f"Total Cost in USD for this conversation: ${TOTAL_COST:.2f}", status=cl.TaskStatus.DONE)
        await cost_counter.add_task(cost_task)
        await cost_counter.send()

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        await cl.Message(content=error_msg).send()
        raise  # Rethrow the exception after sending the error message to the user
