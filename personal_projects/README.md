
## Personal Projects

Heres a list of project descriptions. Earlier projects are very elementary examples, with more complex use cases further down the list

0. **`Annoyed Chatbot`**: A simple example of using a prompt template to influence a chatbot to respond in a sarcastic manner. 
    - technologies used: langchain
    - notes:

1. **`audio-gpt`**: The audio is then sent to `Whisper-1` to transcribe spoken language into text. This text will then be sent to `ChatGPT`. The response from OpenAI is then converted into a realistic voice via the ElevenLabs API The audo is then played in response to the prompt you said.
    - technologies used: ElevenLabs, openai api
    - notes:

2. **`President Speeches`**: Retrieval augment generation (RAG) example - Load a large corpus of presidential speeches into a vector store, and use `VectorDBQA` chain to ask questions about the documents. 
    - technologies used:  langchain
    - notes: 

3. **`Fact Checker`**: A simple `Streamlit` application using a langchain sequential chain that answers a question and reassesses if the response is true based on a number of assertions. 
    - technologies used: streamlit, langchain
    - notes:

4. **`Youtube Video QA`**: Download the transcript of a youtube video using the `YoutubeLoader`, and store the text from the transcript in a `FAISS` vectorstore. A `ChatOpenAI` is then used to answer questions about the video.
    - technologies used: langchain
    - notes: **`Langchain.YoutubeLoader` was broken** at the time

5. **`historia-lingua`**: Interactive LLM powered history application. You decide the year and click location using a interactive map interface, and the LLM provides you history knowledge of what happened in that region around that time period.
    - technologies used: Docker, openai api, langchain
    - notes: 

6. **`Web Scraping Researcher`**: A sample application which uses LLMs search the web based on the users query for a research topic, and summarize the page content. 
    - tehcnologies used: langhchain, fastapi
    - notes: `SERP_API_KEY` was expensive


7. **`echarts-streamlit`**: Example app to display data in interactive charts - The goal is to have an LLM to autogenerate and return nice looking charts in the UI.
    - technologies used: streamlit, Apache ECharts
    - notes: No models used in this example, just an example template that could be used

8. **`miniminds`**: A 2D similuation game with NPCs powered by LLMs agents.
    - technologies used: pygame
    - notes: Not yet finished, the base UI and randomly generated map is complete, along with a movable avatar and different instances of Person. Need to come back to this some day and add personalities to the NPCs.

9. **`chainlit x autogen`**: A chat interface to interact with autogen agents
    - technologies used: chainlit, autogen
    - notes: chainlit has changed significantly since this example was made, so the code used might not work with newer version versions. The new version of autogen no longer has a logging capability

10. **`Ollama x autogen`**: Example of using open source local models agents with Autogen - use case is to calculate the YTD percentage gain of a given stock.
    - technologies used: Ollama, Autogen, Litellm
    - notes: At the time llama2 struggled to write the code to perform this task.

11. **`Cellular Automata with Agents`**: This example shows how agents can be used to generate cellular automata videos - they would write the code to achieve this. Considering this is a iterative task, the agents are instructed to use GPU accelaration to speed things up where possible.
    - technologies used: autogen
    - notes: Reused this notebook to test out `CompressionAgent` agent, so not a very tidy notebook.

12. **`Autogen RAG QA Evaluation`**: This project showcases how you can evaluate autogen QA Retrieval with weights and biases to find the optimal parameters for a given problem - the iterations are evaluated and plotting using a parrelel coordinates plot. For this use case a QA dataset was generated using langchain and OpenAI.
    - technologies used: Autogen, wandb, langchain
    - notes: 


13. **`SQL Database Querying with Agents`**:  A multi agent application that takes in user input, and uses agents generate SQL, query a postgres database and respond with an answer to the user.
    - technologies used: chaintlit, autogen, postgres
    - notes: Newer autogen and chaintlit versions may affect this applications functionality.


14. **`SQL Database Querying with OpenAI Assistant`**:  This project contains two examples multi agent application that takes in user input, automatically generate SQL, query a postgres database and respond with an answer to the user. One using autogents `GPTAssistantAgent` and the other using openai's assistant API
    - technologies used: chaintlit, autogen, postgres, openai API
    - notes: Newer autogen versions may affect this applications functionality.


15. **`Agent Orchestration using Autogen`**: This extends example 13 to include orchestration of agents. IE: controlling the flow in which messages are sent to specific agents.
    - technologies used: chaintlit, autogen, postgres
    - notes: Newer autogen and chaintlit versions may affect this applications functionality.


16. **`Dynamic Agents x Autogen`**: The purpose of this project is to create agents dynamically depending on the complexity of the users input or query. 
    - technologies used: langchain, autogen
    - notes: **Unfinished**


17. **`Visual Agent - for plotting interactive charts`**: This folder contains code for setting up a conversation initialization
with agents focused on visual tasks with plotting libraries.
    - technologies used: Autogen, chainlit, plotly
    - notes: **Unfinished** - streamlit eCharts wouldn't work, Chainlit wasn't finished implementing the plotly at the time.


18. **`Autogen Discord RAG`**: This project involved scraping all the chat log history from the Autogen and store it in a vector store to perform RAG operations using Agents. The purpose of this is to use the knowledge of Autogen users/developers to answer questions on how to use autogen
    - technologies used: Autogen, ChromaDB
    - notes: This is a naive approach, meaning the raw text conversations text were stored in the vector store - this led to issues with the LLM returning some irrelavant information such as conversational "back-and-forths". A better approach would be to further process the data using an LLM to make a QA dataset.


19. **`Autogen Agent Robot`**: This project showcases how LLM's can be built to control robot actions. Rather than deterministic input rules that dictate how the robot might move - for example pressing forward on the controller to initiate the walking action - the LLM brain of the robot knows what actions it can perform, and decide to put a number of combinations together to achieve a goal. The robot is interfaced with natural language in a Chainlit UI.
    - technologies used: Physical robot, Raspberry Pi, Autogen, paramiko, Chainlit
    - notes: I damaged the expansion board of the robot so the limbs are currently immobile. Will need to fix if i want to extend this project. 


20. **`Custom GPT - Autogen Discord RAG`**: This example extends project 18 to create a more refined QA dataset, by iterating over the chat logs and creating question/answer pairs.
    - technologies used: OpenAI API, Autogen, ChromaDB, 
    - notes: This cost about $10 to do.

21. **`Local Mistral 8x7B Agents`:** Using a quantized **mixtral-8x7b-instruct-v0.1.Q3_K_M** model to create local agents for simple coding tasks, rather than spending money on the OpenAI API.
    - technologies used: llamafile, autogen, mistral
    - notes: Had issues with function calling. Using the instruct model wasn't a good idea - should have used the chat model instead. There is special system message formatting that needs to be used `<s>[INST]` - I suppose now that ollama supports openai schema this shouldn't be an issue going forward.

22. **`Local Agent File Organizer`**: A simple POC for using agents to categorize and organize photographs using the `llava-v1.5-7b` local vision model. Assume you have a folder with a random mix of image types, the agents will be able to classify what's happening in the image and move it to the appropriate folders. Add-on capabilities: have the agents create new category folders.
    - technologies used: autogen, llamafile, chainlit
    - notes: Unfinished, couldn't get autogen to work with `llava-v1.5-7b` because llamafile didn't support the OpenAI schema. Also - chainlit no longer supports `indent` in their sdk so seeing interagent communication in a nice UI is no longer possible -_-

23. **`LLM Finetuning with MLX`**: mlx is an array library that is similar to Numpy, It contains an python API for Apple Silicon. For this i needed some data to fintune a model on - i converted the QA dataset from project 20 into `.jsonl` format and used mlx to fine a mistral 7B model
    - technologies used: mlx
    - notes: output from the finetuned model was basically nonsense, would probably need to use more data to get good results or using a different model. Finetuning takes some time so it needs to be done overnight.

24. **`Llava x Autogen`**: Using the llava vision model with autogen to answer questions based on images provided to it, using chainlit as the chat user interface.
    - technologies used: litellm, ollama, autogen, llava, chainlit
    - notes: Need to try this again without litellm now that Ollama supports the openai schema
