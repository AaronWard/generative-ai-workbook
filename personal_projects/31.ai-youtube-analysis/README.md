

## AI Youtube Analysis

The following is a showcase of ControlFlow in action. To do something interesting, I've built a tool that can analyse a youtube channel and give you a summary of the videos and the functionalities that are covered in each video

###  Here are some of the Channels:
- https://www.youtube.com/@vrsen/videos
- https://www.youtube.com/@matthew_berman/videos
- https://www.youtube.com/@WesRoth/videos
- https://www.youtube.com/@aiexplained-official/videos
- https://www.youtube.com/@AIJasonZ/videos
- https://www.youtube.com/@alejandro_ao/videos
- https://www.youtube.com/@AllAboutAI/videos
- https://www.youtube.com/@AssemblyAI/videos
- https://www.youtube.com/@DaveShap/videos
- https://www.youtube.com/@EdanMeyer/videos
- https://www.youtube.com/@indydevdan/videos
- https://www.youtube.com/@mreflow/videos
- https://www.youtube.com/@maya-akim/videos
- https://www.youtube.com/@MervinPraison/videos
- https://www.youtube.com/@ShawhinTalebi/videos
- https://www.youtube.com/@YannicKilcher/videos
- https://www.youtube.com/@1littlecoder/videos
- https://www.youtube.com/@jamesbriggs/videos
- https://www.youtube.com/@YaronBeen/videos


### The logic is as follows:

**Max date window:** 3 years from today
**Broader topic:** AI and LLMs


1. Get all the videos from the channel in the passed 3 years
2. For each video, get the transcript
3. For each transcript, get a summary of the video
4. Check if video is about the broader topic
4. For each summary, get the topics (Check the topics examples below, if the topic is not in the list, add it to the list)
5. Return the videos, summaries and topics and store them in a tree structure
6. Create a timeseries dataset that can be grouped by topic and channel
7. Visualize the timeseries dataset showing the growth of the topic over time for each channel


### Topics Examples relating to LLMs:
- In context learning
- Multimodal models
- Agents
- Vector Databases
- Prompting
- Chain of thought reasoning
- Image
- Search
- Classification 
- Topic Modelling
- Clustering
- Data, Text and Code generation
- Summarization
- Rewriting
- Extractions
- Proof reading
- Swarms
- Querying Data
- Fine tuning
- Executing code
- Sentiment Analysis
- Planning and Complex Reasoning
- Image classification and generation (If multi-modal)
- Philosophical reasoning an ethics
- Reinforcement learning
- Model security and privacy
- API's
- Infrastructure
