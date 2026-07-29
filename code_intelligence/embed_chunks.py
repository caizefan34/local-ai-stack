"""Embed AST-aware code chunks with a local CodeBERT-compatible encoder."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create local code embeddings from code-index.json")
    parser.add_argument("input", type=Path, help="Output from index_codebase.py")
    parser.add_argument("--output", type=Path, default=Path("code-embeddings.json"))
    parser.add_argument("--model", default="microsoft/codebert-base")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    args = parser.parse_args()
    if args.batch_size < 1 or args.max_length < 32:
        parser.error("--batch-size must be positive and --max-length must be at least 32")
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except ImportError as error:
        parser.error(f"Install transformers and torch to use code embeddings: {error}")
    source = json.loads(args.input.read_text(encoding="utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModel.from_pretrained(args.model)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    embedded = []
    chunks = source.get("chunks", [])
    with torch.no_grad():
        for start in range(0, len(chunks), args.batch_size):
            batch = chunks[start:start + args.batch_size]
            texts = ["\n".join(filter(None, [chunk.get("signature"), chunk.get("docstring"), chunk.get("code")])) for chunk in batch]
            inputs = tokenizer(texts, padding=True, truncation=True, max_length=args.max_length, return_tensors="pt")
            inputs = {key: value.to(device) for key, value in inputs.items()}
            outputs = model(**inputs).last_hidden_state
            mask = inputs["attention_mask"].unsqueeze(-1)
            vectors = (outputs * mask).sum(1) / mask.sum(1).clamp(min=1)
            for chunk, vector in zip(batch, vectors.cpu().tolist()):
                embedded.append({**chunk, "embedding_profile": "code", "embedding": vector})
    args.output.write_text(json.dumps({"model": args.model, "chunks": embedded, "dependencies": source.get("dependencies", [])}, ensure_ascii=False), encoding="utf-8")
    print(f"Embedded {len(embedded)} code chunks with {args.model} on {device}: {args.output}")


if __name__ == "__main__":
    main()
