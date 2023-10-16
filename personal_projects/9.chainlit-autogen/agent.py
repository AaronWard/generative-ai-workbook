"""
This class contains code for setting up a conversation initialization
with agents. It includes the use of Autogens Assistant agent for writing
code and User Proxy agent for executing actions.

Written by: Aaron Ward - October 2023
"""
import os
import time
import shutil
import autogen
import logging
import pprint as pp
import streamlit as st 
import chainlit as cl
from pathlib import Path
from datetime import datetime
from multiprocessing import Process, Queue
from autogen import AssistantAgent, UserProxyAgent

import json

class MultiAgent():
    """
    StreamlitAgent class for managing Autogen chat agents and related operations.
    """

    def __init__(self, **kwargs):
        """
        Initialize StreamlitAgent with coding assistant and runner agents.
        """
        # self.model  = kwargs.get('model', 'gpt-3.5-turbo')
        self.model  = kwargs.get('model', 'gpt-4')
        self.work_dir = kwargs.get('work_dir', None)
        self.temperature = kwargs.get('temperature', 0.2)
        self.env_path = '../../.env'
        self.config_list = self.get_config_list()


    def clear_history(self, clear_previous_work=False):
        """
        Clean up the cache directory to avoid conversation spillover between models.

        Args:
            clear_previous_work (bool, optional): Whether to clear the previous work directory. Defaults to True.
        """
        if os.path.exists('.cache') and os.path.isdir('.cache'):
            print('Deleting cache...')
            shutil.rmtree('.cache')

        if clear_previous_work:
            self.clear_previous_work()

    def clear_previous_work(self):
        """
        Clean up the previous work directory.
        """
        if os.path.exists('.coding') and os.path.isdir('.coding'):
            print('Deleting previous work...')
            shutil.rmtree('.coding')

    def get_config_list(self):
        """
        Get a list of configuration options for Autogen.

        Returns:
            list: List of configuration options.
        """
        # For open sources models
        # config_list = [
        #     {
        #         "model": "ollama/mistral",
        #         # "model": "ollama/llama2",
        #         "api_base": "http://0.0.0.0:8001",
        #         "api_type": "litellm"
        #     }
        # ]

        config_list = autogen.config_list_from_dotenv(
            dotenv_file_path=self.env_path,
            model_api_key_map={
                "gpt-4": "OPENAI_API_KEY",
                "gpt-3.5-turbo": "OPENAI_API_KEY",
            },
            filter_dict={
                "model": {
                    # self.model,
                    "gpt-4"
                }
            }
        )
        return config_list
    
    def instiate_agents(self):
        logging.info("Initializing Agents")
        coding_assistant_config = {
                "name": "coding_assistant",
                "llm_config": {
                    "request_timeout": 1000,
                    "seed": 42,
                    "config_list": self.config_list, 
                    "temperature": self.temperature,
                }
        }
        coding_runner_config = {
                "name": "coding_runner",
                "human_input_mode": "NEVER",
                "max_consecutive_auto_reply": 5,
                "is_termination_msg": self.is_termination_message,
                "code_execution_config": {
                    "work_dir": self.work_dir,
                    "use_docker": False
                },
                "llm_config": {
                    "request_timeout": 1000,
                    "seed": 42,
                    "config_list": self.config_list,
                    "temperature": self.temperature,
                },
        }

        coding_assistant = AssistantAgent(**coding_assistant_config)
        coding_runner = UserProxyAgent(**coding_runner_config)

        return coding_assistant, coding_runner

    def is_termination_message(self, x):
        return x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")
    
