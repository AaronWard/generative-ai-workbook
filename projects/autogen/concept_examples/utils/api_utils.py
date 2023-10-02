"""
This file serves as location for utilities related to authentication
and configurations.

Written by: Aaron Ward
"""
import os
import json
import autogen
import tempfile
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from typing import List, Dict, Union, Optional, Set

def config_list_from_dotenv(dotenv_file_path: Optional[str] = None,
                                 filter_dict: Optional[dict] = None) -> List[Dict[str, Union[str, Set[str]]]]:
    """
    Loads configuration details from a .env file or from the environment,
    creates a temporary JSON structure, and sets configurations for autogen.

    Args:
        dotenv_file_path (str, optional): The path to the .env file. If not provided,
            it will look for a .env file using the find_dotenv method from the dotenv module.

    Returns:
        config_list: A list of configurations loaded from the .env file or the environment.
        Each configuration is a dictionary containing:
            - model (str): The model name, e.g., 'gpt-4' or 'gpt-3.5-turbo'.
            - api_key (str): The API key for OpenAI.

    Raises:
        AssertionError: If no configurations are loaded.

    Example:
        >>> load_config_list_from_dotenv(dotenv_file_path='path_to_dotenv_file')
        models to use:  ['gpt-4', 'gpt-3.5-turbo']
        [
            {'model': 'gpt-4', 'api_key': 'some_api_key'}, 
            {'model': 'gpt-3.5-turbo', 'api_key': 'some_api_key'}
        ]
    """

    if dotenv_file_path:
        load_dotenv(Path(dotenv_file_path))
    else:
        load_dotenv(find_dotenv())

    if not filter_dict:
        filter_dict = {
                    "model": {
                        "gpt-4",
                        "gpt-3.5-turbo",
                    }
                }
        
    env_var = [
        {'model': model, "api_key": os.getenv('OPENAI_API_KEY')} for model in filter_dict['model']
    ]

    # Create a temporary file
    # Write the JSON structure to a temporary file and pass it to config_list_from_json
    with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp:
        env_var = json.dumps(env_var)
        temp.write(env_var)
        temp.flush()

        # Setting configurations for autogen
        config_list = autogen.config_list_from_json(
            env_or_file=temp.name,
            filter_dict=filter_dict
        )

    if len(config_list) == 0:
        raise ValueError("No configurations loaded.")
    print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])


    return config_list


if __name__ == "__main__":
    pass
