"""
Class for Langchain chain, this chain makes a request to OpenAI to provide information
in a given location and time period. 
"""
import os
import logging
from pathlib import Path
import langchain


PROMPT_STRING = """
You goal is to respond with 10 interest detailed historical facts about {location}. \n
Only provide information from around this time period, give or take a few decades: {time_period}. \n
Provide context of what was going in the region around that time. \n
Provide no filler or conversation response, just detailed bullet points.\n
You should always provide a full response. \n
If you are unsure of the history for this time period, explain that the for this area and time period 
is limited. \n\n
"""

class HistoryChain():

    def __init__(self, openai_api_key, model):
        super().__init__()
        self.openai_api_key = openai_api_key
        self.llm_chains = []  # Buffer to store LLMChain objects
        self.model = model

        # Add LLMChain objects to the buffer
        self.add_chain(self.get_history_chain())

    def add_chain(self, llm_chain):
        self.llm_chains.append(llm_chain)

    def get_template(self, input):
        # Create the first PromptTemplate
        prompt = langchain.PromptTemplate(
            input_variables=input,
            template=PROMPT_STRING
        )
        return prompt

    def get_history_chain(self):
        prompt_1 = self.get_template(input=["location", "time_period"])

        return langchain.LLMChain(llm=langchain.OpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.model), prompt=prompt_1)

    def run(self, input_text):
        
        llm_1 = self.llm_chains[0].run(input_text)

        # Return the results
        return {
            "response": llm_1,
        }