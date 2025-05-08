from safetensors.torch import load_file

path = "./models/nayeon_flux_lora.safetensors"
weights = load_file(path)

print(list(weights.keys())[:20])  

# for key in weights.keys()[:20]:
#     print(f"{key}: {weights[key].shape}, dtype={weights[key].dtype}")
