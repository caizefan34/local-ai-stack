# 🏋️ Qwen3 LoRA Fine-Tuning Toolkit

使用真实对话数据对 Qwen3 模型进行 LoRA 微调，支持 8GB 显卡。

## 工作流

```
1. collect_data.py  →  从 Codex 会话中提取 Q&A 对
2. prepare_data.py  →  清洗、去重、格式化
3. train.py         →  QLoRA 微调
4. merge_and_export.py → 合并导出为 GGUF
5. ollama create    →  部署到 Ollama
```

## 快速开始

```bash
pip install -r requirements.txt

# 1. 收集数据
python scripts/collect_data.py

# 2. 训练
python scripts/train.py

# 3. 导出并部署
python scripts/merge_and_export.py
ollama create my-model -f Modelfile
```

## 训练参数

| 参数 | 值 | 说明 |
|------|-----|------|
| LoRA Rank | 8 | 低秩适应矩阵维度 |
| LoRA Alpha | 16 | 缩放参数 |
| 学习率 | 2e-4 | AdamW 优化器 |
| 批次大小 | 1 | 8GB 显存极限 |
| 梯度累积 | 4 | 等效 batch=4 |
| 精度 | 4-bit QLoRA | NF4 量化 |
| 序列长度 | 2048 | 最大 token 数 |

## 数据格式 (Alpaca)

```json
[
  {
    "instruction": "用户的问题",
    "input": "额外的上下文（可选）",
    "output": "期望的回答"
  }
]
```
