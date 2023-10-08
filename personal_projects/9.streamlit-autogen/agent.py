import os
import shutil
import autogen
import logging
import threading
import streamlit as st 
from pathlib import Path
from multiprocessing import Process, Queue
from autogen import AssistantAgent, UserProxyAgent

logging.basicConfig(level=logging.INFO)

class StreamlitAgent():
    """
    StreamlitAgent class for managing Autogen chat agents and related operations.
    """

    def __init__(self, **kwargs):
        """
        Initialize StreamlitAgent with coding assistant and runner agents.
        """
        self.config_list = self.get_config_list()

    def clear_cache(self, clear_previous_work=True):
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
        config_list = autogen.config_list_from_dotenv(
            dotenv_file_path='../../.env',
            model_api_key_map={
                "gpt-4": "OPENAI_API_KEY",
                # "huggingface/mistralai/Mistral-7B-v0.1": "HUGGINGFACE_HUB",
            },
            filter_dict={
                "model": {
                    "gpt-4",
                    # "huggingface/mistralai/Mistral-7B-v0.1",
                }
            }
        )
        return config_list
    
    @staticmethod
    def _chat_target(coding_assistant_config, coding_runner_config, config_list, message, queue, callback):
        try:
            logging.info("Starting chat target")
            coding_assistant = AssistantAgent(**coding_assistant_config)
            coding_runner = UserProxyAgent(**coding_runner_config)

            logging.info(f"Sending message: {message}")
            # Wrap message into a dictionary
            coding_runner.initiate_chat(coding_assistant, message=message, config_list=config_list)

            runner_msg = coding_runner.last_message(coding_assistant)
            assistant_msg = coding_assistant.last_message(coding_runner)

            logging.info(f"Runner message: {runner_msg}, Assistant message: {assistant_msg}")
            queue.put((runner_msg, assistant_msg))
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}", exc_info=True)
            queue.put((f"Error: {str(e)}", f"Error: {str(e)}"))


    def is_termination_message(self, x):
        return x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")

    def run_in_process(self, message, callback):
        """
        Run initiate_chat in a separate process to avoid blocking.
        """
        queue = Queue()

        process = Process( # process_target()?
            target=self._chat_target,
            args=(
                {
                    "name": "coding_assistant",
                    "llm_config": {
                        "request_timeout": 1000,
                        "seed": 42,
                        "config_list": self.config_list, 
                        "temperature": 0.8,
                    }
                },
                {
                    "name": "coding_runner",
                    "human_input_mode": "NEVER",
                    "max_consecutive_auto_reply": 20,
                    "is_termination_msg": self.is_termination_message,
                    "code_execution_config": {
                        "work_dir": "coding",
                        "use_docker": False
                    },
                    "llm_config": {
                        "request_timeout": 1000,
                        "seed": 42,
                        "config_list": self.config_list,
                        "temperature": 0.4,
                    },
                },
                self.config_list,
                message,
                queue,
                None
            )
        )
        process.start()
        # process.join()
        
        # Get messages from queue
        runner_msg, assistant_msg = queue.get()        
        # Update UI with messages
        callback(runner_msg, assistant_msg)

    def run(self, message, callback):
        """
        Run Autogen chat with the coding_runner agent.
        """
        self.run_in_process(message, callback)