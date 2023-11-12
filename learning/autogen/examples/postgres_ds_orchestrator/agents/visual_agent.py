"""
This class contains code for setting up a conversation initialization
with agents focused on visual tasks with eCharts

Written by: Aaron Ward - 3rd November

TODO: Updated chainlit to incorporate plotly interactive charts.
"""
import os
import sys
import autogen
import logging
from autogen import AssistantAgent, UserProxyAgent

sys.path.append("../")

from agents.agent_base import AgentBase

class VisualAgent(AgentBase):
    """
    VisualAgent class for managing Autogen chat agents and related operations
    for visual-related tasks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instantiate_visual_agents()

    def get_function_map(self):
        """
        Get a mapping of functions to their visual operation counterparts.

        Returns:
            dict: A dictionary mapping function names to visual methods.
        """
        function_map = {    
            # Define visual-related functions here. For example:
            # "generate_image": self.generate_image,
        }
        return function_map

    def get_config_common(self):
        """ Get the common configurations among all visual agents"""
        # Common configurations for visual agents
        return {
            "request_timeout": 1000,
            "seed": 42,
            "config_list": self.config_list,
            "temperature": self.temperature,
            # Define additional common configurations here
        }

    def get_system_messages(self):
        """
        Get system messages for different agent roles in visual tasks.
        Returns:
            dict: A dictionary of system messages.
        """
        system_messages = {
            "Visual_Designer": 
                "As a Visual Designer, create and provide insights on visual content.",
            # Define other roles and system messages here
        }
        return system_messages

    def instantiate_visual_agents(self):
        logging.info("Initializing Visual Agents")

        llm_config_common = self.get_config_common()
        system_messages = self.get_system_messages()

        # Define the configurations for the different visual agents here
        visual_designer_config = {
            "name": "Visual_Designer",
            "llm_config": llm_config_common,
            "system_message": system_messages["Visual_Designer"],
            # "is_termination_msg": self.is_termination_message,
            # Other configurations as needed
        }

        # Instantiate agents using the above configurations
        visual_designer = AssistantAgent(**visual_designer_config)

        # Save the instantiated agents
        self.visual_designer_agent = visual_designer
        print("Visual Agents Initiated!")

    # Define any additional methods needed for visual tasks

    def run_visual_task(self, task_description):
        """
        Initiate a visual task based on the description.
        Args:
            task_description (str): The description of the visual task to run.
        """
        # The process of running a visual task would go here
        pass

    # Implement other helper methods as needed

# Example usage
if __name__ == "__main__":
    visual_agent = VisualAgent(model='gpt-4')  # Add other arguments as needed
    task_description = "Describe the visual task here"
    visual_agent.run_visual_task(task_description)
