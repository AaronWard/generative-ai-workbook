
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
    Agent wrapper class for intefacing with the Autogen/chroma and Chainlit.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model', "gpt-4-1106-preview")

    # def get_group_chat_messages(self):
    #     """Returns the messages from the group chat."""
    #     return self.groupchat.messages

    def get_system_messages(self):
        """
        Get system messages for different agent roles.
        Returns:
            dict: A dictionary of system messages.
        """
        system_messages = {
            "USER_PROXY_SYSTEM_MESSAGE": (
                """

                """
            ),
            "LAVA_SYSTEM_MESSAGE": (
                """
                
                """
            ),
        }

        return system_messages

    def get_function_map(self):
        """
        """
        pass
        # function_map = {
        #     "send_action": self.robot_motion_manager.send_action,
        # }
        # return function_map
    
    def instantiate_groupchat(self):
        print("Agents Initiated!")

    def stuff_context(self, prompt):
        # Context stuffing
        termination_notice = self.get_additional_termination_notice()

        # Convert to string if 'text' attribute is not found
        prompt_text = prompt.text if hasattr(prompt, 'text') else str(prompt)
        prompt = prompt_text + f"\n\n{termination_notice}"

        return prompt

    def encode_image_to_base64(self, image_bytes):
        encoded_string = base64.b64encode(image_bytes).decode('utf-8')
        return encoded_string

    def run(self, prompt, bytes):
        """Start a conversation"""
        # if bytes:
        #     bytes = self.encode_image_to_base64(bytes)

        # data = {
        #     "model": "llava:34b",
        #     "prompt": f"{prompt}",
        #     "stream": False,
        #     "images": [bytes]
        # }

        # # Send the POST request
        # url = "http://127.0.0.1:5050/api/generate"
        # response = requests.post(url, data=json.dumps(data))
        # print(response.json())
        # return response.json()['content']

        print('hello')
        return "hello!!!"

    def _continue(self, prompt):
        """Continue previous chat"""
        pass
