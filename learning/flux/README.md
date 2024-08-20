

## Setup

```bash
conda create -n flux python=3.8
conda activate flux

git clone https://github.com/black-forest-labs/flux
cd flux
pip install -e '.[all]'
# pip install git+https://github.com/huggingface/diffusers.git
pip install diffusers==0.10.2 transformers==4.24.0
pip install accelerate


pip install torch==2.3.1 torchaudio==2.3.1 torchvision==0.18.1
```



```
sudo mkdir -p /var/vm
sudo touch /var/vm/swapfile
sudo chmod 600 /var/vm/swapfile
sudo dd if=/dev/zero of=/var/vm/swapfile bs=1m count=4096  # creates a 4GB swap file
sudo /sbin/mkswap /var/vm/swapfile
sudo swapon /var/vm/swapfile

```


## Links

- Github Repo: https://github.com/black-forest-labs/flux
- Schnell: https://fal.ai/models/fal-ai/flux/schnell
- Mflux: https://github.com/filipstrand/mflux 

HuggingFace:
- `huggingface-cli`: https://huggingface.co/docs/huggingface_hub/guides/cli#huggingface-cli-login
- https://huggingface.co/ChuckMcSneed/FLUX.1-dev

Github Issue:
- https://github.com/black-forest-labs/flux/issues/19
- https://github.com/black-forest-labs/flux/issues/30
- https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX.md
- https://github.com/huggingface/diffusers/issues/9047
- https://github.com/comfyanonymous/ComfyUI/issues/4165
- https://github.com/huggingface/diffusers/issues/9095
- https://github.com/pytorch/pytorch/issues/133520
- https://github.com/black-forest-labs/flux/issues/83

Reddit:
- https://www.reddit.com/r/StableDiffusion/comments/1eij95i/running_flux_on_an_apple_m1_using_comfyui/
- https://www.reddit.com/r/open_flux/comments/1eikuz7/comment/lgbgfys/?share_id=kC9DEiQokXpdlMyFVEvYV&utm_content=2&utm_medium=android_app&utm_name=androidcss&utm_source=share&utm_term=1

Youtube Videos:
- https://www.youtube.com/watch?v=EvdgI_JLVcQ&t=2s

Misc:
- https://izard.livejournal.com/277230.html
- https://towards-agi.medium.com/how-to-flux-schnell-locally-on-an-m3-max-macbook-pro-a7b16b6fcd1c
- https://comfyanonymous.github.io/ComfyUI_examples/flux/
- https://www.chaindesk.ai/tools/youtube-summarizer/flux-1-schnell-local-install-guide-comfy-ui-tXO6SJ-6Eb8#Workflow%20and%20Model%20Setup
- https://fluxaiimagegenerator.com/
- https://anakin.ai/blog/flux-schnell-local/
- https://huggingface.co/ChuckMcSneed/FLUX.1-dev (Flux reupload for those who don't want to make a throwaway account to download it.)



---


### 20th Aug - Update on issues


> The primary issue with running FLUX.1 on an Apple Silicon MacBook (such as the M1, M2, or M3 series) stems from the incompatibility between the PyTorch MPS (Metal Performance Shaders) backend and certain data types used by the FLUX model. Specifically, MPS does not support float64 or bfloat16 tensors, which are used by the FLUX model’s implementation. This leads to errors or, when workarounds are attempted, noisy or incorrect image outputs. recent versions of PyTorch (2.4.0 and above) have introduced changes that further degrade performance or compatibility when running models on Apple Silicon, particularly with MPS. Attempts to downgrade PyTorch to 2.3.1 have provided some relief, but they have not entirely solved the problem, leading to slow performance and high memory usage.


1.	MPS Backend Limitations: MPS does not support float64 tensors, and attempts to use bfloat16 have led to noisy outputs. Converting operations to float32 partly resolves the issue, but not entirely.
2.	Model Precision and Data Types: The FLUX model’s reliance on bfloat16 and float64 precision leads to compatibility issues with MPS, causing poor image quality and errors during inference.
3.	Performance and Memory Issues: Even when downgrading PyTorch to a more stable version (2.3.1), the model still runs slowly and consumes a lot of memory. On M3 Macs, this has led to very high energy usage and fan noise.
4.	Inconsistent Outputs: Many users reported grainy or noisy image outputs when attempting to run the model on MPS, even with workarounds such as modifying the rope function.


### Solution 1:


- `mflux` sorts out a lot of the problems 

```bash
git clone https://github.com/filipstrand/mflux.git
cd mflux

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py --prompt "Realistic image" --steps 6 --seed 2024 --height 1024 --width 1024
```
