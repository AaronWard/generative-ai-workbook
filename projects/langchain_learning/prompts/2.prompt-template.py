"""
https://python.langchain.com/en/latest/modules/prompts/prompt_templates/getting_started.html

"""
from langchain import PromptTemplate


prompt_example = PromptTemplate(
        input_variables=["name"],
        template=
"""Hello There {name}
"""
)

print(prompt_example.format(name="John"))
