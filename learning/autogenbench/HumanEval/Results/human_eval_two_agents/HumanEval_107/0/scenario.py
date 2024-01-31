import os
import json
import base64
import testbed_utils
import autogen

# NOTE:
# This scenario runs Human Eval in a slightly unconventional way:
# The agents have access to the unit tests, and can keep trying
# until they pass.

testbed_utils.init()
##############################

work_dir = "coding"

# Read the prompt
PROMPT = ""
with open("prompt.txt", "rt") as fh:
    PROMPT = fh.read()

# Ok, now get autogen to solve it.
config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")

assistant = autogen.AssistantAgent(
    "assistant",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=testbed_utils.default_llm_config(config_list, timeout=180),
)

user_proxy = autogen.UserProxyAgent(
    "user_proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "work_dir": work_dir,
        "use_docker": False,
    },
    max_consecutive_auto_reply=10,
    default_auto_reply="TERMINATE",
)

user_proxy.initiate_chat(
    assistant,
    message="""
The following python code imports the `run_tests(candidate)` function from my_tests.py, and runs
it on the function `even_odd_palindrome`. This will run a set of automated unit tests to verify the
correct implementation of `even_odd_palindrome`. However, `even_odd_palindrome` is only partially
implemented in the code below. Complete the implementation of `even_odd_palindrome` and output
a new stand-alone code block that contains everything needed to run the tests, including: importing
`my_tests`, calling `run_tests(even_odd_palindrome)`, as well as even_odd_palindrome's complete definition,
such that this code block can be run directly in Python.

```python
from my_tests import run_tests

"""
    + PROMPT
    + """

# Run the unit tests
run_tests(even_odd_palindrome)
```
""",
)

##############################
testbed_utils.finalize(agents=[assistant, user_proxy])
