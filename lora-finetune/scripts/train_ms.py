import os, json, sys, torch
import gc
os.environ["MODELSCOPE_CACHE"] = "D:\\学习文件夹\\modelscope"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["PYTHONUTF8"] = "1"

from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

MODEL_PATH = r"D:\学习文件夹\modelscope\models\Qwen--Qwen3-8B\snapshots\master"
DATA_FILE = r"/home/user\local-model-lab\lora-finetune\data\train.json"
OUTPUT_DIR = r"/home/user\local-model-lab\lora-finetune\outputs"
ADAPTER_DIR = os.path.join(OUTPUT_DIR, "qwen3-8b-lora-adapter")

def format_example(example):
    messages = [
        {"role": "user", "content": example["instruction"]}
    ]
    if example.get("input"):
        messages[0]["content"] += "\n" + example["input"]
    messages.append({"role": "assistant", "content": example["output"]})
    return {"messages": messages}

def main():
    print("=" * 60)
    print("Qwen3 8B QLoRA Fine-Tuning")
    print("=" * 60)

    if not os.path.exists(DATA_FILE):
        sys.exit(1)
    dataset = load_dataset("json", data_files=DATA_FILE, split="train")
    dataset = dataset.map(format_example)
    print(f"Dataset: {len(dataset)} samples")

    torch.cuda.empty_cache()
    gc.collect()

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        llm_int8_enable_fp32_cpu_offload=True,
    )

    print("[1/5] Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
    )
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print("[2/5] Model loaded")

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    model.config.use_cache = False

    print("[3/5] Training config...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        warmup_ratio=0.05,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        bf16=True,  # Use bf16 instead of fp16 for RTX 50 series
        optim="paged_adamw_8bit",
        report_to="none",
        max_grad_norm=0.3,
        gradient_checkpointing=True,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=dataset,
        max_seq_length=2048,
        dataset_text_field="messages",
        formatting_func=lambda x: tokenizer.apply_chat_template(
            x["messages"], tokenize=False, add_generation_prompt=False
        ),
    )

    print("[4/5] Training started!")
    trainer.train()

    print("[5/5] Saving adapter...")
    trainer.save_model(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print(f"Adapter saved to: {ADAPTER_DIR}")

if __name__ == "__main__":
    main()
