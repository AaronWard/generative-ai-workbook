# agents/agent.py

from ollama import ChatResponse
from ollama import chat
import random
from typing import Dict
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# AGENTS MUST USE STRUCTURED OUTPUTS:
class ActionResponse(BaseModel):
    action: str
#   parameters: dict
class PerceiveResponse(BaseModel):
    pass
class ThinkRepsonse(BaseModel):
    pass

class Agent:
    def __init__(self, agent_id: int, position: Dict[str, float]):
        self.agent_id = agent_id
        self.position = position  # {'x': float, 'y': float, 'z': float}
        self.goal = None
        self.action = None
        self.direction = {'x': 0.0, 'y': 0.0, 'z': 0.0}  # New attribute
        self.surroundings = ""

    def perceive(self, surroundings):
        self.surroundings = surroundings
        # TODO: Mix of rule + AI generated perception logic here
        #


    def think(self):
        # Thoughts: Decide what to do based on surroundings

        messages = [
            {"role": "system", "content": "You are a sea monkey in a fishbowl."},
            {"role": "user", "content": f"""
Your current position is {self.position}.
Your surroundings are {self.surroundings}.
Decide on an action to move within the fishbowl.

Possible actions:
- `MoveForward`: Move forward along the z-axis.
- `TurnLeft`: Move left along the x-axis.
- `TurnRight`: Move right along the x-axis.
- `MoveUp`: Move up along the y-axis.
- `MoveDown`: Move down along the y-axis.

It's your job to pick a suitable action.
"""},
        ]

        try:
            response: ChatResponse = chat(model='qwen:0.5b',
                                        messages=messages,
                                        format=ActionResponse.model_json_schema(),
                                        options={'temperature': 0.9},
                                        )

            action_output = response.message.content.strip()
            print(f"Agent {self.agent_id}'s response: {action_output}")
            self.action = json.loads(action_output)

            if self.action == "MoveForward":
                self.direction = {'x': 0, 'y': 0, 'z': 1}
            elif self.action == "TurnLeft":
                self.direction = {'x': -1, 'y': 0, 'z': 0}
            elif self.action == "TurnRight":
                self.direction = {'x': 1, 'y': 0, 'z': 0}
            elif self.action == "MoveUp":
                self.direction = {'x': 0, 'y': 1, 'z': 0}
            elif self.action == "MoveDown":
                self.direction = {'x': 0, 'y': -1, 'z': 0}
            elif self.action == "StayStill":
                self.direction = {'x': 0, 'y': 0, 'z': 0}
            else:
                # Random movement if action is unknown
                self.direction = {
                    'x': random.uniform(-1, 1),
                    'y': random.uniform(-1, 1),
                    'z': random.uniform(-1, 1)
                }
        except Exception as e:
            print(f"Error in think(): {e}")
            # Default action
            self.action = {"action": "MoveForward"}

    # def act(self):
    #     # Move in the current direction
    #     speed = 1 / 10  # Units per time step; adjust as needed
    #     for axis in ['x', 'y', 'z']:
    #         self.position[axis] += self.direction[axis] * speed

    #     # Ensure the sea monkey stays within bounds (-50 to 50)
    #     for axis in ['x', 'y', 'z']:
    #         self.position[axis] = max(min(self.position[axis], 50), -50)

    def act(self):
        # Move in the current direction
        speed = 1  # Units per simulation step; adjust as needed
        self.position['x'] += self.direction['x'] * speed
        self.position['y'] += self.direction['y'] * speed
        self.position['z'] += self.direction['z'] * speed

        # Ensure the sea monkey stays within bounds (-50 to 50)
        for axis in ['x', 'y', 'z']:
            self.position[axis] = max(min(self.position[axis], 50), -50)
