"""
This is the UI component to the multi agent framework application
using chainlit and autogens GPT Assistant.

The intended goal is to control a robots motions using natural language.
The robot has different sets of motions called Actions (located in action_files).
These can be used as function calls

TODO: Experiment with passing each action as function, or providing a single function
and pass the .d6a files. 

Written by: Aaron Ward - December 2023.
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
    "Robot_Motion_Assistant": "Robot Motion Assistant"
}

USER_NAME = "User"
USER_PROXY_NAME = "User Proxy"
ASSISTANT_NAME = "Robot Motion Assistant"
WELCOME_MESSAGE = f"""
**👾 Robot Motion Automation👾**\n
_This tool is intended to be a motion orchestration system for the raspberry pi
robot. The end goal is extend this and allow the robot to decide itself which
motions it wants to take._

_Give instructions, or start off with one of the examples below._ 👇
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

    # Setup Actions
    actions = [
        cl.Action(
                name="on_chat_start_action", 
                value="Stand in a T-Pose", 
                description="Stand in a T-Pose",
                label="Stand in a T-Pose",
            ),
        cl.Action(
                name="on_chat_start_action", 
                value="Kneel Down", 
                description="Kneel Down",
                label="Kneel Down", 
            )
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
    print(f"Received user message: {user_message.content}")
    # if user_message.elements:
    #     pass
        # for element in user_message.elements:
        #     if 'text/plain' in element.mime:
        #         await handle_text_file(element)
        #     elif 'image/' in element.mime:
        #         await handle_image_file(element)

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
        # Ensure the get_response is awaited properly
        await get_response(user_message=user_message.content)
        print(f"Make call to get_response...")

        # Process and display messages
        final_response = await handle_message_indentation(naming_dict)
        print(f"Got final response: {final_response}")

        # Send final response if available
        await send_final_response(final_response)
        print(f"Sent final_response")

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        await cl.Message(content=error_msg).send()
        raise