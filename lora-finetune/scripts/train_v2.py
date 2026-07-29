import os, sys
os.environ["MODELSCOPE_CACHE"] = "D:\学\习\文\件\夹\modelscope"
os.environ["PYTHONUTF8"] = "1"

import torch, gc
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

MODEL_PATH = "D:\\学\习\文\件\夹\\modelscope\\models\\Qwen--Qwen3-8B\\snapshots\\master"
DATA_FILE = "/home/user\\local-model-lab\\lora-finetune\\data\\train.json"
OUTPUT_DIR = "/home/user\\local-model-lab\\lora-finetune\\outputs"
ADAPTER_DIR = os.path.join(OUTPUT_DIR, "qwen3-8b-lora-adapter")

def main():
    print("=" * 60)
    print("Qwen3 8B QLoRA (accelerate offload)")
    print("=" * 60)

    torch.cuda.empty_cache(); gc.collect()

    # Load model with accelerate: only 4-bit on GPU, rest on CPU
    print("[1/5] Loading model with accelerate mediation...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
            # Use simple 8-bit to avoid bitsandbytes crash
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=True,
        )
    except Exception as e1:
        print(f"8-bit failed: {e1[:80]}")
        print("Trying 4-bit with sequential loading...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map="sequential",
            trust_remote_code=True,
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False,
            llm_int8_enable_fp32_cpu_offload=True,
            max_memory={0: "6GiB", "cpu": "20GiB"},
        )

    print(f"Model loaded. GPU mem: {torch.cuda.max_memory_allocated()/1e9:.2f} GB")

    # Check model device distribution
    gpu_params = sum(p.numel() for p in model.parameters() if p.device.type == "cuda")
    cpu_params = sum(p.numel() for p in model.parameters() if p.device.type == "cpu")
    print(f"Parameters on GPU: {gpu_params/1e6:.1f}M, CPU: {cpu_params/1e6:.1f}M")

    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print("[2/5] Model ready")

    # Dataset
    dataset = load_dataset("json", data_files=DATA_FILE, split="train")
    def fmt(example):
        msgs = [{"role": "user", "content": example["instruction"]}]
        if example.get("input"):
            msgs[0]["content"] += "\n" + example["input"]
        msgs.append({"role": "assistant", "content": example["output"]})
        return {"messages": msgs}
    dataset = dataset.map(fmt)
    print(f"Dataset: {len(dataset)} samples")

    # LoRA
    lora_config = LoraConfig(
        r=8, lora_alpha=16,
        target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Training args
    print("[3/5] Configuring training...")
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        warmup_ratio=0.05,
        logging_steps=10, save_steps=100, save_total_limit=2,
        fp16=True, optim="paged_adamw_8bit", report_to="none",
        max_grad_norm=0.3, gradient_checkpointing=True,
    )

    trainer = SFTTrainer(
        model=model, tokenizer=tokenizer, args=args,
        train_dataset=dataset, max_seq_length=2048,
        dataset_text_field="messages",
        formatting_func=lambda x: tokenizer.apply_chat_template(
            x["messages"], tokenize=False, add_generation_prompt=False),
    )

    print("[4/5] Starting training...")
    trainer.train()

    print("[5/5] Saving adapter...")
    trainer.save_model(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print(f"[OK] Adapter saved: {ADAPTER_DIR}")

if __name__ == "__main__":
    main()
