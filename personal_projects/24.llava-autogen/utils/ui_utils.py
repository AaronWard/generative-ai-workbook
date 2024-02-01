"""
Utility functions for UI components

"""
import os
import json
import base64
import autogen
import chainlit as cl
from agents.image_agent import ImageAgent
from autogen import GroupChat
from typing import Dict, Union

########################## Setup Functions ########################################

async def setup_agents(temperature: float,
                        model: str,
                        output_folder: str):
    """Create Agent objects and set user session variables"""
    agent = ImageAgent(model=model)
    agent.clear_history(clear_previous_work=True)
    cl.user_session.set('agent', agent)

async def setup_chat_settings():
    # Set up agent configuration
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="Model",
                label="Model",
                values=["llava:34b"],
                initial_index=0
            ),
            cl.input_widget.Slider(id="Temperature", label="Temperature (randomness)", initial=0, min=0, max=2, step=0.1),
        ]
    ).send()

    return settings

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
            "name": "Llava",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Fluffy&radius=45&backgroundColor=546e7a",
        },
        {
            "name": "chatbot",
            "url": "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Dusty&backgroundColor=ffb300",
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

########################## Message Handling Functions ########################################

# termination_msgs = ["TERMINATE", "TERMINATE."]

async def handle_message_parent_idation(naming_dict):
    """
    Handles message parent_idation for chainlit UI components. Within
    a run of the Autogen agent conversations there may be messages inbetween
    by agents conversing amongst themselves that we may want to see.
    This sets them to an parent_idation level of 1, while the final response is 
    set to parent_idation level 0.

    There is no gaurantee that the last message in an Autogen conversation will be
    the message we want, so the function provides functionality to ommitt messages
    that are just termination messages, and removes termination messages from the 
    final response we want. 
    
    There are different types of information that we make be interested in within the message
    json keys, such as `content` and `function_call`, they need to accounted for when pulling from the message.

    The function also updates some chainlit user session values for updating the UI.
    
    """
    agent: ImageAgent = cl.user_session.get("agent")
    group_chat = agent.groupchat 

    last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)
    new_message_history = group_chat.messages[last_seen_message_index:]
    final_response = None


    for i, message in enumerate(new_message_history):
        print(message)

        content = message.get("content", "")
        if content:
            content.strip()
        function_call = message.get("function_call", "")

        if content:
            if "TERMINATE" in content:
                content = content.replace("TERMINATE.", "").replace("TERMINATE", "").strip()
                if content == ""  and  i > 0:
                    final_response = new_message_history[i - 1].get("content", "").strip()
                    final_response = final_response.replace("TERMINATE.", "").replace("TERMINATE", "")
                    if final_response != "None":
                        final_response = new_message_history[i - 2].get("content", "").strip()
                    break
                elif content != "":
                    final_response = content
                    final_response = final_response.strip().replace("TERMINATE.", "").replace("TERMINATE", "")

                    break
            else:
                final_response = content

            await cl.Message(
                author=naming_dict[message["role"]],
                content=content,
                parent_id=1
            ).send()

        if function_call:
            final_response = function_call
            await cl.Message(
                author=naming_dict[message["role"]],
                content=function_call,
                parent_id=1
            ).send()

    cl.user_session.set('last_seen_message_index', len(group_chat.messages))
    if type(final_response) == str:
        final_response = final_response.strip().replace("TERMINATE.", "").replace("TERMINATE", "")

    return final_response

async def get_response(user_message: str, bytes: str):
    agent: ImageAgent = cl.user_session.get("agent")
    return await cl.make_async(agent.run)(prompt=user_message, bytes=bytes)

async def send_final_response(final_response):
    if final_response:
        await cl.Message(
            author="chatbot",
            content=final_response,
            parent_id=0
        ).send()
    else:
        await cl.Message(
            author="chatbot",
            content="Sorry, please try again. we got lost in thought...",
            parent_id=0
        ).send()
