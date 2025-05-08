##  Training LoRAs Locally on Mac (for MFlux)


> Nevermind, doesn't work on Mac - well it does but you need to wait for eternity 


## Preparing Data

1. Use LLaVA 1.6 in Ollama to generate captions for your LoRA training dataset. You will need files in img folder


```
img/
├── pollock01.jpg
├── pollock01.txt
├── pollock02.jpg
├── pollock02.txt
...
```

along with respective txt file with captions. LLava 1.6 is used to caption it using Ollama 
```
ollama run llava
```

Captions should include a trigger word prepended in the caption - example:
```
triggerword, A photo of a middle-aged man with short brown hair wearing a blue hoodie and glasses. He is standing in front of a lake surrounded by autumn trees. His expression is calm and reflective. Back view, soft lighting, DSLR photo, natural setting.
```

## Training

Use `ai-toolkit` to train the lora. 

```
git clone https://github.com/ostris/ai-toolkit.git
cd ai-toolkit
pip install -r requirements.txt
cp config/examples/train_lora_flux_24gb.yaml config/train_pollock.yaml
huggingface-cli login   # https://huggingface.co/settings/tokens
```

Train:
```
python run.py config/train_pollock.yaml
```

---

## Running the UI

```
cd external/ai-toolkit/ui
npm run build_and_start
```
