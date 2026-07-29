import os, sys, torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ADAPTER_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "qwen3-8b-lora-adapter")
MERGED_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "qwen3-8b-merged")
BASE_MODEL = "Qwen/Qwen3-8B"

def main():
    print("=" * 60)
    print("合并 LoRA 适配器 → 完整模型")
    print("=" * 60)

    if not os.path.exists(ADAPTER_DIR):
        print(f"[ERR] 未找到 LoRA 适配器: {ADAPTER_DIR}")
        print("请先运行 scripts/train.py 完成微调")
        sys.exit(1)

    print("[1/3] 加载基座模型...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

    print("[2/3] 加载并合并 LoRA 权重...")
    model = PeftModel.from_pretrained(model, ADAPTER_DIR)
    merged = model.merge_and_unload()

    print("[3/3] 保存合并模型...")
    os.makedirs(MERGED_DIR, exist_ok=True)
    merged.save_pretrained(MERGED_DIR, safe_serialization=True)
    tokenizer.save_pretrained(MERGED_DIR)

    print(f"[OK] 已保存到: {MERGED_DIR}")
    print()

    # 生成 Ollama Modelfile
    modelfile = f"""FROM {MERGED_DIR}
PARAMETER temperature 0.2
PARAMETER top_p 0.85
PARAMETER num_ctx 8192

SYSTEM \"\"\"你是一个经过微调的 Qwen3 助手。\"\"\"
"""
    with open(os.path.join(MERGED_DIR, "Modelfile"), "w", encoding="utf-8") as f:
        f.write(modelfile)

    print("部署到 Ollama:")
    print(f"  cd {MERGED_DIR}")
    print("  ollama create qwen3-8b-finetuned -f Modelfile")
    print()
    print("注意: 合并后的模型约 16GB（FP16），建议转 GGUF Q4_K_M 再导入 Ollama")
    print("=" * 60)

if __name__ == "__main__":
    main()
