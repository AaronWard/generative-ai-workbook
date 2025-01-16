# agents/agent.py

import random
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from ollama import ChatResponse, chat

load_dotenv()

class ActionResponse(BaseModel):
    action: str

class Agent:
    def __init__(self, agent_id: int, position: dict):
        self.agent_id = agent_id
        self.position = position  # {'x': float, 'y': float, 'z': float}
        self.goal = None
        self.action = None
        self.direction = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.surroundings = ""

    def perceive(self, surroundings):
        self.surroundings = surroundings

    def think(self):
        messages = [
            {"role": "system", "content": "You are a sea monkey in a fishbowl."},
            {
                "role": "user",
                "content": f"""
Your current position is {self.position}.
Your surroundings are {self.surroundings}.
Decide on an action to move within the fishbowl.

Possible actions:
- MoveForward
- TurnLeft
- TurnRight
- MoveUp
- MoveDown
- StayStill

Please provide JSON with a single key 'action' that is one of the above.
""",
            },
        ]

        try:
            # 2) Pass the Pydantic model’s JSON schema as the format:
            response: ChatResponse = chat(
                model='qwen:0.5b',
                messages=messages,
                format=ActionResponse.model_json_schema(),
                options={'temperature': 1.0},
            )

            # 3) The LLM returns a message in the shape of ActionResponse. 
            #    Parse it with Pydantic:
            parsed_output = ActionResponse.model_validate_json(response.message.content)

            # 4) Use the action
            self.action = parsed_output.action
            print(f"Agent {self.agent_id}'s LLM-chosen action: {self.action}")

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
            else:
                # If unknown, random movement
                self.direction = {
                    'x': random.uniform(-1, 1),
                    'y': random.uniform(-1, 1),
                    'z': random.uniform(-1, 1),
                }

        except ValidationError as ve:
            print(f"Error parsing LLM JSON into ActionResponse: {ve}")
            # Default fallback:
            self.action = "MoveForward"
            self.direction = {'x': 0, 'y': 0, 'z': 1}

        except Exception as e:
            print(f"Error in think(): {e}")
            self.action = "MoveForward"
            self.direction = {'x': 0, 'y': 0, 'z': 1}

    def act(self):
        speed = 1
        self.position['x'] += self.direction['x'] * speed
        self.position['y'] += self.direction['y'] * speed
        self.position['z'] += self.direction['z'] * speed

        # Boundaries
        for axis in ['x', 'y', 'z']:
            self.position[axis] = max(min(self.position[axis], 50), -50)
