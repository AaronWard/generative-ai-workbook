"""
This is the UI component to the multi agent framework application
using chainlit and autogens GPT Assistant.

Written by: Aaron Ward - Jan 2024.
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
from utils.ui_utils import (setup_chat_settings, setup_avatars, 
                            handle_message_indentation, send_final_response, 
                            setup_agents, get_response)


output_folder = "_output/"
logs_filename = f"{output_folder}_logs/conversations_{datetime.now().timestamp()}.json"
naming_dict = {
    "User_Proxy": "User Proxy",
    "assistant": "Assistant Agent",
    "User Proxy": "User Proxy",
    "User": "User",
    "user": "User Proxy",
    "function": "Code output",
}

USER_NAME = "User"
USER_PROXY_NAME = "User Proxy"
ASSISTANT_NAME = "Image Analyzer"
WELCOME_MESSAGE = f"""
**👾Image Analyzer👾**\n
_Chat interface for multimodel models such as Llava_

_Drop in an image, or start off with one of the examples below._ 👇
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

@cl.on_chat_start
async def setup_chat():
    actions = [
        cl.Action(
                name="on_chat_start_action", 
                value="What can you do?", 
                description="What can you do?",
                label="What can you do?",
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


########################## Message Handling Functions ########################################

@cl.on_message
async def handle_message(user_message: dict):
    """Handle a message from a user"""
            
    last_user_message = cl.user_session.get('user_message')
    bytes = None
    if user_message.content == last_user_message:
        print(f"Received user message: {user_message.content}")

        return
    cl.user_session.set('user_message', user_message.content)

    if user_message.elements:
        print(f"Received user element")
        for element in user_message.elements:
            if 'image/' in element.mime:
                bytes = element.content

    await cl.Message(
            author="Image Analyzer",
            content=user_message.content,
            indent=1,
    ).send()

    try:
        response = await get_response(user_message=user_message.content, bytes=bytes)
        print(f"Make call to get_response...")

        await send_final_response(response)
        print(f"Sent final_response")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        await cl.Message(content=error_msg).send()
        raise