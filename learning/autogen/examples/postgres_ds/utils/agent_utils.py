import autogen

def _is_termination_message(x):
    return x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")
    
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
