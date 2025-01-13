# Description: This file contains helper functions for agents
# these functions pull from a series of prompt templates to generate
# agent thoughts, actions, and awareness of other agents.
# Information from the UI is used to populate the prompts to enable the LLM to simulate
# life within 3D space


# helper functions for awareness of the agents

import math
from typing import List
from agents.agent import Agent

def compute_surroundings(agent: Agent, agents: List[Agent], perception_radius: float = 10.0):
    nearby_agents = []
    for other_agent in agents:
        if other_agent.agent_id != agent.agent_id:
            dx = agent.position['x'] - other_agent.position['x']
            dy = agent.position['y'] - other_agent.position['y']
            dz = agent.position['z'] - other_agent.position['z']
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            if distance <= perception_radius:
                nearby_agents.append({
                    'agent_id': other_agent.agent_id,
                    'distance': distance,
                    'position': other_agent.position
                })
    # Compute distance to boundaries
    distance_to_boundaries = {
        'x_min': agent.position['x'] + 50,
        'x_max': 50 - agent.position['x'],
        'y_min': agent.position['y'] + 50,
        'y_max': 50 - agent.position['y'],
        'z_min': agent.position['z'] + 50,
        'z_max': 50 - agent.position['z'],
    }
    surroundings = {
        'nearby_agents': nearby_agents,
        'distance_to_boundaries': distance_to_boundaries
    }
    return surroundings


# helper functions for thoughts of the agents



# helper functions for actions of the agents