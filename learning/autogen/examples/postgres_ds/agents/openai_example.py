"""
OpenAI API Example for simple chaining.
(not used in final implementation)
"""

import os
import sys

sys.path.append("../")

from utils import api_utils
from data.db import PostgresManager

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SQL_DELIMETER = "---------"
RESPONSE_FORMAT_CAP_REF = "RESPONSE_FORMAT"
POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
REPLACE_INSTRUCTION = f"""<explanation of the sql query>
{SQL_DELIMETER} 
<sql query exclusively as raw text>"""

with PostgresManager() as db:
    db.connect_with_url(DB_URL)
    table_definitions = db.get_table_definitions_for_prompt()
    print(table_definitions)
    print("-----------------------------------------")

    prompt = api_utils.add_cap_ref(
        args.prompt,
        f"Use these table definitions to inform how you create the suitable query: {POSTGRES_TABLE_DEFINITIONS_CAP_REF}", 
        POSTGRES_TABLE_DEFINITIONS_CAP_REF,
        table_definitions
    )
    print()
    print(prompt)
    print("-----------------------------------------")


    prompt = api_utils.add_cap_ref(
        prompt,
        (f"\n\nRespond in this format {RESPONSE_FORMAT_CAP_REF}.  Replace the text and remove text <> with it's request. "
        "I need to be able to easily parse the sql query from your response. Do NOT use ``` in your response."),
        RESPONSE_FORMAT_CAP_REF,
        REPLACE_INSTRUCTION
    )

    print(prompt)
    print("-----------------------------------------")

    prompt_response = api_utils.prompt(prompt)
    print(prompt_response)

    print("-----------------------------------------")

    sql_query = prompt_response.split(SQL_DELIMETER)[1].strip()
    result = db.run_sql(sql_query)
    print("Result:", result[0])