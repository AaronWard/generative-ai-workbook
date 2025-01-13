# backend/main.py

import os
import uvicorn
import base64
import requests
from typing import Optional
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv

# 1) Load environment variables
load_dotenv(find_dotenv())
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_API_URL = "https://api.elevenlabs.io/v1"

app = FastAPI()

# 2) Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read/Chunk text from data/book1.txt
CHUNKS = []
with open("data/book0.txt", "r", encoding="utf-8") as f:
    full_text = f.read()
words = full_text.split()
chunk_size = 200
for i in range(0, len(words), chunk_size):
    chunk_words = words[i : i + chunk_size]
    CHUNKS.append(" ".join(chunk_words))

# Models
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"  # Replace with your default voice
    model_id: str = "eleven_multilingual_v2"

class QueryRequest(BaseModel):
    question: str
    current_chunk: str

@app.get("/chunks/{chunk_id}")
def get_chunk(chunk_id: int):
    if chunk_id < 0 or chunk_id >= len(CHUNKS):
        return {"error": "Invalid chunk_id"}
    return {"chunk_id": chunk_id, "text": CHUNKS[chunk_id]}

@app.get("/voices")
def list_voices():
    """
    Fetch the list of voices available from the ElevenLabs API
    """
    try:
        response = requests.get(
            f"{ELEVEN_API_URL}/voices",
            headers={"xi-api-key": ELEVEN_API_KEY},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch voices: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/tts")
def text_to_speech(req: TTSRequest):
    """
    Use ElevenLabs /with-timestamps endpoint, parse the JSON, decode the base64 audio,
    and return real MP3 bytes so the frontend can play it.
    """
    try:
        # 1) Build the request to /with-timestamps
        url = f"{ELEVEN_API_URL}/text-to-speech/{req.voice_id}/with-timestamps"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": req.text,
            "model_id": req.model_id,
        }
        # e.g. output_format=mp3_44100_128 for MP3
        params = {
            "output_format": "mp3_44100_128"
        }

        # 2) Call ElevenLabs
        r = requests.post(url, headers=headers, json=payload, params=params)

        if r.status_code != 200:
            raise HTTPException(
                status_code=r.status_code,
                detail=f"Error from ElevenLabs: {r.text}",
            )

        # 3) The response is JSON with an "audio" field in base64.
        data = r.json()  # parse JSON
        # data structure example: { "audio": "<base64>", "timestamps": [...] }
        if "audio" not in data:
            raise HTTPException(
                status_code=500,
                detail="No 'audio' field found in /with-timestamps response",
            )

        base64_audio = data["audio"]
        # 4) Decode base64 -> raw MP3 bytes
        mp3_bytes = base64.b64decode(base64_audio)

        # 5) Return the raw MP3
        return Response(content=mp3_bytes, media_type="audio/mpeg")

    except Exception as e:
        error_msg = f"Error generating TTS: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/query")
def context_query(q: QueryRequest):
    return {
        "answer": f"Stub answer to question '{q.question}' about: {q.current_chunk}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
