
```
mflux-generate \
    --prompt "Your desired prompt describing the image and style" \
    --init-image-path "/Users/aw/Documents/github/generative-ai-workbook/learning/flux/loras/pfp.jpg" \
    --init-image-strength 0.5 \
    --lora-paths "/Users/aw/Documents/github/generative-ai-workbook/learning/flux/loras/inoitohV2-000012.safetensors" \
    --lora-scales 1.0 \
    --model dev \
    --steps 20 \
    --seed 42 \
    --guidance 4.0 \
    --quantize 8 \
    --height 1024 \
    --width 1024

```