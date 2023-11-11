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

from utils.ui_utils import (save_logs, setup_chat_settings, setup_avatars, 
                            handle_message_indentation, update_cost_counter, 
                            send_final_response, handle_text_file, 
                            handle_image_file, setup_agents, get_response)

output_folder = "_output/"
logs_filename = f"{output_folder}_logs/conversations_{datetime.now().timestamp()}.json"
naming_dict = {
    "User_Proxy": "User Proxy",
    "assistant": "Assistant Agent",
    "User Proxy": "User Proxy",
    "User": "User",
    "user": "User Proxy",
    "function": "Code output",
    "Data_Engineer": "Data Engineer"
}


# PROBLEM_TYPE = "COMPLEX"
PROBLEM_TYPE = "SIMPLE"
TOTAL_COST = 0.0
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

@cl.on_settings_update
async def update_agent_settings(settings):
    """Used to update agent"""
    await setup_agents(temperature=settings['Temperature'],
                        model=settings['Model'], 
                        output_folder=output_folder)

    print(f"Settings updated {settings}")

########################## User Interface Functions ########################################

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
                        model=settings['Model'],
                        output_folder=output_folder)

    cl.user_session.set("total_cost", TOTAL_COST)
    

########################## Message Handling Functions ########################################


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

    # "Using {groupchat / twoway}"
    await cl.Message(
            author="User Proxy",
            content=user_message.content,
            indent=1,
    ).send()

    try:
        autogen.ChatCompletion.start_logging()
        print(f"Start logging...")

        # Ensure the get_response is awaited properly
        await get_response(problem_type=PROBLEM_TYPE, 
                           user_message=user_message.content)
        print(f"Make call to get_response...")

        # Ensure the save_logs is awaited properly
        print(f"Make call to save_logs...")
        logs = await save_logs(logs_filename=logs_filename)

        autogen.ChatCompletion.stop_logging()
        print(f"stopped logging...")

        # Process and display messages
        final_response = await handle_message_indentation(naming_dict)
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