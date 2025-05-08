#!/usr/bin/env python3
import argparse
import sys
from safetensors.torch import load_file, save_file

# Map your SDXL‐style subkeys to the correct module names
SUB_MAP = {
    "mlp_fc1": "mlp.fc1",
    "mlp_fc2": "mlp.fc2",
    "self_attn_q_proj": "self_attn.to_q",
    "self_attn_k_proj": "self_attn.to_k",
    "self_attn_v_proj": "self_attn.to_v",
    "self_attn_out_proj": "self_attn.to_out",
}

def convert_key(orig_key: str, scale: float):
    """
    Turn e.g.:
      lora_te_text_model_encoder_layers_3_mlp_fc1.lora_up.weight
    into:
      text_model.encoder.layers.3.mlp.fc1.lora_A.weight
    and multiply the tensor by `scale`.
    """
    # we only handle weights
    if not orig_key.endswith(".weight"):
        return None, None

    # expect startswith lora_te_
    if not orig_key.startswith("lora_te_text_model_encoder_layers_"):
        return None, None

    # strip prefix
    tail = orig_key[len("lora_te_"):]
    # tail now: text_model_encoder_layers_3_mlp_fc1.lora_up.weight

    # split at ".lora_"
    module_part, updown = tail.rsplit(".lora_", 1)
    # module_part: text_model_encoder_layers_3_mlp_fc1
    # updown: "up.weight" or "down.weight"

    # get A vs B
    ab = "A" if updown.startswith("up") else "B"

    # break module part into its pieces
    parts = module_part.split("_")
    # ["text", "model", "encoder", "layers", "3", "mlp", "fc1"]

    # sanity check
    if parts[:4] != ["text", "model", "encoder", "layers"]:
        return None, None

    layer_idx = parts[4]
    subkey = "_".join(parts[5:])  # "mlp_fc1" or "self_attn_q_proj", etc.

    # map subkey
    if subkey not in SUB_MAP:
        return None, None
    subpath = SUB_MAP[subkey]  # e.g. "mlp.fc1"

    # rebuild the final key
    new_key = f"text_model.encoder.layers.{layer_idx}.{subpath}.lora_{ab}.weight"
    return new_key, scale

def main(input_path, output_path, scale):
    print(f"📦 Loading: {input_path}")
    flat = load_file(input_path)

    converted = {}
    count = 0

    for k, v in flat.items():
        new_key, mult = convert_key(k, scale)
        if new_key is None:
            continue
        converted[new_key] = v * mult
        count += 1

    if count == 0:
        print("❌ No compatible keys found. Check your input file.")
        sys.exit(1)

    save_file(converted, output_path)
    print(f"✅ Converted {count} tensors → {output_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Convert SDXL LoRA to MFlux/Diffusers–compatible safetensors"
    )
    p.add_argument("input", help="Path to input LoRA (.safetensors)")
    p.add_argument("output", help="Path for output safetensors")
    p.add_argument(
        "-s", "--scale", type=float, default=1.0, help="LoRA scale factor"
    )
    args = p.parse_args()
    main(args.input, args.output, args.scale)
