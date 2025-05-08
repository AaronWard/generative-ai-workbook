#!/usr/bin/env python3
import sys
from safetensors.torch import load_file, save_file

def rename_keys_for_mflux(input_path: str, output_path: str):
    state_dict = load_file(input_path)
    new_state = {}

    for key, tensor in state_dict.items():
        new_key = key

        # 👇 the one that was blowing up in your LoraUtil:
        new_key = new_key.replace("self_attn_out_proj.lora_A",  "self_attn.out_proj.lora_A")
        new_key = new_key.replace("self_attn_out_proj.lora_B",  "self_attn.out_proj.lora_B")

        # and in case you ever need the MLP projections:
        new_key = new_key.replace("proj_mlp.lora_A",             "mlp.fc1.lora_A")
        new_key = new_key.replace("proj_mlp.lora_B",             "mlp.fc1.lora_B")
        new_key = new_key.replace("proj_out.lora_A",             "mlp.fc2.lora_A")
        new_key = new_key.replace("proj_out.lora_B",             "mlp.fc2.lora_B")

        # and the layer‐norm inside attention blocks:
        new_key = new_key.replace("norm.linear.lora_A",          "self_attn_norm.lora_A")
        new_key = new_key.replace("norm.linear.lora_B",          "self_attn_norm.lora_B")

        new_state[new_key] = tensor

    save_file(new_state, output_path)
    print(f"✅ Renamed keys and wrote {len(new_state)} tensors to {output_path!r}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python _rename_for_mflux.py <input.safetensors> <output.safetensors>")
        sys.exit(1)
    rename_keys_for_mflux(sys.argv[1], sys.argv[2])
