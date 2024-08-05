"""
This script demonstrates the usage of the FluxPipeline from the diffusers library to generate an image based on a given text prompt.

> Read the README.md
"""

import torch
from diffusers import FluxPipeline
import diffusers
from accelerate import Accelerator

# def get_device(device_name):
#     if device_name == 'mps':
#         return torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')
#     elif device_name == 'cuda':
#         return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
#     else:
#         return torch.device('cpu')

# device = get_device(args.device)


# Modify the rope function to handle MPS device
_flux_rope = diffusers.models.transformers.transformer_flux.rope


def new_flux_rope(pos: torch.Tensor, dim: int, theta: int) -> torch.Tensor:
    assert dim % 2 == 0, "The dimension must be even."
    if pos.device.type == "mps":
        return _flux_rope(pos.to("cpu"), dim, theta).to(device=pos.device)
    else:
        return _flux_rope(pos, dim, theta)


diffusers.models.transformers.transformer_flux.rope = new_flux_rope

# accelerator = Accelerator()

print("Starting script...")

# Step 1: Define the local directory to save the model
model_path = "./saved_flux_model"
print(f"Model path: {model_path}")

# Step 2: Load and cache the model locally
print("Loading model...")
pipe = FluxPipeline.from_pretrained(
    # "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
    # cache_dir=model_path,
    # revision='refs/pr/1',
    # low_cpu_mem_usage=True,
    torch_dtype=torch.bfloat16,
).to("mps")

# pipe = accelerator.prepare(pipe)

print("Model loaded.")

# Step 3: Set the text prompt
# prompt = "Anime cat girl holding a sign that says hello world"
prompt = "iPhone photo: A woman stands in front of a mirror, capturing a selfie. The image quality is grainy, with a slight blur softening the details. The lighting is dim, casting shadows that obscure her features. The room is cluttered, with clothes strewn across the bed and an unmade blanket. Her expression is casual, full of concentration, while the old iPhone struggles to focus, giving the photo an authentic, unpolished feel. The mirror shows smudges and fingerprints, adding to the raw, everyday atmosphere of the scene."

print(f"Prompt: {prompt}")

# Step 4: Run inference and generate the image
print("Generating image...")
try:
    image = pipe(
        prompt=prompt,
        guidance_scale=3.5,
        height=1024,
        width=1024,
        num_inference_steps=6,
        max_sequence_length=256,
    ).images[0]
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Proper cleanup to avoid leaking resources
    del pipe

print("Image generated.")

# Step 5: Save the generated image to a file
output_path = "_output/flux_image.png"
image.save(output_path)
print(f"Image saved to {output_path}.")
