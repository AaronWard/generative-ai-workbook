
"""
Agent wrapper class for intefacing with the Autogen/chroma and Chainlit.

Written by: Aaron Ward - 17nd November 2023
"""
from db.db import ChromaDBManager
from agents.agent_base import AgentBase
import os
import sys
import autogen
import logging
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent

sys.path.append("../")


class ChromaAgent(AgentBase):
    """
    Agent wrapper class for intefacing with the Autogen/chroma and Chainlit.
    """

    def __init__(self, docs_path, db_path, collection_name, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model', "gpt-4-1106-preview")
        self.chroma_db_manager = ChromaDBManager(
            docs_path, db_path, collection_name, model=self.model)
        # self.chroma_db_manager.setup(clear_history=True)
        # self.chroma_db_manager.create_vector_db()
        self.instantiate_two_way_chat()

    def get_system_messages(self):
        """
        Get system messages for different agent roles.
        TODO: Move this out to it's own location as the application grows
        Returns:
            dict: A dictionary of system messages.
        """
        system_messages = {
            "RAG_ASSISTANT_SYSTEM_MESSAGE": ("""As a Retrieve-Augmented Chatbot, your role involves analyzing message history and the context to answer a question. 
            \n\n
            When a question is presented, you should:
            Step 1: Determine the user's intent by considering the question and its context. The intent might involve generating code or answering a question, or both.
            Step 2: Formulate a response based on the identified intent.
            \n\n
            For contextual understanding, use the `query_vector_db` tool to access information from the Chroma vector database. 
            Enhance your replies by integrating context extracted from the Chroma DB using the `get_context` function. 
            \n\n
            This approach will provide a well-informed basis for your responses.
            If there is relevant links in the chat logs, provide the fill link in the response.
            Only provide verifiable information, don't make assumptions. If you cannot answer the question accurately, its okay - just say you can't give a confident response.
            Give code for in your answer where appropriate while adhering to this format:
            ```language
            <code>
            ```
            If you are quoting a message directly, you should format it `>` first.
            Be concise with your answer, writing no more then 3 paragraphs.
            \n\n
            Say TERMINATE when no further instructions are given to indicate the task is complete.
            """)
        }

        return system_messages

    def get_function_map(self):
        """
        Updated function map to use ChromaDBManager's methods.
        """
        function_map = {
            "query_vector_db": self.chroma_db_manager.query_db,
            "get_context": self.chroma_db_manager.get_context
        }
        return function_map

    def instantiate_two_way_chat(self):
        logging.info("Initializing Agents")
        system_messages = self.get_system_messages()

        query_vector_db_tool_config = {
            "name": "query_vector_db",
            "description": "Function to query the Chroma vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_texts": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["query_texts"]
            }
        }

        get_context_tool_config = {
            "name": "get_context",
            "description": "Function to get the context from query results of the Chroma vector database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "results": {"type": "object"}
                },
                "required": ["results"]
            }
        }

        llm_config = {
            "config_list": self.config_list,
            "assistant_id": None,
            "tools": [
                {
                    "type": "function",
                    "function": query_vector_db_tool_config
                },
                {
                    "type": "function",
                    "function": get_context_tool_config
                }
            ],
            "model": "gpt-4-1106-preview"
        }

        sql_assistant = GPTAssistantAgent(
            name="Chroma_RAG_Assistant",
            instructions=system_messages['RAG_ASSISTANT_SYSTEM_MESSAGE'],
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
        # prompt = self.stuff_context(prompt)

        if not self.user_proxy or not self.secondary_agent:
            raise ValueError(
                f"Error occurred initiating the agents {self.user_proxy}, {self.secondary_agent}")
        self.user_proxy.initiate_chat(
            self.secondary_agent, message=prompt, clear_history=False, config_list=self.config_list)

    def _continue(self, prompt):
        """Continue previous chat"""
        # prompt = self.stuff_context(prompt)

        if not self.user_proxy or not self.secondary_agent:
            raise ValueError(
                f"Error occurred initiating the agents {self.user_proxy}, {self.secondary_agent}")
        self.user_proxy.send(recipient=self.secondary_agent, message=prompt)
