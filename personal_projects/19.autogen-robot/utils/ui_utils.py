"""
Utility functions for UI components

"""
import os
import json
import autogen
import chainlit as cl
from agents.robot_agent import RobotAgent
from autogen import GroupChat
from typing import Dict, Union


# async def setup_agents(temperature: float,
#                         model: str,
#                         output_folder: str):
#     """Create Agent objects and set user session variables"""
#     agent = RobotAgent(model=model)
                        
#     # # User Session Variables TODO: make this dynamic
#     # secondary_agent_name = agent.secondary_agent.name.replace("_", " ")
#     # user_proxy_name = agent.user_proxy.name.replace("_", " ")

#     # # Setting user session variables
#     # cl.user_session.set('agent', agent)
#     # cl.user_session.set(secondary_agent_name, agent.secondary_agent)
#     # cl.user_session.set(user_proxy_name, agent.user_proxy)    


async def setup_agents(temperature: float,
                        model: str,
                        output_folder: str):
    """Create Agent objects and set user session variables"""
    agent = RobotAgent(model=model)
    agent.clear_history(clear_previous_work=True)
    agent.instantiate_groupchat()

    # secondary_agent_name = agent.secondary_agent.admin_name.replace("_", " ")
    # user_proxy_name = "User Proxy"

    cl.user_session.set('agent', agent)
    cl.user_session.set("Admin", agent.groupchat)
    cl.user_session.set("User Proxy", agent.user_proxy)

async def setup_chat_settings():
    # Set up agent configuration
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="Model",
                label="Model",
                values=["gpt-3.5-turbo",  "gpt-4-1106-preview", "gpt-4"],
                initial_index=2
            ),
            cl.input_widget.Slider(id="Temperature", label="Temperature (randomness)", initial=0.5, min=0, max=2, step=0.1),
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
            "name": "Data Engineer",
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


async def handle_message_indentation(naming_dict):
    """
    Handles message indentation for chainlit UI components. Within
    a run of the Autogen agent conversations there may be messages inbetween
    by agents conversing amongst themselves that we may want to see.
    This sets them to an indentation level of 1, while the final response is 
    set to indentation level 0.

    There is no gaurantee that the last message in an Autogen conversation will be
    the message we want, so the function provides functionality to ommitt messages
    that are just termination messages, and removes termination messages from the 
    final response we want. 
    
    There are different types of information that we make be interested in within the message
    json, such as content and function_call, they need to accounted for when pulling from the message.

    The function also updates some chainlit user session values for updating the UI.
    
    """
"""
Utility functions for UI components

"""
import os
import json
import autogen
import chainlit as cl
from agents.robot_agent import RobotAgent
from autogen import GroupChat

async def setup_agents(temperature: float,
                        model: str,
                        output_folder: str):
    """Create Agent objects and set user session variables"""
    agent = RobotAgent(model=model)
    agent.clear_history(clear_previous_work=True)
    agent.instantiate_groupchat()

    # secondary_agent_name = agent.secondary_agent.admin_name.replace("_", " ")
    # user_proxy_name = "User Proxy"

    cl.user_session.set('agent', agent)
    cl.user_session.set("Admin", agent.groupchat)
    cl.user_session.set("User Proxy", agent.user_proxy)

async def setup_chat_settings():
    # Set up agent configuration
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="Model",
                label="Model",
                values=["gpt-3.5-turbo",  "gpt-4-1106-preview", "gpt-4"],
                initial_index=2
            ),
            cl.input_widget.Slider(id="Temperature", label="Temperature (randomness)", initial=0.9, min=0, max=2, step=0.1),
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
            "name": "Data Engineer",
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

termination_msgs = ["TERMINATE", "TERMINATE."]

async def handle_message_indentation(naming_dict):
    """
    Handles message indentation for chainlit UI components. Within
    a run of the Autogen agent conversations there may be messages inbetween
    by agents conversing amongst themselves that we may want to see.
    This sets them to an indentation level of 1, while the final response is 
    set to indentation level 0.

    There is no gaurantee that the last message in an Autogen conversation will be
    the message we want, so the function provides functionality to ommitt messages
    that are just termination messages, and removes termination messages from the 
    final response we want. 
    
    There are different types of information that we make be interested in within the message
    json keys, such as `content` and `function_call`, they need to accounted for when pulling from the message.

    The function also updates some chainlit user session values for updating the UI.
    
    """
    agent: RobotAgent = cl.user_session.get("agent")
    group_chat = agent.groupchat  # Assuming groupchat attribute is accessible

    final_response = None
    last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)
    new_message_history = group_chat.messages[last_seen_message_index:]

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
                indent=1
            ).send()

        if function_call:
            final_response = function_call
            await cl.Message(
                author=naming_dict[message["role"]],
                content=function_call,
                indent=1
            ).send()

    cl.user_session.set('last_seen_message_index', len(group_chat.messages))
    if type(final_response) == str:
        final_response = final_response.strip().replace("TERMINATE.", "").replace("TERMINATE", "")

    return final_response

async def get_response(user_message: str):
    agent: RobotAgent = cl.user_session.get("agent")
    group_chat = agent.groupchat  # Adjust based on actual class structure

    if not group_chat.messages:
        print('Initiating conversation with agent.run()')
        await cl.make_async(agent.run)(prompt=user_message)
    else:
        print('Continuing conversation with agent._continue()')
        await cl.make_async(agent._continue)(prompt=user_message)

async def send_final_response(final_response):
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
            content="Sorry, please try again. we got lost in thought...",
            indent=0
        ).send()
