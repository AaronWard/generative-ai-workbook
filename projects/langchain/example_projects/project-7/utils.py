'''
Creating an agents from the lanchain
agents module to query a dataframe.

'''
import pandas as pd
from langchain.llms import OpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

def query_agent(data, query):

    # Parse the CSV file and create a Pandas DataFrame from its contents.
    df = pd.read_csv(data)

    llm = OpenAI(model='text-davinci-003', temperature=0.8)
    
    # Create a Pandas DataFrame agent.
    agent = create_pandas_dataframe_agent(llm, df, verbose=True)


    # agent = create_pandas_dataframe_agent(
    #     ChatOpenAI(temperature=0, model="gpt-4", endpoint="v1/chat/completions"),
    #     df,
    #     verbose=True,
    #     agent_type=AgentType.OPENAI_FUNCTIONS,
    # )

    #Python REPL: A Python shell used to evaluating and executing Python commands. 
    #It takes python code as input and outputs the result. The input python code can be generated from another tool in the LangChain
    return agent.run(query)