import os
import torch
import soundfile as sf
from build_model import build_model  # This references the repository's "models/build_model.py"
from kokoro import generate         # This references "kokoro.py"

# Ensure MPS fallback is on if an op is missing
# os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# 1) Build the model from the local file
model_path = "models/kokoro-v0_19.pth"
print(f"Loading TTS model from {model_path}...")
MODEL = build_model(model_path, device)

# 2) Load the "af_bella.pt" voicepack
voice_path = "models/voices/af_bella.pt"
print(f"Loading voice from {voice_path}...")
voicepack = torch.load(voice_path, weights_only=True).to(device)

# 3) Generate TTS audio
text = "Hello from Kokoro running on Apple's MPS backend!"
print(f"Generating TTS for text: {text}")

with torch.no_grad():
    # The language is determined by the first letter: 'a' => American English
    # So for 'af_bella', use lang='a' or just voicepack from the same set
    audio, out_phonemes = generate(MODEL, text, voicepack, lang='a')

# 4) Save to a WAV file and print phonemes
output_file = "out_mps.wav"
sf.write(output_file, audio, 24000)  # 24 kHz is the default
print(f"Generated audio saved to {output_file}")
print("Phonemes used:", out_phonemes)
