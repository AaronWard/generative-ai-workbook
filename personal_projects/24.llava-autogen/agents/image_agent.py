
"""
Agent wrapper class for interacting with Image Agent
which can classify or describe images. 

Written by: Aaron Ward - 3rd December 2023
"""
import os
import sys
import json
import autogen
import logging
import base64
import requests
from agents.agent_base import AgentBase

sys.path.append("../")

class ImageAgent(AgentBase):
    """
    Agent wrapper class for intefacing with Ollama local
    models via LiteLLM.

    In this scenario, it is Llava and Mistral
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model', "mistral")
        self.instantiate_two_way_chat()

    def get_system_messages(self):
        """
        Get system messages for different agent roles.
        Returns:
            dict: A dictionary of system messages.
        """
        system_messages = {
            "USER_PROXY": (
            """
            You are an AI assistant that takes an image from the user and/or a query and passes them to the llava agent.
            If no image data is passed then just say TERMINATE.
            Say TERMINATE when no further instructions are given to indicate the task is complete.
            """
            ),
            "LAVA_SYSTEM_MESSAGE": (
            """
            You are an AI assistant that answers questions based on images. You have the ability to see what is in an image and describe it.
            Say TERMINATE when no further instructions are given to indicate the task is complete.
            """
            ),
        }

        return system_messages
    
    def instantiate_two_way_chat(self):
        logging.info("Initializing Agents")
        system_messages = self.get_system_messages()


        mistral_config_list = [
            {
                "api_key": "NULL",
                "base_url": "http://0.0.0.0:41765",
            }
        ]
        llava_config_list = [
            {
                "api_key": "NULL",
                "base_url": "http://0.0.0.0:8181",
            }
        ]
    

        llava_agent = autogen.AssistantAgent(
            name="llava_model",
            llm_config={
                "temperature": 0,
                "config_list": llava_config_list,
            },
            system_message=system_messages['LAVA_SYSTEM_MESSAGE']
        )

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
            code_execution_config=False,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            llm_config={
                "temperature": 0,
                "config_list": mistral_config_list,
            },
            system_message=system_messages['USER_PROXY']
        )

        self.user_proxy = user_proxy
        self.secondary_agent = llava_agent

    def encode_image_to_base64(self, image_bytes):
        encoded_string = base64.b64encode(image_bytes).decode('utf-8')
        return encoded_string

    def run(self, prompt, bytes):
        """Start a conversation"""

        if bytes:
            print("decoding...")
            bytes = self.encode_image_to_base64(bytes)
            prompt = prompt + f"\n\nHere is the base64 encoded image data: {str(bytes)}"
            print(prompt)


        if not self.user_proxy or not self.secondary_agent:
            raise ValueError(
                f"Error occurred initiating the agents {self.user_proxy}, {self.secondary_agent}")
        self.user_proxy.initiate_chat(self.secondary_agent, message=prompt)

    def _continue(self, prompt):
        """Continue previous chat"""

        if not self.user_proxy or not self.secondary_agent:
            raise ValueError(
                f"Error occurred initiating the agents {self.user_proxy}, {self.secondary_agent}")
        self.user_proxy.send(recipient=self.secondary_agent, message=prompt)
