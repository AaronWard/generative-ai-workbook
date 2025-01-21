import random
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from ollama import ChatResponse, chat

load_dotenv()

class ActionResponse(BaseModel):
    action: str

class Agent:
    def __init__(self, agent_id: int, position: dict):
        self.agent_id = agent_id
        self.position = position
        self.goal = None
        self.action = "StayStill"   # <-- Store the current action 
        self.direction = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.surroundings = ""
        # This will track how many steps we've done since last LLM call
        self.steps_since_last_think = 0
        # How frequently to consult the LLM (in # of simulation steps)
        self.think_frequency = 5

    def perceive(self, surroundings):
        """Store the environment context."""
        self.surroundings = surroundings

    def think(self):
        """Call the LLM to decide a new action."""
        messages = [
            {"role": "system", "content": "You are a sea monkey in a fishbowl."},
            {
                "role": "user",
                "content": f"""
Your current position is {self.position}.
Your surroundings are {self.surroundings}.
Decide on an action to move within the fishbowl.

Pick one of the following actions:
- MoveForward
- MoveLeft
- MoveRight
- MoveUp
- MoveDown
- StayStill
""",
            },
        ]

        try:
            response: ChatResponse = chat(
                model='qwen:0.5b',
                messages=messages,
                format=ActionResponse.model_json_schema(),
                options={'temperature': 0.7},
            )
            parsed_output = ActionResponse.model_validate_json(response.message.content)
            self.action = parsed_output.action
            print(f"Agent {self.agent_id}'s LLM-chosen action: {self.action}")
        except ValidationError as ve:
            print(f"Error parsing LLM JSON into ActionResponse: {ve}")
            # Default fallback:
            self.action = "MoveForward"
        except Exception as e:
            print(f"Error in think(): {e}")
            self.action = "MoveForward"

        # Based on self.action, set a direction vector
        if self.action == "MoveForward":
            self.direction = {'x': 0, 'y': 0, 'z': 5}
        elif self.action == "TurnLeft":
            self.direction = {'x': -5, 'y': 0, 'z': 0}
        elif self.action == "TurnRight":
            self.direction = {'x': 5, 'y': 0, 'z': 0}
        elif self.action == "MoveUp":
            self.direction = {'x': 0, 'y': 5, 'z': 0}
        elif self.action == "MoveDown":
            self.direction = {'x': 0, 'y': -5, 'z': 0}
        else:
            self.direction = {'x': 0, 'y': 0, 'z': 0}

    def act(self):
        """Apply the movement from self.direction to self.position."""
        speed = 1
        self.position['x'] += self.direction['x'] * speed
        self.position['y'] += self.direction['y'] * speed
        self.position['z'] += self.direction['z'] * speed

        # Boundaries
        for axis in ['x', 'y', 'z']:
            self.position[axis] = max(min(self.position[axis], 50), -50)

    def simulate_step(self):
        """
        Do one "step" of the agent's simulation:
        - Possibly call self.think() (less frequently).
        - Always call self.act() (to keep moving in the current direction).
        """
        self.steps_since_last_think += 1
        if self.steps_since_last_think >= self.think_frequency:
            # Re-check with the LLM
            self.think()
            self.steps_since_last_think = 0

        # Either way, continue doing the action
        self.act()
