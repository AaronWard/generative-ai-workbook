
"""
This script is contains helper functions
related to autogen. Update initiate_agents
with the appropriate agents interaction scenario to evaluate.

Written by: Aaron Ward - 2nd November 2023
"""


import os
import sys
import shutil
import logging
import autogen
from autogen import AssistantAgent, UserProxyAgent
sys.path.append('../')


class AgentBase():
    """
    Base class for managing Autogen chat agents and related operations.
    """

    def __init__(self, **kwargs):
        """
        Initialize AgentBase with common configurations.
        """
        self.model = kwargs.get('model', 'gpt-4')
        self.work_dir = kwargs.get('work_dir', "_output")
        self.cache_dir = kwargs.get('cache_dir', ".cache")
        self.temperature = kwargs.get('temperature', 0.2)
        self.env_path = '../../../../.env'
        self.config_list = self.get_config_list()
        self.two_way_user_proxy = None
        self.two_way_secondary_agent = None
        self.groupchat_user_proxy = None
        self.groupchat_secondary_agent = None

    def get_config_list(self):
        """
        Get a list of configuration options for Autogen.

        Returns:
            list: List of configuration options.
        """
        config_list = autogen.config_list_from_dotenv(
            dotenv_file_path=self.env_path,
            model_api_key_map={
                "gpt-4": "OPENAI_API_KEY",
                "gpt-3.5-turbo": "OPENAI_API_KEY",
            },
            filter_dict={
                "model": {self.model}
            }
        )

        if not config_list:
            raise ValueError("Config list wasn't set, check configurations.")
        logging.info("Models to use: %s", [c["model"] for c in config_list])
        return config_list




    def is_termination_message(self, message):
        """
        Determine if a message signifies termination.

        Args:
            message (dict): A message dictionary.

        Returns:
            bool: True if the message is a termination message, False otherwise.
        """
        return message.get("content", "").rstrip().endswith("TERMINATE")

    def get_additional_termination_notice(self):
        """Extra instructions for terminating when goal is finished."""
        termination_notice = (
            '\n\nDo not show appreciation in your responses, say only what is necessary. '
            'if "Thank you" or "You\'re welcome" are said in the conversation, then say TERMINATE '
            'to indicate the conversation is finished and this is your last message.'
        )
        return termination_notice

    def clear_history(self, clear_previous_work=False):
        """
        Clean up the cache directory to avoid conversation spillover between models.

        Args:
            clear_previous_work (bool, optional): Whether to clear the previous work directory. Defaults to True.
        """
        if os.path.exists(self.cache_dir) and os.path.isdir(self.cache_dir):
            print('Deleting cache...')
            shutil.rmtree(self.cache_dir)

        if clear_previous_work:
            self.clear_previous_work()

    def clear_previous_work(self):
        """
        Clean up the previous work directory.
        """
        if os.path.exists(self.work_dir) and os.path.isdir(self.work_dir):
            print('Deleting previous work...')
            shutil.rmtree(self.work_dir)
