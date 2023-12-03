
"""
Agent wrapper class for intefacing with the Autogen
using the RobotMotionManager to interface with the raspberry
pi robot. 

Written by: Aaron Ward - 3rd December 2023
"""
import os
import sys
import autogen
import logging

from robot.managers.robot_motion_manager import RobotMotionManager
from agents.agent_base import AgentBase

from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent

sys.path.append("../")

class RobotAgent(AgentBase):
    """
    Agent wrapper class for intefacing with the Autogen/chroma and Chainlit.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model', "gpt-4-1106-preview")
        self.robot_motion_manager = RobotMotionManager(model=self.model)

        self.instantiate_two_way_chat()

    def get_system_messages(self):
        """
        Get system messages for different agent roles.
        Returns:
            dict: A dictionary of system messages.
        """
        system_messages = {
            "USER_PROXY_SYSTEM_MESSAGE": (
                """
                You are an AI assistant to interface with a rasberry pi robot. Your job is to act as an AI interface between the human use and the AI robot agents

                End your process with `TERMINATE` when no further instructions are given, to indicate that the task is complete.
                """
            ),
            "ROBOT_PLANNER_SYSTEM_MESSAGE": (
                """
                You are part of a Raspberry pi humanoid robot,your role involves understanding instructions and planning steps for the robot to take.
                You can choose from any of the following list of possible actions you can perform:
                ```
                0 - Stretch your arms
                back_end - Back End
                back_fast - Back Fast
                back_one_step - Back One Step
                back_start - Back Start
                back - Back
                bow - Bow
                chest - Chest
                go_forward_end - Go Forward End
                go_forward_fast - Go Forward Fast
                go_forward_one_small_step - Go Forward One Small Step
                go_forward_one_step - Go Forward One Step
                go_forward_slow - Go Forward Slow
                go_forward_start_fast - Go Forward Start Fast
                go_forward_start - Go Forward Start
                go_forward - Go Forward
                left_kick - Left Kick
                left_move_10 - Left Move 10
                left_move_20 - Left Move 20
                left_move_30 - Left Move 30
                left_move - Left Move
                left_move_fast - Left Move Fast
                left_shot_fast - Left Shot Fast
                left_shot - Left Shot
                left_uppercut - Left Uppercut
                move_up - Move Up
                put_down - Put Down
                right_kick - Right Kick
                right_move_10 - Right Move 10
                right_move_20 - Right Move 20
                right_move_30 - Right Move 30
                right_move - Right Move
                right_move_fast - Right Move Fast
                right_shot_fast - Right Shot Fast
                right_shot - Right Shot
                right_uppercut - Right Uppercut
                sit_ups - Sit Ups
                squat - Squat
                stand_slow - Stand Slow
                stand_up_back - Stand Up Back
                stand_up_front - Stand Up Front
                stand - Stand
                stepping - Stepping
                turn_left_fast - Turn Left Fast
                turn_left_small_step - Turn Left Small Step
                turn_left - Turn Left
                turn_right_fast - Turn Right Fast
                turn_right_small_step - Turn Right Small Step
                turn_right - Turn Right
                twist - Twist
                wave - Wave
                wing_chun - Wing Chun
                t-pose - stand in a t-pose position
                kneel_down - Sit in a kneeling down position.
                ```

                When you receive a command, follow these steps:
                    1. Identify the User's Intent: Understand the command and its context. The intent might involve moving the robot, manipulating objects, or gathering information.
                    2. You come up with a logical plan to achieve what has been instructed with the given actions from the list. You are free to use any combination of these to achieve your goal.
                
                You send your plan to Robot_Motion_Assistant, who runs each action one by one in the command line.
                For example, if you sending a single action:
                ```
                # User asked for you to wave
                Actions: wave
                ```
                For example, if you sending a multiple actions:
                ```
                # User asked for you to stand up and t-pose, then kneel down
                Actions: t-pose, kneel_down
                ```
                
                End your process with `TERMINATE` when no further instructions are given, to indicate that the task is complete.
                """
            ),
            "ROBOT_ASSISTANT_SYSTEM_MESSAGE": (
                """
                You are part of a Raspberry pi humanoid robot, your role involves understanding instructions and executing actions through the robot body, by running code. 
                You take instructions from Robot_Action_Planner and run them in the exact order specified.

                For example, Robot_Action_Planner asks for you to stand up and t-pose, then kneel down:
                ```
                Actions: t-pose, kneel_down
                ```

                Key Points to Remember:
                - Utilize Context: If the command relates to previous actions or instructions, take that into account to make informed decisions.
                - Tools: You pass the action name to `send_action()` function as a string. If multiple instructions are given, run them in order and don't respond until the tasks are finished.

                For example:
                ```
                > send_action(command="t-pose")
                > send_action(command="kneel_down")
                ...
                ```

                End your process with `TERMINATE` when no further instructions are given, to indicate that the task is complete.
                """
            )
        }

        return system_messages

    def get_function_map(self):
        """
        Updated function map to use RobotMotionManager's methods.
        """
        function_map = {
            "send_action": self.robot_motion_manager.send_action,
        }
        return function_map
    


    def instantiate_groupchat(self):
        # Load system messages
        system_messages = self.get_system_messages()

        # Configurations
        send_action_tool_config = {
            "name": "send_action",
            "description": "Function to send an action group name to command the raspberry pi robot",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"]
            }
        }

        llm_config = {
            "config_list": self.config_list,
            "assistant_id": None,
            "tools": [
                {
                    "type": "function",
                    "function": send_action_tool_config
                },
            ],
            "model": "gpt-4-1106-preview"
        }

        # Initiate agents
        robot_action_assistant = GPTAssistantAgent(
            name="Robot_Motion_Assistant",
            instructions=system_messages['ROBOT_ASSISTANT_SYSTEM_MESSAGE'],
            llm_config=llm_config
        )

        robot_action_assistant.register_function(
            function_map=self.get_function_map()
        )

        robot_action_planner_config = {
            "name": "Robot_Action_Planner",
            "llm_config": llm_config,
            "system_message": system_messages["ROBOT_PLANNER_SYSTEM_MESSAGE"],
            "code_execution_config": False,
            "human_input_mode": "NEVER",
            # "is_termination_msg": self.is_termination_message,
        }

        robot_action_planner = autogen.AssistantAgent(**robot_action_planner_config)

        # Instantiate agents using the above configurations
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            system_message=system_messages["USER_PROXY_SYSTEM_MESSAGE"],
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
            code_execution_config=False,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

        # Instantiate group chat and manager
        groupchat_user_proxy = autogen.GroupChat(agents=[user_proxy, robot_action_planner, robot_action_assistant], messages=[], max_round=50)
        groupchat_manager = autogen.GroupChatManager(groupchat=groupchat_user_proxy, llm_config=llm_config)

        self.groupchat_user_proxy = groupchat_user_proxy
        self.groupchat_secondary_agent = groupchat_manager
        print("Agents Initiated!")


    def instantiate_two_way_chat(self):
        logging.info("Initializing Agents")
        system_messages = self.get_system_messages()

        send_action_tool_config = {
            "name": "send_action",
            "description": "Function to send an action group name to command the raspberry pi robot",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"]
            }
        }

        llm_config = {
            "config_list": self.config_list,
            "assistant_id": None,
            "tools": [
                {
                    "type": "function",
                    "function": send_action_tool_config
                },
            ],
            "model": "gpt-4-1106-preview"
        }

        sql_assistant = GPTAssistantAgent(
            name="Robot_Motion_Assistant",
            instructions=system_messages['ROBOT_ASSISTANT_SYSTEM_MESSAGE'],
            llm_config=llm_config
        )

        sql_assistant.register_function(
            function_map=self.get_function_map()
        )

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
            code_execution_config=False,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

        self.user_proxy = user_proxy
        self.secondary_agent = sql_assistant

    def stuff_context(self, prompt):
        # Context stuffing
        termination_notice = self.get_additional_termination_notice()

        # Convert to string if 'text' attribute is not found
        prompt_text = prompt.text if hasattr(prompt, 'text') else str(prompt)
        prompt = prompt_text + f"\n\n{termination_notice}"

        return prompt

    def run(self, prompt):
        """Initiate a chat"""
        # if not self.user_proxy or not self.secondary_agent:
        #     raise ValueError(
        #         f"Error occurred initiating the agents {self.user_proxy}, {self.secondary_agent}")
        # self.user_proxy.initiate_chat(
        #     self.secondary_agent, message=prompt, clear_history=False, config_list=self.config_list)

        if not self.groupchat_user_proxy or not self.groupchat_secondary_agent:
            raise ValueError(f"Error occurred initiating the agents {self.groupchat_user_proxy}, {self.groupchat_secondary_agent}")
        self.groupchat_user_proxy.initiate_chat(
            self.groupchat_secondary_agent, message=prompt, clear_history=False, config_list=self.config_list)

    def _continue(self, prompt):
        """Continue previous chat"""
        # if not self.user_proxy or not self.secondary_agent:
        #     raise ValueError(
        #         f"Error occurred initiating the agents {self.user_proxy}, {self.secondary_agent}")
        # self.user_proxy.send(recipient=self.secondary_agent, message=prompt)

        if not self.groupchat_user_proxy or not self.groupchat_secondary_agent:
            raise ValueError(f"Error occurred initiating the agents {self.groupchat_user_proxy}, {self.groupchat_secondary_agent}")
        self.groupchat_user_proxy.send(recipient=self.groupchat_secondary_agent, message=prompt)
