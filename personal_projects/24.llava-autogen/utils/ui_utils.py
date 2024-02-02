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

########################## Message Handling Functions ########################################

async def handle_message_step_implementation(user_message):
    """
    Handles the organization of messages using cl.Step()
    """
    agent: ImageAgent = cl.user_session.get("agent")
    # group_chat = agent.groupchat

    async with cl.Step(name="Agent Interaction") as step:
        # Add messages between agents to the step
        # Example usage, customize as per your actual logic
        step.input = user_message.content
        response = await agent.run(prompt=user_message.content)
        step.output = response

    # Send final response at root level
    await send_final_response(response)

async def get_response(user_message: str, bytes: Union[str, None]):
    """Obtain a response for the given user message and image bytes if applicable"""
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

async def send_final_response(final_response):
    """Send the final response to the user at root level"""
    if final_response:
        await cl.Message(author="chatbot", content=final_response).send()
    else:
        await cl.Message(author="chatbot", content="Sorry, please try again. We got lost in thought...").send()