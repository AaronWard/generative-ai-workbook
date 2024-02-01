# Llava x Autogen

An example using Llava on Ollama and autogen



## Setting up model:

Run ollama server locally
- `OLLAMA_HOST=127.0.0.1:5050 ollama serve`

```bash
curl http://localhost:5050/api/chat -d '{
   "model": "llava:34b",
   "messages": [
     {
       "role": "user",
       "content": "why is the sky blue?"
     }
   ],
   "stream": false
}'
```