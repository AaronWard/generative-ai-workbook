# Deep Researcher

- This is a controlflow implementation of the same concept as https://github.com/langchain-ai/open_deep_research
- 



---


### Start LM Studio


```sh
# 1) Install Xvfb (virtual X server)
sudo pacman -S --needed xorg-server-xvfb

# 2) Launch a virtual display on :99
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp -noreset &

# 3) Point this shell at the virtual display
export DISPLAY=:99

LM_APP=~/Applications/LM-Studio-0.3.22-1-x64.appimage
chmod +x "$LM_APP"

# Start the background service. --no-sandbox helps on some setups over SSH.
"$LM_APP" --appimage-extract-and-run --no-sandbox --run-as-service & sleep 5


pgrep -a lm-studio

# Start and bind to port
~/.lmstudio/bin/lms server start --port 1234
```


## Check if server is running 

```sh
# Check json res
curl -s http://127.0.0.1:1234/v1/models || true

# List models
~/.lmstudio/bin/lms ls
```


## Load model

> lets use openai/gpt-oss-20b for this

```sh
MODEL_ID="openai/gpt-oss-20b"
CUDA_VISIBLE_DEVICES=1 ~/.lmstudio/bin/lms load "$MODEL_ID"
```


## Monitor GPU

```sh
watch -n 1 nvidia-smi
```


Unload 
```
~/.lmstudio/bin/lms unload --all || true
```