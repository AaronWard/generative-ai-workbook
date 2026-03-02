

# Dynamic Voice

NPC Dialogue + Emotion + TTS Server
This service generates NPC responses using:

* LLM dialogue (persona + memory)
* Emotion scoring (emotion_label, intensity, mood_delta)
* Internal mood tracking per NPC
* Emotion-based reference voice selection
* TTS synthesis via VibeVoice running in a ComfyUI Docker container

Main endpoint: POST /npc/speak

---

1. Project Structure

```xml
app.py
utils.py
data/
```

---

2. Conda Setup

```bash
conda create -n npc-tts python=3.11 -y
conda activate npc-tts
pip install fastapi uvicorn[standard] requests pydantic openai python-dotenv
```

---

3. Environment Variables

```bash
export OPENAI_API_KEY="your-key"
export LLM_MODEL="gpt-4o-mini"
export COMFYUI_API_URL="http://localhost:8188"
export VOICES_ROOT="./voices"
export AUDIO_OUTPUT_DIR="./generated_audio"
```

---

4. Running the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

5. Voice Sample Layout

```text
voices/
  npc_innkeeper/
    neutral/ref_01.wav
    angry/ref_01.wav
    sad/ref_01.wav
```

Place multiple WAVs per bucket if desired.

---

6. Using the API

Example request:

```bash
curl -X POST http://localhost:8000/npc/speak \
  -H "Content-Type: application/json" \
  -d '{
        "npc_id": "npc_innkeeper",
        "player_input": "Do you have rooms?",
        "session_id": "test-1"
      }'
```

Example response:

```json
{
  "npc_id": "npc_innkeeper",
  "reply": "Of course. How long are you staying?",
  "emotion_label": "neutral",
  "intensity": 0.2,
  "mood_score": 0.1,
  "audio_path": "/media/audio/npc_innkeeper/xyz.wav"
}
```

---

7. Notes

* Ensure VibeVoice / ComfyUI container exposes an HTTP endpoint matching `COMFYUI_API_URL`.
* Make sure `voices/` and `generated_audio/` are mounted or accessible from both the Python server and the container.
* Emotion→bucket mapping lives in `main.py` (`normalize_emotion_label()` and `bucket_from_emotion_and_mood()`).
