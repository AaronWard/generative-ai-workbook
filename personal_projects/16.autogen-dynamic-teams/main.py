import os
import autogen
import logging
import pprint as pp
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from chains.delegator_chain import DelegatorChain

user_query = ""

delegator = DelegatorChain(openai_api_key=os.getenv('OPENAI_API_KEY'))
pp.pprint(delegator.get_roles())

# def get_configuration():
#     """Return the list dynamic agent configurations"""

#     delegator = DelegatorChain(openai_api_key=os.getenv('OPENAI_API_KEY'), model='model')
#     response = delegator.run({
#         "input": user_query,
#     })

#     return response


# def instantiate_agents(self, agent_configs):
#     logging.info("Initializing Agents")
    

#     llm_config_common = agent_configs['llm_config']

#     agents = []
#     for agent_name, config in agent_configs.items():
#         # Update common configurations
#         config_updated = config.copy()
#         config_updated['llm_config'] = llm_config_common
#         config_updated['system_message'] = agent_configs[agent_name]['system_message']

#         # Dynamically create agents based on type specified in the config
#         if config.get('type') == 'UserProxyAgent':
#             agent = autogen.UserProxyAgent(**config_updated)
#         elif config.get('type') == 'AssistantAgent':
#             agent = autogen.AssistantAgent(**config_updated)
#         else:
#             raise ValueError(f"Unknown agent type for {agent_name}")

#         agents.append(agent)

#     if config.get('complexity' == "simple"):
#         # Assert len(agent_configs.items()) is not > 2
#         pass
#     elif config.get('complexity' == "complex"):
#         # Instantiate group chat and manager with the created agents
#         groupchat_user_proxy = autogen.GroupChat(agents=agents, messages=[], max_round=50)
#         groupchat_manager = autogen.GroupChatManager(groupchat=groupchat_user_proxy, llm_config=llm_config_common)    

#     print("Agents Initiated!")

# agent_configs = get_configuration(user_query)
# agents = instantiate_agents(agent_configs)


