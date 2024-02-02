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
from utils.ui_utils import (setup_chat_settings, setup_avatars, handle_message_step_implementation, 
                            send_final_response, setup_agents, get_response)

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

    action_msg = cl.Message(content=action.value, author="User")
    await action_msg.send()

    await handle_message_step_implementation(cl.Message(content=action.value, author="User"))

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

    # UI Configurations
    await setup_avatars()
    await cl.Message(content=WELCOME_MESSAGE, author="chatbot", actions=actions).send()

    # Initialize Agents
    settings = await setup_chat_settings()
    await setup_agents(temperature=settings['Temperature'],
                        model=settings['Model'],
                        output_folder=output_folder)


########################## Message Handling Functions ########################################

@cl.on_message
async def handle_message(msg: cl.Message):
    """Handle a message from a user"""
    bytes = None
    
    if msg.elements:
        print(f"Received user element")
        images = [file for file in msg.elements if "image" in file.mime]
        print(images)
        if len(images) > 1:
            await cl.Message(content="I can only handle one image at a time", author="chatbot").send()
        else:
            
            bytes = images
            print(bytes)

    # await get_response(user_message=msg.content, bytes=bytes) 