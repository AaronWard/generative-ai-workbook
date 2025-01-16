# main.py

import os
import uvicorn
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.agent import Agent
import random
from utils.agent_utils import compute_surroundings

# Load environment variables
load_dotenv(find_dotenv())

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize some agents
agents = [
    Agent(
        agent_id=i,
        position={
            'x': random.uniform(-10, 20),
            'y': random.uniform(-10, 20),
            'z': random.uniform(-10, 20),
        },
    )
    for i in range(1, 15)  # 5 agents
]


@app.post("/simulate")
def simulate():
    # Simulate one time step for each agent
    for agent in agents:
        surroundings = compute_surroundings(agent, agents)
        agent.perceive(surroundings)
        agent.think()
        agent.act()
    return {"status": "Simulation step completed"}


@app.get("/agents")
def get_agents():
    # Return positions of all agents
    return [
        {
            'agent_id': agent.agent_id,
            'position': agent.position,
        }
        for agent in agents
    ]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
