import os, json, sys, torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
    TrainingArguments, HfArgumentParser
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

MODEL_NAME = "Qwen/Qwen3-8B"
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "train.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
ADAPTER_DIR = os.path.join(OUTPUT_DIR, "qwen3-8b-lora-adapter")

def format_example(example):
    """将 Alpaca 格式转换为 Qwen3 的 chat template 格式"""
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

    # === 1. 数据准备 ===
    if not os.path.exists(DATA_FILE):
        print(f"[ERR] 未找到数据集: {DATA_FILE}")
        print("请将训练数据保存为 JSON 格式，放入 data/ 目录")
        sys.exit(1)

    dataset = load_dataset("json", data_files=DATA_FILE, split="train")
    dataset = dataset.map(format_example)
    print(f"[OK] 数据集加载: {len(dataset)} 条")

    # === 2. 4-bit 量化配置（适配 8GB 显存）===
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,  # QLoRA 双重量化
    )

    # === 3. 加载模型和分词器 ===
    print(f"[1/5] 加载基座模型: {MODEL_NAME}")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    model = prepare_model_for_kbit_training(model)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print(f"[2/5] 模型已加载: {sum(p.numel() for p in model.parameters())/1e9:.1f}B 参数")

    # === 4. LoRA 配置 ===
    lora_config = LoraConfig(
        r=8,                # LoRA 秩（8GB 显存推荐 8-16）
        lora_alpha=16,      # 缩放参数
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    # 预期输出: trainable params: ~8M / 8.2B = 0.1%

    # === 5. 训练参数 ===
    print("[3/5] 配置训练参数...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,        # 8GB 显存只能 batch=1
        gradient_accumulation_steps=4,        # 等效 batch_size=4
        num_train_epochs=3,                   # 训练 3 个 epoch
        learning_rate=2e-4,
        warmup_ratio=0.05,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        fp16=True,
        optim="paged_adamw_8bit",            # 节省显存
        report_to="none",
        max_grad_norm=0.3,
    )

    # === 6. SFT Trainer ===
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=dataset,
        max_seq_length=2048,                  # 最大序列长度
        dataset_text_field="messages",
        formatting_func=lambda x: tokenizer.apply_chat_template(
            x["messages"], tokenize=False, add_generation_prompt=False
        ),
    )

    # === 7. 开始训练 ===
    print("[4/5] 开始训练...")
    print(f"    {'数据集':>12}: {len(dataset)} 条")
    print(f"    {'训练轮次':>12}: 3 epoch")
    print(f"    {'学习率':>12}: 2e-4")
    print(f"    {'LoRA 秩':>12}: r=8")
    print(f"    {'显存需求':>12}: ~7GB")
    print("-" * 60)
    trainer.train()

    # === 8. 保存 LoRA 适配器 ===
    print("[5/5] 保存 LoRA 适配器...")
    trainer.save_model(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print(f"[OK] 适配器已保存到: {ADAPTER_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
