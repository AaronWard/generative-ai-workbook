import os
import dotenv
import autogen
import argparse


import llm
from db import PostgresManager

dotenv.load_dotenv()

# assert os.environ.get("DATABASE_URL"), "POSTGRES_CONNECTION_URL not found in env file"
# assert os.environ.get("OPENAI_API_KEY"), "OPENAI_API_KEY not found in env file"

# DB_URL = os.environ.get("DATABASE_URL")
DB_URL = "postgresql://postgres:admin@localhost:5432/testdb"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_config(model_type, dotenv_path):
    config_list = autogen.config_list_from_dotenv(
        dotenv_file_path=dotenv_path,
        model_api_key_map={
            "gpt-4": "OPENAI_API_KEY",
            "gpt-3.5-turbo": "OPENAI_API_KEY",
        },
        filter_dict={
            "model": {
                model_type,
            }
        }
    )
    return config_list



def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("prompt", help="The prompt for the AI")
    # args = parser.parse_args()


    # config_list = get_config(model_type='gpt-4', dotenv_path='../../../.env')

    # parse prompt param using arg parse
    # connect to db using with statement and create a db_manager
    with PostgresManager() as db:
        db.connect_with_url(DB_URL)
        users_table = db.get_all(table_name="patients")
        print("users_table", users_table)

        # Build the gpt_configuration object
        # llm_config = {
        #     "use_cache": False,
        #     "temperature": 0,
        #     "config_list": config_list,
        #     "request_timeout": 120,
        #     "functions": {
        #         "name": "run_sql",
        #         "description": "Run a SQL query against the postgres database",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "sql": {
        #                     "type": "string",
        #                     "description": "The SQL query to run"
        #                 }
        #             },
        #             "required": ["sql"]
        #         }
        #     }
        # }


        # Build the function map
        # function_map = {
        #     "run_sql": db.run_sql,
        # }


        # # Create our terminate msg function
        # def is_termination_msg(content):
        #     have_content = content.get("content", None) is not None
        #     if have_content and "APPROVED" in content["content"]:
        #         return True
        #     return False




        # table_definitions = db.get_table_definitions_for_prompt()
        # prompt = llm.add_cap_refl(args.prompt,  # "Show jobs that were created after September 25th 20231"
        #                         "Here are the table definitions:",
        #                         "TABLE_DEFINITIONS", table_definitions)
        # prompt = llm.add_cap_refl(prompt, "Please provide the SOL query:", "SOL_QUERY")

        # prompt_response = llm.prompt(prompt)
        # sql_query = prompt_response.split(",")[1].strip()
        # result = db.run_sq(sql_query)
        # print(result)


if __name__ == "__main__":
    main()
