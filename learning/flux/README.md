

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
- `huggingface-cli`: https://huggingface.co/docs/huggingface_hub/guides/cli#huggingface-cli-login

Github Issue:
- https://github.com/black-forest-labs/flux/issues/19
- https://github.com/black-forest-labs/flux/issues/30
- https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX.md

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
- https://anakin.ai/blog/flux-schnell-local/
