"""
https://python.langchain.com/en/latest/modules/models/llms/getting_started.html

"""

from dotenv import find_dotenv, load_dotenv
from langchain.llms import OpenAI

# Load environment variables
load_dotenv(find_dotenv())

llm = OpenAI(model_name="text-davinci-003")
prompt = "Write a poem about python and ai"
print(llm(prompt))