
## Personal Projects



0. `Annoyed Chatbot`: A simple example of using a prompt template to influence a chatbot to respond in a sarcastic maner. 
1. `audio-gpt`: The audio is then sent to `Whisper-1` to transcribe spoken language into text. This text will then be sent to `ChatGPT`. The response from OpenAI is then converted into a realistic voice via the ElevenLabs API The audo is then played in response to the prompt you said
2. `President Speeches`: Load a large corpus of presidential speeches into a vector store, and use `VectorDBQA` chain to ask questions about the documents. 
3. `Fact Checker`: A simple `Streamlit` application using a sequential chain that answers a question and reassesses if the response is true based on a number of assertions. 
4. `Youtube Video QA`: Download the transcript of a youtube video using the `YoutubeLoader`, and store the text from the transcript in a `FAISS` vectorstore. A `ChatOpenAI` is then used to answer questions about the video.
5. `historia-lingua`: Interactive LLM powered history application. You decide the year and location using a graphical interface, and the LLM provides you history knowledge of what happened in that region around that time period.
