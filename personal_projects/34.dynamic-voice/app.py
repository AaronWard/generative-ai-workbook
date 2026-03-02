#!/usr/bin/env python3
"""
NPC TTS server using:
- LLM for dialogue + emotion scoring
- VibeVoice via ComfyUI (Docker) for TTS using reference audio per emotion
"""

import os
import json
import random
import uuid
from collections import defaultdict, deque
from typing import Dict, Deque, List, Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import openai

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# LLM configuration (adapt model name to what you actually use)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")  # example

# ComfyUI / VibeVoice configuration
COMFYUI_API_URL = os.environ.get("COMFYUI_API_URL", "http://localhost:8188")
# directory where your voice samples live
VOICES_ROOT = os.environ.get("VOICES_ROOT", "./voices")
# directory where generated audio will be written and served from
AUDIO_OUTPUT_DIR = os.environ.get("AUDIO_OUTPUT_DIR", "./generated_audio")

os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class CharacterPersona(BaseModel):
    npc_id: str
    name: str
    base_description: str
    speech_style: str
    default_mood: float = 0.0  # -1..1
    emotion_bias: Dict[str, float] = Field(default_factory=dict)


class NPCState(BaseModel):
    npc_id: str
    mood_score: float = 0.0
    memory: Deque[Dict[str, str]] = Field(default_factory=deque)


class LLMEmotionOutput(BaseModel):
    reply: str
    emotion_label: str
    intensity: float
    mood_delta: float


class SpeakRequest(BaseModel):
    npc_id: str
    player_input: str
    session_id: Optional[str] = None


class SpeakResponse(BaseModel):
    npc_id: str
    reply: str
    emotion_label: str
    intensity: float
    mood_score: float
    audio_path: Optional[str] = None


# ---------------------------------------------------------------------------
# In-memory registries (replace with your DB or persistence)
# ---------------------------------------------------------------------------

# Example persona definitions – extend as needed
PERSONAS: Dict[str, CharacterPersona] = {
    "npc_innkeeper": CharacterPersona(
        npc_id="npc_innkeeper",
        name="Elira the Innkeeper",
        base_description=(
            "Elira runs a small, cozy inn in a frontier town. She is practical, "
            "a bit suspicious of strangers, but softens with regulars."
        ),
        speech_style=(
            "Speaks plainly, rarely uses big words, and often adds small comments "
            "about the town's gossip. Slightly sarcastic when annoyed."
        ),
        default_mood=0.1,  # slightly positive
        emotion_bias={"angry": 0.1, "sad": -0.1},
    ),
    "npc_guard": CharacterPersona(
        npc_id="npc_guard",
        name="Ser Bran the Guard",
        base_description=(
            "A town guard focused on duty and order, usually stern and formal. "
            "Doesn't like troublemakers."
        ),
        speech_style=(
            "Short, clipped sentences, very direct. Uses formal address with outsiders."
        ),
        default_mood=0.0,
        emotion_bias={"angry": 0.2},
    ),
}

# NPC states keyed by (session_id, npc_id)
NPC_STATES: Dict[str, NPCState] = {}

# Memory limits
MAX_MEMORY_ENTRIES = 10

# ---------------------------------------------------------------------------
# Helper functions: NPC state & memory
# ---------------------------------------------------------------------------

def make_state_key(session_id: Optional[str], npc_id: str) -> str:
    if not session_id:
        return f"default::{npc_id}"
    return f"{session_id}::{npc_id}"


def get_or_create_npc_state(session_id: Optional[str], npc: CharacterPersona) -> NPCState:
    key = make_state_key(session_id, npc.npc_id)
    if key not in NPC_STATES:
        NPC_STATES[key] = NPCState(
            npc_id=npc.npc_id,
            mood_score=npc.default_mood,
            memory=deque(maxlen=MAX_MEMORY_ENTRIES),
        )
    return NPC_STATES[key]


def update_memory(state: NPCState, player_input: str, npc_reply: str) -> None:
    state.memory.append({
        "player": player_input,
        "npc": npc_reply,
    })


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# Emotion mapping and sample selection
# ---------------------------------------------------------------------------

# Map arbitrary labels to normalized buckets
def normalize_emotion_label(label: str) -> str:
    l = label.strip().lower()
    if l in ["angry", "rage", "irritated", "annoyed"]:
        return "angry"
    if l in ["sad", "depressed", "melancholic", "gloomy"]:
        return "sad"
    if l in ["happy", "joyful", "content", "cheerful"]:
        return "happy"
    if l in ["fearful", "scared", "anxious", "nervous"]:
        return "fearful"
    if l in ["excited", "enthusiastic", "eager"]:
        return "excited"
    if l in ["sarcastic", "mocking"]:
        return "sarcastic"
    # default
    return "neutral"


def bucket_from_emotion_and_mood(emotion_label: str, mood_score: float) -> str:
    norm = normalize_emotion_label(emotion_label)
    if norm != "neutral":
        return norm

    # fallback: use mood_score to pick bucket
    if mood_score > 0.5:
        return "happy"
    if mood_score < -0.5:
        return "sad"
    return "neutral"


def list_reference_samples(npc_id: str, bucket: str) -> List[str]:
    """
    Returns full paths to reference audio files for given NPC and emotion bucket.
    Expects structure: VOICES_ROOT / npc_id / bucket / *.wav
    """
    bucket_dir = os.path.join(VOICES_ROOT, npc_id, bucket)
    if not os.path.isdir(bucket_dir):
        return []
    files = [
        os.path.join(bucket_dir, f)
        for f in os.listdir(bucket_dir)
        if f.lower().endswith(".wav")
    ]
    return files


def choose_reference_sample(npc_id: str, bucket: str) -> Optional[str]:
    samples = list_reference_samples(npc_id, bucket)
    if not samples:
        return None
    return random.choice(samples)


# ---------------------------------------------------------------------------
# LLM integration
# ---------------------------------------------------------------------------

def call_llm_for_npc(
    persona: CharacterPersona, state: NPCState, player_input: str
) -> LLMEmotionOutput:
    """
    Call the LLM with persona, memory, mood score and get structured JSON.
    Uses OpenAI ChatCompletion-style API (adjust if you use something else).
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Build memory transcript (simple)
    history_lines = []
    for turn in state.memory:
        history_lines.append(f"Player: {turn['player']}")
        history_lines.append(f"{persona.name}: {turn['npc']}")
    history_text = "\n".join(history_lines[-2 * MAX_MEMORY_ENTRIES:])

    system_prompt = f"""
You are roleplaying the NPC '{persona.name}' in a fantasy RPG.

Persona:
- {persona.base_description}
- Speaking style: {persona.speech_style}

You must:
- Stay in character.
- Respond as {persona.name} to the player's input.
- Decide your current emotional state and intensity for this specific reply.
- Return ONLY a JSON object. No additional commentary.
"""

    user_prompt = f"""
Conversation history (most recent last, may be empty):
{history_text if history_text else "(no prior context)"}

Your current internal mood score is in range [-1,1]: {state.mood_score:.2f}.
Positive is happier, negative is sadder or more hostile.

Player just said:
{player_input}

Return ONLY valid minified JSON with this exact schema:
{{
  "reply": "<what you say as {persona.name}>",
  "emotion_label": "<one of: angry, sad, neutral, happy, fearful, excited, sarcastic>",
  "intensity": <float between 0 and 1, where 0 is flat and 1 is extremely intense>,
  "mood_delta": <float between -1 and 1 indicating how this interaction changes your internal mood score>
}}
"""

    completion = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.7,
        max_tokens=512,
    )

    raw = completion.choices[0].message["content"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM did not return valid JSON: {e}\nRaw: {raw}")

    # Basic validation & clamping
    reply = str(data.get("reply", "")).strip()
    emotion_label = str(data.get("emotion_label", "neutral")).strip()
    intensity = float(data.get("intensity", 0.0))
    mood_delta = float(data.get("mood_delta", 0.0))

    intensity = clamp(intensity, 0.0, 1.0)
    mood_delta = clamp(mood_delta, -1.0, 1.0)

    return LLMEmotionOutput(
        reply=reply,
        emotion_label=emotion_label,
        intensity=intensity,
        mood_delta=mood_delta,
    )


# ---------------------------------------------------------------------------
# ComfyUI / VibeVoice integration
# ---------------------------------------------------------------------------

def call_vibevoice_tts(
    text: str,
    reference_audio: Optional[str],
    emotion: str,
    intensity: float,
) -> Optional[str]:
    """
    Call your ComfyUI/VibeVoice docker container to synthesize audio.

    This function assumes an HTTP API like:
      POST {COMFYUI_API_URL}/vibevoice_tts
      JSON body: {text, reference_audio, emotion, intensity}
      Response: {audio_path: "<absolute_or_relative_path.wav>"}

    Adapt the endpoint and payload to your actual workflow.
    """
    if not text:
        return None

    url = f"{COMFYUI_API_URL.rstrip('/')}/vibevoice_tts"
    payload = {
        "text": text,
        "reference_audio": reference_audio,
        "emotion": emotion,
        "intensity": intensity,
    }

    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[VibeVoice] request error: {e}")
        return None

    try:
        data = resp.json()
    except ValueError:
        print("[VibeVoice] invalid JSON response")
        return None

    audio_path = data.get("audio_path")
    if not audio_path:
        print("[VibeVoice] no audio_path in response")
        return None

    # If the container returns a path inside the container, you might need to
    # copy or mount that directory to your host and map it to AUDIO_OUTPUT_DIR.
    # For now we assume it's already accessible or a URL you can return directly.
    return audio_path


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="NPC TTS Server", version="0.1.0")

# Serve generated audio statically if you place files there
if os.path.isdir(AUDIO_OUTPUT_DIR):
    app.mount("/media/audio", StaticFiles(directory=AUDIO_OUTPUT_DIR), name="audio")


@app.post("/npc/speak", response_model=SpeakResponse)
def npc_speak(req: SpeakRequest) -> SpeakResponse:
    # 1. Get persona
    npc = PERSONAS.get(req.npc_id)
    if not npc:
        raise HTTPException(status_code=404, detail=f"Unknown npc_id: {req.npc_id}")

    # 2. Get or init state
    state = get_or_create_npc_state(req.session_id, npc)

    # 3. Call LLM to get reply + emotion
    try:
        llm_out = call_llm_for_npc(npc, state, req.player_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    # 4. Update mood score
    new_mood = clamp(state.mood_score + llm_out.mood_delta, -1.0, 1.0)
    state.mood_score = new_mood

    # 5. Decide emotion bucket and reference sample
    bucket = bucket_from_emotion_and_mood(llm_out.emotion_label, new_mood)
    ref_sample = choose_reference_sample(npc.npc_id, bucket)

    # 6. Call VibeVoice via ComfyUI
    audio_path = call_vibevoice_tts(
        text=llm_out.reply,
        reference_audio=ref_sample,
        emotion=bucket,
        intensity=llm_out.intensity,
    )

    # 7. Update memory
    update_memory(state, req.player_input, llm_out.reply)

    # 8. Return response
    return SpeakResponse(
        npc_id=npc.npc_id,
        reply=llm_out.reply,
        emotion_label=bucket,
        intensity=llm_out.intensity,
        mood_score=state.mood_score,
        audio_path=audio_path,
    )


@app.get("/npc/state/{session_id}/{npc_id}")
def get_state(session_id: str, npc_id: str):
    """Debug endpoint to inspect NPC state."""
    key = make_state_key(session_id, npc_id)
    state = NPC_STATES.get(key)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    # Convert deque to list for JSON
    return {
        "npc_id": state.npc_id,
        "mood_score": state.mood_score,
        "memory": list(state.memory),
    }


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
