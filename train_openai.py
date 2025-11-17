#!/usr/bin/env python3
"""
☁️  Train Gấu Kẹo với OpenAI Fine-tuning
Sử dụng OpenAI API để fine-tune GPT-4o-mini

Yêu cầu:
- API key từ OpenAI (https://platform.openai.com/api-keys)
- Có phí ~$1-5 tùy data
- pip install --upgrade openai

Chạy: python train_openai.py
"""

import json
import os
import sys
import time
from pathlib import Path

# Check dependencies
try:
    from openai import OpenAI
    import openai
except ImportError:
    print("❌ Chưa cài OpenAI library!")
    print()
    print("Chạy lệnh này:")
    print("  pip install --upgrade openai")
    sys.exit(1)

# Check OpenAI version
try:
    version = openai.__version__
    major_version = int(version.split('.')[0])
    if major_version < 1:
        print(f"⚠️  OpenAI version cũ: {version}")
        print("   Cần upgrade:")
        print("   pip install --upgrade openai")
        sys.exit(1)
except Exception:
    pass

print("=" * 60)
print("🐧 GẤU KẸO - OPENAI FINE-TUNING")
print("=" * 60)
print()

# ============================================
# BƯỚC 1: Kiểm tra API key
# ============================================
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️  Không tìm thấy OPENAI_API_KEY!")
    print()
    print("Nhập API key của bạn:")
    api_key = input().strip()

    if not api_key:
        print("❌ Cần API key để tiếp tục!")
        print("   Lấy tại: https://platform.openai.com/api-keys")
        exit()

try:
    client = OpenAI(api_key=api_key)
    print("✓ API key OK!")
except TypeError as e:
    if 'proxies' in str(e):
        print()
        print("❌ Lỗi OpenAI library version conflict!")
        print()
        print("Chạy lệnh này để fix:")
        print("  pip install --upgrade openai httpx")
        print()
        sys.exit(1)
    else:
        raise

# ============================================
# BƯỚC 2: Chuẩn bị training data
# ============================================
print()
print("📖 Đọc training data...")

with open('training_data/gau_keo/personality_profile.json', 'r', encoding='utf-8') as f:
    personality = json.load(f)

with open('training_data/gau_keo/conversations.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

# System prompt cho Gấu Kẹo
system_prompt = f"""Bạn là {personality['character_name']}.

Tính cách: {personality['communication_style']['tone']}
Từ hay dùng: {', '.join(personality['common_words'][:10])}
Emoji: {', '.join(personality['signature_emojis'])}

Hãy trả lời như Gấu Kẹo - mềm mại, dễ thương, casual Gen Z Việt."""

# Chuyển đổi sang OpenAI format
training_examples = []
for conv in conversations:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conv['conversation'])
    training_examples.append({"messages": messages})

# Lưu file JSONL
output_file = Path("training_data/openai_gaukeo_finetune.jsonl")
with open(output_file, 'w', encoding='utf-8') as f:
    for example in training_examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

print(f"✓ Đã tạo {len(training_examples)} training examples")
print(f"✓ Lưu tại: {output_file}")

# ============================================
# BƯỚC 3: Upload file
# ============================================
print()
print("☁️  Uploading file to OpenAI...")

with open(output_file, 'rb') as f:
    file_response = client.files.create(
        file=f,
        purpose='fine-tune'
    )

file_id = file_response.id
print(f"✓ File uploaded: {file_id}")

# ============================================
# BƯỚC 4: Tạo fine-tune job
# ============================================
print()
print("🔥 Tạo fine-tune job...")
print("   Model: gpt-4o-mini-2024-07-18")
print("   Epochs: 3")
print()

job = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3
    },
    suffix="gau-keo"
)

job_id = job.id
print(f"✓ Job created: {job_id}")
print(f"✓ Status: {job.status}")

# Lưu job ID để check sau
with open('openai_job_id.txt', 'w') as f:
    f.write(job_id)

print()
print("=" * 60)
print("⏳ TRAINING ĐANG CHẠY...")
print("=" * 60)
print()
print("Training sẽ mất ~10-20 phút.")
print("Bạn có thể:")
print("  1. Đợi ở đây (script sẽ tự động check)")
print("  2. Tắt và check sau bằng: python train_openai.py --check")
print()
print("Bạn muốn đợi không? (y/n)")

wait = input().lower() == 'y'

if wait:
    print()
    print("Đang đợi training hoàn thành...")
    print("(Check mỗi 60 giây)")

    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status

        print(f"  [{time.strftime('%H:%M:%S')}] Status: {status}")

        if status == "succeeded":
            print()
            print("=" * 60)
            print("✅ TRAINING HOÀN THÀNH!")
            print("=" * 60)
            print()
            print(f"🎯 Model ID: {job.fine_tuned_model}")

            # Lưu model ID
            with open('openai_model_id.txt', 'w') as f:
                f.write(job.fine_tuned_model)

            print()
            print("Để test model, chạy:")
            print(f"  python test_personality.py --openai")
            break

        elif status in ["failed", "cancelled"]:
            print()
            print(f"❌ Training {status}!")
            if job.error:
                print(f"   Lỗi: {job.error}")
            break

        # Đợi 60 giây
        time.sleep(60)
else:
    print()
    print("Để check status sau, chạy:")
    print(f"  python -c \"from openai import OpenAI; print(OpenAI().fine_tuning.jobs.retrieve('{job_id}'))\"")
    print()
    print("Hoặc xem tại: https://platform.openai.com/finetune")
