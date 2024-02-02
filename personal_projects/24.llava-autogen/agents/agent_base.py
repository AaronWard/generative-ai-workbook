
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
        self.model = kwargs.get('model', 'mistral')
        self.work_dir = kwargs.get('work_dir', "_output")
        self.cache_dir = kwargs.get('cache_dir', ".cache")
        self.temperature = kwargs.get('temperature', 0.2)
        # self.env_path = "../../../.env"
        # self.config_list = self.get_config_list()
        self.user_proxy = None
        self.secondary_agent = None

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
            'to indicate the conversation is finished'
            # "Say TERMINATE when no further instructions are given to indicate the task is complete"
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
