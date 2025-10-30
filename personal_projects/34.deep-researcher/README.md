# Deep Researcher

- This is a controlflow implementation of the same concept as https://github.com/langchain-ai/open_deep_research
- 



---


### Start LM Studio
## Load model

> lets use openai/gpt-oss-20b for this

```sh
# 0) Stop LM Studio + helpers
~/.lmstudio/bin/lms server stop || true
pkill -f ".lmstudio/.internal/utils/node" || true
pkill -f "lm-studio" || true

# 1) Free GPU1 (your 5090) from Open WebUI (adjust if docker/systemd)
# sudo kill -TERM 374063 2>/dev/null || true; sleep 1
# sudo kill -KILL 374063 2>/dev/null ||lm true

# 2) Re-enable compute on the 4060 (GPU 0) – the survey needs to see *some* GPUs
sudo nvidia-smi -i 0 -c DEFAULT

# 3) Headless display (use a clean one; if :100 is locked, clear it or pick :101)
rm -f /tmp/.X100-lock /tmp/.X11-unix/X100 2>/dev/null || true
Xvfb :100 -screen 0 1280x800x24 -nolisten tcp -noreset & disown
export DISPLAY=:100

# 4) **Pin to the 5090 for the worker (two ways; pick ONE)**

# Option A (mask to GPU1): Inside masked view, device 0 == your 5090
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=1
export LLAMA_CUDA_DEV=0

# Option B (both GPUs visible, pick 1 explicitly)
# export CUDA_DEVICE_ORDER=PCI_BUS_ID
# export CUDA_VISIBLE_DEVICES=0,1
# export LLAMA_CUDA_DEV=1

# 5) Start the LM Studio service **YOURSELF** so it inherits the env above
~/.local/opt/squashfs-root/lm-studio --no-sandbox --run-as-service & disown
sleep 3

# 6) Start API server and load the model
~/.lmstudio/bin/lms server start --port 1234
~/.lmstudio/bin/lms unload --all || true
~/.lmstudio/bin/lms load "openai/gpt-oss-20b"

# 7) Verify – worker should now sit on GPU 1 (5090)
nvidia-smi

```




python test2.py --debug --los "Solve step by step: A car travels 60 km in 1.5 hours. What is its average speed in km/h?"
python test2.py --debug --medium "Solve step by step: A car travels 60 km in 1.5 hours. What is its average speed in km/h?"
python test2.py --debug --high "Solve step by step: A car travels 60 km in 1.5 hours. What is its average speed in km/h?"
