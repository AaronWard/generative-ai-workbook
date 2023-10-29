'''
Misc utility functions
'''
import yaml

def load_sweep_config(filename="config.yaml"):
    with open(filename, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(e)
