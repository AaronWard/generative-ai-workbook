import os
import requests
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

def easy_load_dotenv(path):
    """
    Small function that loads
    in environment variables for API's
    """
    if isinstance(path, Path):
        pass
    else:
        path = Path(path)

    load_dotenv(path)    
    print(f"Loaded environment variables from {path}, access them using os.environ['']")


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