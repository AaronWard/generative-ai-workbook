## 33. Sea Moneksy

I want make a 3D game, with autonomous agents that walk around and interact with eachother. 
The sea monkeys can swim around in 3D space. Their actions are decided by LLM - which acts a low dimensional mind. 

## Methodology

The agent iteratively thinks based after every step (1 second) on the following
    Awareness:
    - The quadrant of the "bowl" they're currently in. If the LLM agent has a scale for the distance of things within its vicinity, then it can make decisions based on that.
    - The surrounding items, it knows whats around it - within the simulated 3D space (fish bowl)

    Thoughts:
    - The agent can:
        1. sets a goal
        2. reflects on surroundings
        2. makes and informed decision
        3. decides an action

Actions:
    - Swim: this can be for a given unit of distance in the 3D space, for any given direction - as long as it's within the bounds of the 

## Setup

Model:
- gtp-4o-mini: for complex tasks that require speed, with openai api
- qwen 0.5B (local): for structure outputs on repetitive LLM calls (thoughts, ideas etc.) - with ollama

Agent Framework:
- controlflow

Web Framework:
- vue js
- vite
- three.js

Backend:
- Python with FastAPI

TTS:
- Use elevenlabs for audio of the agents


3D Models:
- Sea Monkey: https://sketchfab.com/3d-models/sea-monkey-9c9482bc05ca424c93d7a47e5d96715a

----


```
source venv/bin/activate
```
```
npm run dev
```