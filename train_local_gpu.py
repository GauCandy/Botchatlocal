#!/usr/bin/env python3
"""
🔥 Train Gấu Kẹo với GPU (Local Fine-tuning)
Sử dụng Unsloth + LoRA để train model local

Yêu cầu:
- GPU NVIDIA (ít nhất 8GB VRAM)
- pip install unsloth transformers datasets bitsandbytes

Chạy: python train_local_gpu.py
"""

import json
import torch
from pathlib import Path

print("=" * 60)
print("🐧 GẤU KẸO - LOCAL GPU TRAINING")
print("=" * 60)
print()

# Kiểm tra GPU
if not torch.cuda.is_available():
    print("❌ KHÔNG TÌM THẤY GPU!")
    print()
    print("Có thể do:")
    print("  1. PyTorch CPU-only version (most common)")
    print("  2. NVIDIA drivers chưa cài")
    print("  3. GPU bị tắt trong BIOS")
    print()
    print("FIX:")
    print("  1. Chạy: python check_gpu.py")
    print("  2. Xem hướng dẫn trong INSTALL_WINDOWS.md")
    print()
    print("Hoặc dùng OpenAI training: python train_openai.py")
    print()
    print("Có muốn tiếp tục train trên CPU? (RẤT CHẬM) (y/n)")
    if input().lower() != 'y':
        exit()
    print()
    print("⚠️  Training trên CPU... (có thể mất vài giờ)")
else:
    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"✅ GPU detected: {gpu_name}")
    print(f"✅ VRAM: {vram_gb:.1f} GB")

    # Check VRAM
    if vram_gb < 6:
        print()
        print(f"⚠️  CẢNH BÁO: VRAM thấp ({vram_gb:.1f} GB)")
        print("   Có thể gặp lỗi out of memory")
        print("   Recommend: ít nhất 6GB VRAM")
        print()
        print("Tiếp tục? (y/n)")
        if input().lower() != 'y':
            exit()
    elif vram_gb < 8:
        print(f"   ⚠️  VRAM hơi thấp ({vram_gb:.1f} GB) - sẽ dùng batch size nhỏ")

print()
print("Đang cài đặt dependencies...")

try:
    from unsloth import FastLanguageModel
    from datasets import Dataset
    from trl import SFTTrainer
    from transformers import TrainingArguments
except ImportError:
    print("⚠️  Chưa cài đặt thư viện cần thiết!")
    print("   Chạy: pip install unsloth transformers datasets trl bitsandbytes")
    print()
    print("Bạn có muốn tự động cài không? (y/n)")
    if input().lower() == 'y':
        import subprocess
        subprocess.run(["pip", "install", "unsloth", "transformers", "datasets", "trl", "bitsandbytes"])
        print("✓ Đã cài xong! Vui lòng chạy lại script.")
    exit()

# ============================================
# BƯỚC 1: Đọc training data
# ============================================
print()
print("📖 Đọc training data...")

with open('training_data/gau_keo/personality_profile.json', 'r', encoding='utf-8') as f:
    personality = json.load(f)

with open('training_data/gau_keo/conversations.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

# Chuẩn bị system prompt
system_prompt = f"""Bạn là {personality['character_name']}.

Tính cách: {personality['communication_style']['tone']}
Emoji hay dùng: {', '.join(personality['communication_style']['signature_emojis'])}
Style: {personality['communication_style']['language']}

Hãy trả lời như Gấu Kẹo - mềm mại, dễ thương, và chân thành."""

# Chuyển đổi sang format training
training_data = []
for conv in conversations:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conv['conversation'])

    # Format thành text cho training
    text = ""
    for msg in messages:
        if msg['role'] == 'system':
            text += f"<|system|>\n{msg['content']}\n"
        elif msg['role'] == 'user':
            text += f"<|user|>\n{msg['content']}\n"
        elif msg['role'] == 'assistant':
            text += f"<|assistant|>\n{msg['content']}\n"

    training_data.append({"text": text})

dataset = Dataset.from_list(training_data)
print(f"✓ Loaded {len(training_data)} conversations")

# ============================================
# BƯỚC 2: Load model
# ============================================
print()
print("🤖 Loading base model...")
print("   Sử dụng: Qwen/Qwen2.5-1.5B (nhỏ, nhanh)")

max_seq_length = 2048
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-1.5B-bnb-4bit",  # Model nhỏ, fit với GPU 8GB
    max_seq_length=max_seq_length,
    dtype=None,
    load_in_4bit=True,  # 4-bit quantization để tiết kiệm VRAM
)

print("✓ Model loaded!")

# ============================================
# BƯỚC 3: Setup LoRA
# ============================================
print()
print("⚙️  Setting up LoRA...")

model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

print("✓ LoRA configured!")

# ============================================
# BƯỚC 4: Train
# ============================================
print()
print("🔥 Bắt đầu training...")
print("   (Có thể mất 10-30 phút tùy GPU)")
print()

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=3,  # 3 epochs
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
        save_strategy="epoch",
    ),
)

trainer.train()

print()
print("=" * 60)
print("✅ TRAINING HOÀN THÀNH!")
print("=" * 60)

# ============================================
# BƯỚC 5: Lưu model
# ============================================
print()
print("💾 Lưu model...")

output_dir = Path("models/gau_keo_local")
output_dir.mkdir(parents=True, exist_ok=True)

model.save_pretrained(str(output_dir))
tokenizer.save_pretrained(str(output_dir))

print(f"✓ Model đã lưu tại: {output_dir}")
print()
print("🎯 Để test model, chạy: python test_personality.py --local")
