#!/usr/bin/env python3
"""
🐧 GẤU KẸO - LOCAL GPU TRAINING (Simple Version)
Không dùng unsloth, dùng transformers + PEFT trực tiếp
Ổn định hơn trên Windows

Chạy: python train_local_simple.py
"""

import os
import json
import sys

print("=" * 60)
print("🐧 GẤU KẸO - LOCAL GPU TRAINING (Simple)")
print("=" * 60)
print()

# Check GPU
try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU detected: {gpu_name}")
        print(f"✅ VRAM: {vram:.1f} GB")
    else:
        print("❌ KHÔNG TÌM THẤY GPU!")
        print()
        print("Cần GPU với CUDA để train local.")
        print("Hoặc dùng OpenAI: python train_openai.py")
        sys.exit(1)
except ImportError:
    print("❌ PyTorch chưa cài!")
    print("   pip install torch --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)

print()
print("Đang load dependencies...")

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling,
        BitsAndBytesConfig
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import Dataset
    print("✓ Dependencies loaded!")
except ImportError as e:
    print(f"❌ Thiếu dependencies: {e}")
    print()
    print("Cài đặt:")
    print("  pip install transformers datasets peft accelerate bitsandbytes")
    sys.exit(1)

# ============================================
# BƯỚC 1: Load training data
# ============================================
print()
print("📖 Đọc training data...")

conversations_path = "training_data/gau_keo/conversations.json"
personality_path = "training_data/gau_keo/personality_profile.json"

if not os.path.exists(conversations_path):
    print(f"❌ Không tìm thấy {conversations_path}")
    sys.exit(1)

with open(conversations_path, 'r', encoding='utf-8') as f:
    conversations = json.load(f)

with open(personality_path, 'r', encoding='utf-8') as f:
    personality = json.load(f)

print(f"✓ Loaded {len(conversations)} conversations")

# Build system prompt
system_prompt = f"""Bạn là {personality['character_name']}.
Tính cách: {personality['communication_style']['tone']}
Từ hay dùng: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

Trả lời như Gấu Kẹo - mềm mại, casual, Gen Z Việt. Dùng emoji 🐧."""

# ============================================
# BƯỚC 2: Prepare dataset
# ============================================
print()
print("🔧 Preparing dataset...")

def format_conversation(conv):
    """Format conversation for training"""
    messages = conv.get('conversation', [])

    # Build chat format
    text = f"<|system|>\n{system_prompt}\n"

    for msg in messages:
        role = msg['role']
        content = msg['content']
        if role == 'user':
            text += f"<|user|>\n{content}\n"
        else:
            text += f"<|assistant|>\n{content}\n"

    return text

# Create dataset
texts = [format_conversation(conv) for conv in conversations]
dataset = Dataset.from_dict({"text": texts})

print(f"✓ Dataset prepared: {len(dataset)} examples")

# ============================================
# BƯỚC 3: Load model
# ============================================
print()
print("🤖 Loading model...")
print("   (Có thể mất vài phút lần đầu)")

# Model to use - small enough for 6GB VRAM
model_name = "microsoft/phi-2"  # 2.7B params, fits in 6GB with 4-bit

# Quantization config for 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Load model with 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

print("✓ Model loaded!")

# ============================================
# BƯỚC 4: Setup LoRA
# ============================================
print()
print("⚙️  Setting up LoRA...")

# Prepare model for training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "dense"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)

trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
print(f"✓ LoRA applied!")
print(f"   Trainable: {trainable_params:,} / {total_params:,} ({100*trainable_params/total_params:.2f}%)")

# ============================================
# BƯỚC 5: Tokenize dataset
# ============================================
print()
print("📝 Tokenizing dataset...")

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
        padding="max_length"
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
print(f"✓ Tokenized!")

# ============================================
# BƯỚC 6: Train
# ============================================
print()
print("🔥 Bắt đầu training...")
print("   (Có thể mất 30-60 phút)")
print()

# Training arguments - optimized for 6GB VRAM
training_args = TrainingArguments(
    output_dir="./models/gau_keo_local",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=50,
    save_total_limit=2,
    warmup_steps=10,
    optim="paged_adamw_8bit",
    report_to="none",
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# Train!
trainer.train()

# ============================================
# BƯỚC 7: Save model
# ============================================
print()
print("💾 Saving model...")

output_dir = "models/gau_keo_local"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

print(f"✓ Model saved to {output_dir}")

print()
print("=" * 60)
print("✅ TRAINING HOÀN THÀNH!")
print("=" * 60)
print()
print(f"Model location: {output_dir}")
print()
print("Test model:")
print("  python test_personality.py --local")
print()
