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

from agents.db_agent import DBAgent
from data.db import PostgresManager

def main(args):
    """
    Main interface function to postgres db 
    interactions. 
    
    """
    # PROBLEM_TYPE = "COMPLEX"
    PROBLEM_TYPE = "SIMPLE"
    db_agent = DBAgent()    
    db_agent.run(problem_type=PROBLEM_TYPE, prompt=args.prompt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="The prompt for the AI", nargs="?", default=None)
    args = parser.parse_args()

    if args.prompt is None:
        with open(os.path.join(os.path.dirname(__file__), 
                               'prompt_templates', 'test_prompt.txt'), 'r') as file:
            args.prompt = file.read().strip()
    main(args)