# Qwen3 LoRA Fine-Tuning Toolkit

Fine-tune Qwen3 models with real conversation data. Supports 8GB GPUs via QLoRA.

## Pipeline

```
1. collect_data.py       Extract Q&A pairs from conversations
2. prepare_data.py       Clean, deduplicate, format
3. train.py              QLoRA fine-tuning
4. merge_and_export.py   Merge adapter and export to GGUF
5. ollama create         Deploy to Ollama
```
## Quick Start

```bash
pip install -r requirements.txt

# 1. Collect data
python scripts/collect_data.py

# 2. Train
python scripts/train.py --model Qwen/Qwen3-8B

# 3. Export and deploy
python scripts/merge_and_export.py
ollama create my-model -f Modelfile
```
## Training Parameters

Parameter| Default| Description
---|---|---
LoRA Rank| 8| Low-rank matrix dimension
LoRA Alpha| 16| Scaling parameter
Learning Rate| 2e-4| AdamW optimizer
Batch Size| 1| 8GB VRAM limit
Gradient Accum.| 4| Effective batch = 4
Precision| 4-bit QLoRA| NF4 quantization
Seq Length| 2048| Max tokens per sample

## Data Format (Alpaca)

```json
[
  {
    "instruction": "user question",
    "input": "context (optional)",
    "output": "expected response"
  }
]
```

## Advanced Usage

```bash
# Use 8-bit quantization
python scripts/train.py --quant 8bit

# Custom model
python scripts/train.py --model Qwen/Qwen3-1.7B

# Download from ModelScope
python scripts/train.py --modelscope

# Custom epochs and learning rate
python scripts/train.py --epochs 5 --lr 1e-4
```
