


def load_prompt(file_path, **kwargs):
    with open(file_path, 'r') as file:
        prompt_template = file.read()
    for key, value in kwargs.items():
        if isinstance(value, list):
            formatted_list = '\n'.join(value)
            kwargs[key] = formatted_list
    return prompt_template.format(**kwargs)