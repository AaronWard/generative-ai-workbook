"""
Helper functions for retrieving keys from environment variables.

Written by Aaron Ward
"""

import os
import requests
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def get_available_models():
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        )
        if response.status_code == 200:
            models = response.json()['data']
            return [model['id'] for model in models]
        else:
            print("Error in getting available models: HTTP status code", response.status_code)
            return []
    except Exception as e:
        print("Error in getting available models:", str(e))
        return []