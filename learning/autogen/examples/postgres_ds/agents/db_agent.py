
"""
This class contains code for setting up a conversation initialization
with agents. It includes the use of Autogens Assistant agent for writing
code and User Proxy agent for executing actions.

Written by: Aaron Ward - 2nd November 2023
"""
import os
import sys
import autogen
import logging
from autogen import AssistantAgent, UserProxyAgent

sys.path.append("../")

from agents.agent_base import AgentBase
from data.db import PostgresManager

class DBAgent(AgentBase):
    """
    StreamlitAgent class for managing Autogen chat agents and related operations.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_conn_var = kwargs.get('db_conn_var', "POSTGRES_CONNECTION_URL")
        self.db = self.connect_to_db(os.environ.get(self.db_conn_var))
        
        # Initiate the agents on creation
        self.instantiate_groupchat()
        self.instantiate_two_way_chat()

    def connect_to_db(self, db_url):
        """
        connect to database on initalization.
        """
        if not db_url:
            raise ValueError("No db_url passed.")
        db = PostgresManager()
        db.connect_with_url(db_url)
        return db

    def get_table_definitions_for_prompt(self):
        """ Return the table defitions"""
        return self.db.get_table_definitions_for_prompt()

    def get_function_map(self):
        """""
        Get a mapping of functions to their database operation counterparts.

        Returns:
            dict: A dictionary mapping function names to database methods.
        """
        function_map = {    
            "run_sql": self.db.run_sql,
        }
        return function_map

    def get_config_common(self):
        """ Get the common confirugations among all agents"""
        return {
            "request_timeout": 1000,
            "seed": 42,
            # "use_cache": False, # 
            "config_list": self.config_list,
            "temperature": self.temperature,
            "functions": [
                {
                "name": "run_sql",
                "description": "Run a SQL query against the postgres database",
                "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": "The SQL query to run"
                            }
                        },
                        "required": ["sql"]
                    }
                }
            ]
        }

    def get_system_messages(self):
        """
        Get system messages for different agent roles.
        TODO: Move this out to it's own location as the application grows
        Returns:
            dict: A dictionary of system messages.
        """
        system_messages = {
            "Senior_Data_Analyst": 
                "Senior Data Analyst. You follow an approval plan. You run the SQL query. Generate the final response and send it to the Product Manager for review.",
            "Admin": 
                "A human admin. Interact with the Product Manager to discuss the plan. Plan execution needs to be approved by this admin.",
            "Data_Engineer": 
                "Data Engineer. You follow an approval plan. Think about and generate SQL based on the requirements provided. Send it out for review.",
            "Senior_Data_Analyst": 
                "Senior Data Analyst. You follow an approval plan. You run the SQL query. Generate the final response and send it to the Product Manager for review.",
            "Product_Manager": 
                "Product Manager. Validate the response to ensure it's correct.",
        }

        return system_messages

    def instantiate_two_way_chat(self):
        logging.info("Initializing Agents")

        llm_config_common = self.get_config_common()
        system_messages = self.get_system_messages()

        user_proxy_config = {
            "name": "User_Proxy",
            "code_execution_config": {
                    "work_dir": self.work_dir,
                    "use_docker": False
                },
            "human_input_mode": "NEVER",
            # "is_termination_msg": self.is_termination_message,
            "llm_config": llm_config_common,
            "function_map": self.get_function_map()
        }

        data_engineer_config = {
            "name": "Data_Engineer",
            "llm_config": llm_config_common,
            "system_message": system_messages["Data_Engineer"],
            "code_execution_config": False,
            "human_input_mode": "NEVER",
            # "is_termination_msg": self.is_termination_message,
        }

        user_proxy = UserProxyAgent(**user_proxy_config)
        data_engineer = AssistantAgent(**data_engineer_config)

        self.two_way_user_proxy = user_proxy
        self.two_way_secondary_agent = data_engineer
        print("Agents Initiated!")

    def instantiate_groupchat(self):
        # TODO: Ramblings of a mad man, but imagine
        # you could pass this function to a conversation
        # and allow the agents to spin off their own sub agent conversations
        # if they need to create a spin off task using different agents.
        logging.info("Initializing Agents")

        llm_config_common = self.get_config_common()
        system_messages = self.get_system_messages()

        user_proxy_config = {
            "name": "Admin",
            "system_message": system_messages["Admin"],
            "code_execution_config": False,
            "human_input_mode": "NEVER",
            # "is_termination_msg": self.is_termination_message,
        }
        data_engineer_config = {
            "name": "Data_Engineer",
            "llm_config": llm_config_common,
            "system_message": system_messages["Data_Engineer"],
            "code_execution_config": False,
            "human_input_mode": "NEVER",
            # "is_termination_msg": self.is_termination_message,
        }
        senior_data_analyst_config = {
            "name": "Senior_Data_Analyst",
            "system_message": system_messages["Senior_Data_Analyst"],
            "human_input_mode": "NEVER",
            "code_execution_config": {
                "work_dir": self.work_dir
            },
            # "is_termination_msg": self.is_termination_message,
            "function_map": self.get_function_map()
        }
        product_manager = {
            "name": "Product_Manager",
            "llm_config": llm_config_common,
            "system_message": system_messages["Product_Manager"],
            "code_execution_config": False,
            "human_input_mode": "NEVER",
            # "is_termination_msg": self.is_termination_message,
        }

        # Instantiate agents using the above configurations
        user_proxy = autogen.UserProxyAgent(**user_proxy_config)
        data_engineer = autogen.AssistantAgent(**data_engineer_config)
        senior_data_analyst = autogen.AssistantAgent(**senior_data_analyst_config)
        product_manager = autogen.AssistantAgent(**product_manager)

        # Instantiate group chat and manager
        groupchat_user_proxy = autogen.GroupChat(agents=[user_proxy, data_engineer, product_manager, senior_data_analyst], messages=[], max_round=50)
        groupchat_manager = autogen.GroupChatManager(groupchat=groupchat_user_proxy, llm_config=llm_config_common)

        self.groupchat_user_proxy = groupchat_user_proxy
        self.groupchat_secondary_agent = groupchat_manager
        print("Agents Initiated!")

    def stuff_context(self, prompt):
        # Context stuffing
        table_defitions = self.get_table_definitions_for_prompt()
        termination_notice = self.get_additional_termination_notice()
        
        prompt = prompt + f"\n\n{termination_notice}"
        prompt = prompt + f"\n\nUse these table defitions: {table_defitions}"

        return prompt

    def run(self, problem_type, prompt):
        """Initiate a chat"""
        prompt = self.stuff_context(prompt)
        
        if problem_type == "COMPLEX":
            if not self.groupchat_user_proxy or not self.groupchat_secondary_agent:
                raise ValueError(f"Error occurred initiating the agents {self.groupchat_user_proxy}, {self.groupchat_secondary_agent} -  problem type: {problem_type}")
            self.groupchat_user_proxy.initiate_chat(self.groupchat_secondary_agent, message=prompt, clear_history=False, config_list=self.config_list)
        elif problem_type == "SIMPLE":
            if not self.two_way_user_proxy or not self.two_way_secondary_agent:
                raise ValueError(f"Error occurred initiating the agents {self.two_way_user_proxy}, {self.two_way_secondary_agent} -  problem type: {problem_type}")
            self.two_way_user_proxy.initiate_chat(self.two_way_secondary_agent, message=prompt, clear_history=False, config_list=self.config_list)

    def _continue(self, problem_type, prompt):
        """Continue previous chat"""
        prompt = self.stuff_context(prompt)

        if problem_type == "COMPLEX":
            if not self.groupchat_user_proxy or not self.groupchat_secondary_agent:
                raise ValueError(f"Error occurred initiating the agents {self.groupchat_user_proxy}, {self.groupchat_secondary_agent} -  problem type: {problem_type}")
            self.groupchat_user_proxy.send(recipient=self.groupchat_secondary_agent, message=prompt)
        elif problem_type == "SIMPLE":
            if not self.two_way_user_proxy or not self.two_way_secondary_agent:
                raise ValueError(f"Error occurred initiating the agents {self.two_way_user_proxy}, {self.two_way_secondary_agent} -  problem type: {problem_type}")
            self.two_way_user_proxy.send(recipient=self.two_way_secondary_agent, message=prompt)

