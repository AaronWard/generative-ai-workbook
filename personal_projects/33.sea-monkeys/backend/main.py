import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from agents.agent import Agent
from utils.agent_utils import compute_surroundings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or whatever your front-end is
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
    for i in range(1, 11)  # Let's do 10 agents
]

@app.post("/simulate")
def simulate():
    # Each agent perceives, then simulates one step
    for agent in agents:
        # Surroundings can be computed each step, or less frequently
        surroundings = compute_surroundings(agent, agents)
        agent.perceive(surroundings)
        agent.simulate_step()

    return {"status": "Simulation step completed"}

@app.get("/agents")
def get_agents():
    # Return positions AND current action
    return [
        {
            'agent_id': agent.agent_id,
            'position': agent.position,
            'action': agent.action,
        }
        for agent in agents
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
