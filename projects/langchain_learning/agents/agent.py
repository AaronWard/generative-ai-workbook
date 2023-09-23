"""
Agent - Agents use an LLM to determine which actions to take and in what order. 
An action can either be using a tool and observing its output, or returning to the user.

Tool: 
    A function that performs a specific duty. 
    This can be things like: Google Search, Database lookup, Python REPL, other chains. 
    The interface for a tool is currently a function that is expected to have a string as an input, 
    with a string as an output.
LLM: 
    The language model powering the agent.
Agent: 
    The agent to use. This should be a string that references a support agent class.
    Because this notebook focuses on the simplest, highest level API, this only covers 
    using the standard supported agents. If you want to implement a custom agent, see 
    the documentation for custom agents (coming soon).

---------------

https://python.langchain.com/en/latest/modules/agents/tools.html?highlight=tools

List of Tools
- python_repl - A Python shell. Use this to execute python commands. 
            Input should be a valid python command. If you expect output it should be printed out.
- serpapi [Complete] - A search engine. Useful for when you need to answer questions about current events. 
            Input should be a search query.
- wolfram-alpha [Complete] - A wolfram alpha search engine. 
            Useful for when you need to answer questions about Math, Science, Technology, Culture, Society and Everyday Life. 
            Input should be a search query.
- requests - A portal to the internet. Use this when you need to get specific content from a site. 
            Input should be a specific url, and the output will be all the text on that page.
- terminal - Executes commands in a terminal. Input should be valid commands, and the output will 
            be any output from running that command.
- pal-math - A language model that is excellent at solving complex word math problems. 
            Input should be a fully worded hard word math problem.
- pal-colored-objects - A language model that is wonderful at reasoning about position and the color 
            attributes of objects. Input should be a fully worded hard reasoning problem. Make sure to include all 
            information about the objects AND the final question you want to answer.
- llm-math - Useful for when you need to answer questions about math.
- open-meteo-api - Useful for when you want to get weather information from the OpenMeteo API. 
            The input should be a question in natural language that this API can answer.
- news-api - Use this when you want to get information about the top headlines of current news stories. 
            The input should be a question in natural language that this API can answer.
- tmdb-api - Useful for when you want to get information from The Movie Database. 
            The input should be a question in natural language that this API can answer.
- google-search - A wrapper around Google Search. Useful for when you need to answer 
            questions about current events. Input should be a search query.
    
https://www.youtube.com/watch?v=Jq9Sf68ozk0

"""

import os 
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.tools.file_management.write import WriteFileTool

load_dotenv(Path('./.env'))
os.environ['SERPAPI_API_KEY'] = os.getenv('SERPER_API_KEY')

llm = OpenAI(temperature=0)

tool_names = ['serpapi']
tools = load_tools(tool_names)


agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
answer = agent.run("How can i write code to make an ARIMA model using pdarima? Only provide the code in your final answer. \
                   Make sure the code is complete and runnable.")

print(answer)

'''
> Entering new AgentExecutor chain...
 I need to find the code for an ARIMA model using pdarima.
Action: Search
Action Input: "ARIMA model using pdarima code"
Observation: The auto-ARIMA process seeks to identify the most optimal parameters for an ARIMA model, settling on a single fitted ARIMA model. This process is based on the ...
Thought: I need to find the code for the auto-ARIMA process.
Action: Search
Action Input: "auto-ARIMA process code"
Observation: Auto ARIMA takes into account the AIC and BIC values generated (as you can see in the code) to determine the best combination of parameters. AIC (Akaike Information Criterion) and BIC (Bayesian Information Criterion) values are estimators to compare models.
Thought: I need to find the code for the AIC and BIC values.
Action: Search
Action Input: "AIC and BIC values code"
Observation: In this case, the BIC is reported to be a value of about -450.020, which is very close to the AIC value of -451.616. Again, this value can be ...
Thought: I now know the code for the ARIMA model using pdarima.
Final Answer:

import pmdarima as pm

# Fit auto_arima function to Airline dataset
model = pm.auto_arima(data, start_p=1, start_q=1,
                      test='adf',
                      max_p=3, max_q=3, m=12,
                      start_P=0, seasonal=True,
                      d=None, D=1, trace=True,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)

print(model.summary())

> Finished chain.
'''

# Write the output to a python file
with open('./output.py', 'w') as f:
    f.write(answer)