"""
Main script for application

"""
import os
import sys
import dotenv
import autogen
import argparse

# sys.path.append('./')
dotenv.load_dotenv()

# from .agents import *
# from .api import *
# from .config import *
# from .data.dictionaries import *
from data.db import PostgresManager


DB_URL = os.environ.get("POSTGRES_CONNECTION_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("prompt", help="The prompt for the AI")
    # args = parser.parse_args()

    # config_list = get_config(model_type='gpt-4', dotenv_path='../../../.env')

    # parse prompt param using arg parse
    # connect to db using with statement and create a db_manager
    with PostgresManager() as db:
        db.connect_with_url(DB_URL)
        # users_table = db.try_query()
        users_table = db.get_all(table_name="patients")
        print("users_table", users_table)


        # parse prompt param using arg parse
        # connect to b using with statement and create a db_manager
        # call db_manager.get_table_definition_for_prompt () to get tables in prompt ready form
        # create two blank calls to 1lm.add_cap_ref() that update our current prompt passed in from cli
        # call llm.prompt to get a prompt_ response variable
        # parse sql response from prompt_response using SQL_QUERY_DELIMITER '---------'
        # call db_manager. run_sql() with the parsed sql
        pass



if __name__ == "__main__":
    main()