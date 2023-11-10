"""
This is the UI component to the multi agent framework appication
using chainlit and Apache eCharts

Written by: Aaron Ward - October 2023.
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

import autogen
import numpy as np
import pandas as pd
import chainlit as cl
import plotly.graph_objects as go

from dotenv import find_dotenv, load_dotenv
from agents.db_agent import DBAgent

output_folder = "_output/"
logs_filename = f"{output_folder}_logs/conversations_{datetime.now().timestamp()}.json"

# PROBLEM_TYPE = "COMPLEX"
PROBLEM_TYPE = "SIMPLE"
TOTAL_COST = 0.0
MAX_ITER = 100
USER_NAME = "User"
USER_PROXY_NAME = "User Proxy"
ASSISTANT_NAME = "Data Engineer"
WELCOME_MESSAGE = f"""
**👾 Multi Agent Data Science Team 👾**\n
_With this tool you are connected to synthetic healthcare database and article knowledgebase._
_A team of agents work in the background to get you the answers you want using various sources._
_Ask a question, or start off with one of the examples below._ 👇
\n\n
"""
load_dotenv(find_dotenv())

############################ Agent Functions #####################################

async def setup_agents(temperature: float,
                        model: str):
    """Create Agent objects and set user session variables"""
    agent = DBAgent(
        work_dir=output_folder,
        temperature=temperature,
        model=model
    )
    agent.clear_history(clear_previous_work=True)

    # Setup subagent interactions
    agent.instantiate_groupchat()
    agent.instantiate_two_way_chat()

    # User Session Variables TODO: make this dynamic
    two_way_secondary_agent_name = agent.two_way_secondary_agent.name.replace("_", " ")
    two_way_user_proxy_name = agent.two_way_user_proxy.name.replace("_", " ")

    # Setting user session variables
    cl.user_session.set('agent', agent)
    cl.user_session.set(two_way_secondary_agent_name, agent.two_way_secondary_agent)
    cl.user_session.set(two_way_user_proxy_name, agent.two_way_user_proxy)    

    # groupchat_secondary_agent_name = agent.groupchat_secondary_agent.name.replace("_", " ") # name
    # groupchat_user_proxy_name = agent.groupchat_user_proxy.name.replace("_", " ")  # admin_name
    # cl.user_session.set(groupchat_secondary_agent_name, agent.groupchat_secondary_agent)
    # cl.user_session.set(groupchat_user_proxy_name, agent.groupchat_user_proxy)

async def save_logs(logs_filename=logs_filename):
    # Make sure the directory exists
    os.makedirs(os.path.dirname(logs_filename), exist_ok=True)

    # Now save the logs
    logs = autogen.ChatCompletion.logged_history
    with open(logs_filename, "w") as log_file:
        json.dump(logs, log_file, indent=4)

    return logs

@cl.on_settings_update
async def update_agent_settings(settings):
    """Used to update agent"""
    await setup_agents(temperature=settings['Temperature'],
                        model=settings['Model'])

    print(f"Settings updated {settings}")


########################## User Interface Functions ########################################

naming_dict = {
    "User_Proxy": "User Proxy",
    "assistant": "Assistant Agent",
    "User Proxy": "User Proxy",
    "User": "User",
    "user": "User Proxy",
    "function": "Code output",
    "Data_Engineer": "Data Engineer"
}


async def setup_avatars():
    """Function for avatar icons"""
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
            "name": "Code output",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "Assistant Agent",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
    ]
    
    for avatar in avatar_configurations:
        await cl.Avatar(
            name=avatar["name"],
            url=avatar["url"],
        ).send()

async def setup_chat_settings():
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

    return settings

@cl.action_callback("on_chat_start_action")
async def on_action(action):
    await action.remove()

    print(action.value)
    action_msg = cl.Message(content=action.value, author="User",indent=0)
    await action_msg.send()

    await handle_message(cl.Message(content=action.value, author="User",
                     indent=0))

    # await handle_message(user_message: dict)

@cl.on_chat_start
async def setup_chat():

    # Setup Actions
    actions = [
        cl.Action(
                name="on_chat_start_action", 
                value="Get the count of people haven't had a checkup in 2 years.", 
                description="Tell me who hasn't had a checkup in 2 years",
                label="How many people haven't had a checkup in 2 years",
            ),
        cl.Action(
                name="on_chat_start_action", 
                value="Get the top 5 states where the most COVID-19 cases were present", 
                description="Get the top 5 states where the most COVID-19 cases were present",
                label="Where are the most COVID-19 cases?", 
            ),
        cl.Action(
                name="on_chat_start_action", 
                value="Get the average age of people with lung disease", 
                description="Get the average age of people with lung disease",
                label="Average age of people with lung disease", 
            ),
    ]

    # UI Configuirations
    await setup_avatars()
    await cl.Message(content=WELCOME_MESSAGE, author="chatbot", actions=actions).send()

    # Initialize Agents
    settings = await setup_chat_settings()
    await setup_agents(temperature=settings['Temperature'],
                        model=settings['Model'])

    cl.user_session.set("total_cost", TOTAL_COST)
    

########################## Message Handling Functions ########################################

async def handle_text_file(file_element):
    # Process text file
    pass

async def handle_image_file(file_element):
    # Process image file
    pass


async def get_response(user_message: str):
    agent = cl.user_session.get("agent")
    assistant = cl.user_session.get(agent.two_way_secondary_agent.name.replace("_", " "))
    user_proxy = cl.user_session.get(agent.two_way_user_proxy.name.replace("_", " "))

    # Run the agent to get initial or continued response
    # TODO: Stream responses to UI
    if len(assistant.chat_messages[user_proxy]) == 0:
        print('initiating a conversation with agent.run()')
        await cl.make_async(agent.run)(problem_type=PROBLEM_TYPE, prompt=user_message)
    else:
        print('continuing a conversation with agent._continue()')
        await cl.make_async(agent._continue)(problem_type=PROBLEM_TYPE, prompt=user_message)

async def handle_message_indentation():
    agent = cl.user_session.get("agent")
    assistant = cl.user_session.get(agent.two_way_secondary_agent.name.replace("_", " "))
    user_proxy = cl.user_session.get(agent.two_way_user_proxy.name.replace("_", " "))
    final_response = None

    # Retrieve and filter message history
    original_message_history = assistant.chat_messages[user_proxy]
    last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)
    new_message_history = original_message_history[last_seen_message_index:]


    # Process messages and check for TERMINATE condition
    for i, message in enumerate(new_message_history):
        content = message.get("content", "").strip() if message.get("content") else ""
        function_call = message.get("function_call", "") if message.get("function_call") else ""

        # Check for TERMINATE condition
        if "TERMINATE" in content:
            # If TERMINATE is the exact content of the last message, disregard it
            if content == "TERMINATE" and i == len(new_message_history) - 1:
                if i > 0:  # Ensure there is a message before the TERMINATE message
                    final_response = new_message_history[i - 1].get("content", "").strip()
                break  # Stop processing as we've reached the end
            else:
                content = content.strip().replace("TERMINATE.", "").replace("TERMINATE", "").strip()  # Strip TERMINATE from the content

        # Only send non-empty and non-TERMINATE contents
        if content:
            await cl.Message(
                author=naming_dict[message["role"]],
                content=content,
                indent=1
            ).send()
        if function_call:
            await cl.Message(
                author=naming_dict[message["role"]],
                content=function_call,
                indent=1
            ).send()

    cl.user_session.set('last_seen_message_index', len(original_message_history))
    if final_response is not None:
        final_response = final_response.strip().replace("TERMINATE.", "").replace("TERMINATE", "")
    print(final_response)
    return final_response


async def send_final_response(final_response):
            # Send the final message
    if final_response:
        await cl.Message(
            author="chatbot",
            content=final_response,
            indent=0
        ).send()

        chart_fig = None  # Get the chart figure
        if chart_fig:
            pass # TODO: Make code for displaying plotly dynamically in UI
    else:
        await cl.Message(
            author="chatbot",
            content="Sorry, please try again. we got lost in thought...",
            indent=0
        ).send()

def update_cost_counter(logs):
    # Display cost logs and update total cost
    conversation = next(iter(logs.values()))
    cost = sum(conversation["cost"])
    TOTAL_COST = cl.user_session.get("total_cost", 0.0) + cost
    cl.user_session.set("total_cost", TOTAL_COST)

    # Display cost counter
    cost_counter = cl.TaskList(status="Done")
    cost_task = cl.Task(title=f"Total Cost in USD for this conversation: ${TOTAL_COST:.2f}", status=cl.TaskStatus.DONE)
    return cost_counter, cost_task

@cl.on_message
async def handle_message(user_message: dict):
    """Handle a message from a user"""
    print(user_message.content)

    print(f"Problem type: {PROBLEM_TYPE}")
    if user_message.elements:
        for element in user_message.elements:
            if 'text/plain' in element.mime:
                await handle_text_file(element)
            elif 'image/' in element.mime:
                await handle_image_file(element)

    last_user_message = cl.user_session.get('user_message')
    if user_message.content == last_user_message:
        return
    cl.user_session.set('user_message', user_message.content)


    await cl.Message(
            author="User Proxy",
            content=user_message.content,
            indent=1,
    ).send()

    try:
        autogen.ChatCompletion.start_logging()
        print(f"Start logging...")

        # Ensure the get_response is awaited properly
        await get_response(user_message.content)
        print(f"Make call to get_response...")

        # Ensure the save_logs is awaited properly
        print(f"Make call to save_logs...")
        logs = await save_logs()

        autogen.ChatCompletion.stop_logging()
        print(f"stopped logging...")

        # Process and display messages
        final_response = await handle_message_indentation()
        print(f"Got final response: {final_response}")

        # Send final response if available
        await send_final_response(final_response)
        print(f"Sent final_response")

        # Update the cost counter asynchronously
        cost_counter, cost_task = await cl.make_async(update_cost_counter)(logs)
        # return cost_counter, cost_task
        await cost_counter.send()
        await cost_counter.add_task(cost_task)
        await cost_counter.send()

        print(f"updated cost counter")

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        await cl.Message(content=error_msg).send()
        raise