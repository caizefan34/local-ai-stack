import os, sys, json, torch, gc, argparse, time
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

def parse_args():
    p = argparse.ArgumentParser(description='Qwen3 QLoRA Fine-Tuning')
    p.add_argument('--model', default='Qwen/Qwen3-8B')
    p.add_argument('--data', default=os.path.join(os.path.dirname(__file__),'..','data','train.json'))
    p.add_argument('--output', default=os.path.join(os.path.dirname(__file__),'..','outputs'))
    p.add_argument('--quant', choices=['4bit','8bit','none'], default='4bit')
    p.add_argument('--epochs', type=int, default=3)
    p.add_argument('--lr', type=float, default=2e-4)
    p.add_argument('--batch-size', type=int, default=1)
    p.add_argument('--grad-accum', type=int, default=4)
    p.add_argument('--lora-r', type=int, default=8)
    p.add_argument('--lora-alpha', type=int, default=16)
    p.add_argument('--max-seq-len', type=int, default=2048)
    p.add_argument('--modelscope', action='store_true')
    p.add_argument('--modelscope-cache', default=os.path.expanduser('~/.cache/modelscope'))
    p.add_argument('--gradient-checkpointing', action='store_true', default=True)
    return p.parse_args()

def format_example(example):
    msgs = [{'role': 'user', 'content': example['instruction']}]
    if example.get('input'):
        msgs[0]['content'] += chr(10) + example['input']
    msgs.append({'role': 'assistant', 'content': example['output']})
    return {'messages': msgs}

def main():
    args = parse_args()
    model_path = args.model
    if args.modelscope:
        ms_cache = args.modelscope_cache
        mn = args.model.replace('/', '--')
        base = os.path.join(ms_cache, 'models', mn, 'snapshots')
        if os.path.isdir(base):
            snaps = sorted(os.listdir(base))
            if snaps:
                model_path = os.path.join(base, snaps[-1])
                print(f'[OK] ModelScope: {model_path}')
    print(f'Model: {model_path}')
    print(f'Data: {args.data}')
    print(f'Quant: {args.quant}')
    if not os.path.exists(args.data):
        print(f'[ERR] Data not found: {args.data}')
        sys.exit(1)
    dataset = load_dataset('json', data_files=args.data, split='train')
    dataset = dataset.map(format_example)
    print(f'[OK] Dataset: {len(dataset)} samples')
    torch.cuda.empty_cache(); gc.collect()
    qc = None
    if args.quant == '4bit':
        qc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
            bnb_4bit_use_double_quant=True)
    elif args.quant == '8bit':
        qc = BitsAndBytesConfig(load_in_8bit=True)
    dt = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print('[1/5] Loading model...')
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=qc,
            device_map='auto', trust_remote_code=True, torch_dtype=dt, low_cpu_mem_usage=True)
    except Exception as e:
        print(f'[WARN] Retry with offload: {str(e)[:60]}')
        model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=qc,
            device_map='sequential', trust_remote_code=True, torch_dtype=dt,
            max_memory={0: '6GiB', 'cpu': '20GiB'})
    if qc:
        model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token; tokenizer.padding_side = 'right'
    mem = torch.cuda.max_memory_allocated()/1e9 if torch.cuda.is_available() else 0
    print(f'[OK] VRAM: {mem:.1f}GB')
    print('[2/5] LoRA config...')
    lc = LoraConfig(r=args.lora_r, lora_alpha=args.lora_alpha,
        target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],
        lora_dropout=0.05, bias='none', task_type='CAUSAL_LM')
    model = get_peft_model(model, lc)
    model.print_trainable_parameters()
    print('[3/5] Training config...')
    ad = os.path.join(args.output, 'lora-adapter')
    ta = TrainingArguments(output_dir=args.output, per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum, num_train_epochs=args.epochs,
        learning_rate=args.lr, warmup_ratio=0.05, logging_steps=10, save_steps=100,
        save_total_limit=2, fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(), optim='paged_adamw_8bit', report_to='none',
        max_grad_norm=0.3, gradient_checkpointing=args.gradient_checkpointing)
    trainer = SFTTrainer(model=model, tokenizer=tokenizer, args=ta, train_dataset=dataset,
        max_seq_length=args.max_seq_len, dataset_text_field='messages',
        formatting_func=lambda x: tokenizer.apply_chat_template(x['messages'], tokenize=False, add_generation_prompt=False))
    print(f'[4/5] Training {len(dataset)} samples x {args.epochs} epochs...')
    t0 = time.time()
    trainer.train()
    print(f'[5/5] Saving adapter...')
    trainer.save_model(ad)
    tokenizer.save_pretrained(ad)
    print(f'[OK] Saved: {ad}')
    print(f'[OK] Time: {(time.time()-t0)/60:.1f} min')

if __name__ == '__main__':
    main()
