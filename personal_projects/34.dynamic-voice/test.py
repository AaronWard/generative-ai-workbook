#!/usr/bin/env python3
import os
import json
import time
import uuid
import requests
from typing import Tuple, Dict, Any, Optional

# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------

COMFYUI_API_URL = os.environ.get("COMFYUI_API_URL", "http://dashy.comfyui")

# Path to the API-exported workflow JSON
WORKFLOW_JSON_PATH = os.environ.get(
    "WORKFLOW_JSON_PATH",
    "./Single-Speaker-npc-tts-api.json",  # local file in your project
)


# Audio reference file (must be visible inside the container at the same path,
# or adjust to the container's path if you mounted it differently)
VOICE_REFERENCE_PATH = os.environ.get(
    "VOICE_REFERENCE_PATH",
    "/home/aw/Documents/models/ComfyUI/input/mina.mp3",
)

# Node IDs / inputs in YOUR exported workflow:
# Open the JSON and look for:
#   - the node that holds the TEXT (probably a "Load Text" or similar VibeVoice node)
#   - the node that holds the audio path for the voice to clone
#
# Put their numeric IDs and input keys here.
TEXT_NODE_ID = "3"          # example: node "3" is the text loader
TEXT_INPUT_KEY = "text"     # example: text field in that node's "inputs"

AUDIO_NODE_ID = "4"         # example: node "4" is the audio loader
AUDIO_INPUT_KEY = "filepath"  # or "audio", "wav_path", etc. Check the JSON.

# How often to poll /history
POLL_INTERVAL_SEC = 1.0
POLL_TIMEOUT_SEC = 120.0


# --------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------

def load_base_prompt() -> Dict[str, Any]:
    """
    Load the workflow JSON exported in API format and return the "prompt" dict.
    Handles both:
      { "prompt": { "1": {...}, "2": {...} } }
    and
      { "1": {...}, "2": {...} }
    styles.
    """
    with open(WORKFLOW_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "prompt" in data:
        return data["prompt"]
    return data


def build_prompt(text: str, voice_path: str) -> Dict[str, Any]:
    """
    Create a prompt payload for /prompt by:
      - cloning the base prompt
      - overriding the text + reference audio path
    """
    base_prompt = load_base_prompt()

    # Deep copy is safer if you plan to reuse this in a long-lived process
    prompt = json.loads(json.dumps(base_prompt))

    # Set text
    if TEXT_NODE_ID not in prompt:
        raise RuntimeError(f"TEXT_NODE_ID '{TEXT_NODE_ID}' not found in workflow")
    prompt[TEXT_NODE_ID]["inputs"][TEXT_INPUT_KEY] = text

    # Set voice reference path
    if AUDIO_NODE_ID not in prompt:
        raise RuntimeError(f"AUDIO_NODE_ID '{AUDIO_NODE_ID}' not found in workflow")
    prompt[AUDIO_NODE_ID]["inputs"][AUDIO_INPUT_KEY] = voice_path

    client_id = str(uuid.uuid4())

    return {
        "prompt": prompt,
        "client_id": client_id,
    }


def queue_prompt(payload: Dict[str, Any]) -> Tuple[str, str]:
    """
    Send POST /prompt; returns (prompt_id, client_id).
    """
    url = COMFYUI_API_URL.rstrip("/") + "/prompt"
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI /prompt did not return prompt_id: {data}")
    return prompt_id, payload["client_id"]


def wait_for_audio(prompt_id: str) -> Optional[str]:
    """
    Poll /history/{prompt_id} until we see an audio output, then
    build a /view URL for it. Returns the URL, or None on timeout.
    """
    history_url = COMFYUI_API_URL.rstrip("/") + f"/history/{prompt_id}"
    start = time.time()

    while True:
        if time.time() - start > POLL_TIMEOUT_SEC:
            print("Timed out waiting for ComfyUI result")
            return None

        try:
            resp = requests.get(history_url, timeout=10)
            if resp.status_code != 200:
                time.sleep(POLL_INTERVAL_SEC)
                continue
            hist = resp.json()
        except Exception as e:
            print(f"Error reading history: {e}")
            time.sleep(POLL_INTERVAL_SEC)
            continue

        # /history usually returns { "<prompt_id>": { "outputs": {...} } }
        entry = hist.get(prompt_id)
        if not entry:
            time.sleep(POLL_INTERVAL_SEC)
            continue

        outputs = entry.get("outputs") or {}
        # Each node that has a preview/output appears here.
        for node_id, node_output in outputs.items():
            ui = node_output.get("ui") or {}
            # Depending on the node, the key might be "audio" or "audios". Check once in a run.
            audio_list = ui.get("audio") or ui.get("audios")
            if not audio_list:
                continue

            # Take first audio file
            info = audio_list[0]
            filename = info.get("filename")
            subfolder = info.get("subfolder", "")
            filetype = info.get("type", "audio")

            if not filename:
                continue

            # ComfyUI's standard view endpoint:
            #   /view?filename=<>&subfolder=<>&type=<image|audio|...>
            audio_url = (
                COMFYUI_API_URL.rstrip("/")
                + f"/view?filename={filename}&subfolder={subfolder}&type={filetype}"
            )
            return audio_url

        time.sleep(POLL_INTERVAL_SEC)


def run_vibevoice_single_speaker(text: str) -> Optional[str]:
    """
    Convenience wrapper:
      - build prompt
      - queue
      - wait for audio
      - return audio URL
    """
    payload = build_prompt(text=text, voice_path=VOICE_REFERENCE_PATH)
    prompt_id, client_id = queue_prompt(payload)
    print(f"Queued prompt_id={prompt_id}, client_id={client_id}")
    audio_url = wait_for_audio(prompt_id)
    return audio_url


# --------------------------------------------------------------------
# CLI test
# --------------------------------------------------------------------

if __name__ == "__main__":
    test_text = "Hello, this is a test of the VibeVoice text-to-speech system."
    print(f"Sending text: {test_text}")
    url = run_vibevoice_single_speaker(test_text)
    if url:
        print(f"Generated audio available at: {url}")
    else:
        print("No audio found (timeout or error).")
