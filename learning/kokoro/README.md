
## Kokoro TTS


- https://github.com/remsky/Kokoro-FastAPI

```bash
git clone https://github.com/remsky/Kokoro-FastAPI.git
cd Kokoro-FastAPI
git checkout v0.0.5post1-stable
docker compose up --build
docker compose -f docker-compose.cpu.yml up --build
```

## Voices

- 'af' # Default voice is a 50-50 mix of Bella & Sarah
- 'af_bella'
- 'af_sarah'
- 'am_adam'
- 'am_michael'
- 'bf_emma'
- 'bf_isabella'
- 'bm_george'
- 'bm_lewis',
- 'af_nicole'
- 'af_sky'


----

## GPU Acceleration:

> Apple Silicon does not have an NVIDIA GPU and does not support CUDA. Docker on macOS does not pass your Apple GPU through to the container in a way that supports CUDA or MPS. Even on Intel-based Macs, if you don’t have an external NVIDIA eGPU (and older drivers for it), Docker can’t provide NVIDIA GPU acceleration. Hence, you can’t simply do docker compose up --build (the GPU version) on your Apple M1/M2 machine to get hardware acceleration.

PyTorch has introduced Metal Performance Shaders (MPS) support for Apple Silicon. To leverage this for Kokoro TTS:

```
/opt/homebrew/bin/python3.10 -m venv .venv
# python3 -m venv .venv

source .venv/bin/activate

pip install --upgrade pip
pip install "torch>=2.0" torchvision torchaudio --index-url https://download.pytorch.org/whl/metal.html
```


