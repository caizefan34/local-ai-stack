import os, sys, torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ADAPTER_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "qwen3-8b-lora-adapter")
MERGED_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "qwen3-8b-merged")
BASE_MODEL = "Qwen/Qwen3-8B"

def main():
    print("=" * 60)
    print("Merge LoRA Adapter → Full Model")
    print("=" * 60)

    if not os.path.exists(ADAPTER_DIR):
        print(f"[ERR] LoRA adapter not found: {ADAPTER_DIR}")
        print("Run scripts/train.py first to complete fine-tuning")
        sys.exit(1)

    print("[1/3] Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

    print("[2/3] Loading and merging LoRA weights...")
    model = PeftModel.from_pretrained(model, ADAPTER_DIR)
    merged = model.merge_and_unload()

    print("[3/3] Saving merged model...")
    os.makedirs(MERGED_DIR, exist_ok=True)
    merged.save_pretrained(MERGED_DIR, safe_serialization=True)
    tokenizer.save_pretrained(MERGED_DIR)

    print(f"[OK] Saved to: {MERGED_DIR}")
    print()

    # Generate Ollama Modelfile
    modelfile = f"""FROM {MERGED_DIR}
PARAMETER temperature 0.2
PARAMETER top_p 0.85
PARAMETER num_ctx 8192

SYSTEM \"\"\"You are a fine-tuned Qwen3 assistant.\"\"\"
"""
    with open(os.path.join(MERGED_DIR, "Modelfile"), "w", encoding="utf-8") as f:
        f.write(modelfile)

    print("Deploy to Ollama:")
    print(f"  cd {MERGED_DIR}")
    print("  ollama create qwen3-8b-finetuned -f Modelfile")
    print()
    print("Note: The merged model is ~16GB (FP16). Convert to GGUF Q4_K_M before importing to Ollama.")
    print("=" * 60)

if __name__ == "__main__":
    main()
