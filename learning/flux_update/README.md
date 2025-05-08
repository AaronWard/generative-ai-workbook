
## mFLUX

- Updated for 2025
- https://github.com/filipstrand/mflux
- https://docs.bfl.ml/pricing/


# 1. Set up environment
```
python3 -m venv .venv
source .venv/bin/activate
```

# 2. Install MFLUX
`pip install -U mflux`


---



🖼️ Image Generation (Quantized Recommended)
Generate a test image (8-bit Schnell model):

```
mflux-generate \
  --model schnell \
  --prompt "Luxury food photograph" \
  --steps 2 \
  --quantize 8 \
  --seed 42
```

Dev model (higher quality, slower):
```
mflux-generate \
  --model dev \
  --prompt "Luxury food photograph" \
  --steps 25 \
  --quantize 8 \
  --seed 42
```

---

📦 Saving Local Quantized Model

```
mflux-save \
  --model dev \
  --quantize 8 \
  --path ~/mflux_models/dev_8bit

```

mflux-generate \
  --path ~/mflux_models/dev_8bit \
  --model dev \
  --prompt "Realistic Skyrim tundra under aurora" \
  --steps 6 \
  --seed 2024

---

## Lora

- `./models/flux1-canny-dev-lora.safetensors` - canny edge map - highlight edges

