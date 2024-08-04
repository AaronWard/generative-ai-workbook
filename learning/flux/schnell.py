import torch
from diffusers import FluxPipeline
from accelerate import Accelerator

accelerator = Accelerator()

print("Starting script...")

# Step 1: Define the local directory to save the model
model_path = "./saved_flux_model"
print(f"Model path: {model_path}")

# Step 2: Load and cache the model locally
print("Loading model...")

try:
    # Load model with low_cpu_mem_usage and bf16 precision
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-schnell", 
        cache_dir=model_path, 
        low_cpu_mem_usage=True,
        torch_dtype=torch.bfloat16
    )
    pipe = accelerator.prepare(pipe)
    print("Model loaded.")

    # Ensure the model is on CPU
    pipe.to("cpu")
    print("Model set to CPU.")

    # Set the text prompt
    prompt = "A cat holding a sign that says hello world"
    print(f"Prompt: {prompt}")

    # Run inference and generate the image
    print("Generating image...")
    with torch.no_grad():  # Disable gradient calculations
        image = pipe(
            prompt,
            guidance_scale=0.0,
            output_type="pil",
            num_inference_steps=4,
            max_sequence_length=256,
            generator=torch.Generator("cpu").manual_seed(0)
        ).images[0]

    # Save the generated image to a file
    if image is not None:
        output_path = "flux-schnell.png"
        image.save(output_path)
        print(f"Image saved to {output_path}.")
    else:
        print("No image was generated.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Proper cleanup to avoid leaking resources
    del pipe
    torch.cuda.empty_cache()  # Free up unused memory
