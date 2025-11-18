#!/usr/bin/env python3
"""
Train Gau Keo voi OpenAI Fine-tuning

Chay: python train.py
"""

import json
import os
import sys
import time
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Check dependencies
try:
    from openai import OpenAI
except ImportError:
    print("Chua cai OpenAI library!")
    print("Chay: pip install openai python-dotenv")
    sys.exit(1)

# ============================================
# CHON CHARACTER DE TRAIN
# ============================================
AVAILABLE_CHARACTERS = {
    "1": {
        "name": "gau_keo",
        "display": "Gấu Kẹo 🐧",
        "suffix": "gau-keo"
    },
    "2": {
        "name": "whitecat",
        "display": "WhiteCat 🐱",
        "suffix": "whitecat"
    }
}

print("=" * 60)
print("OPENAI FINE-TUNING")
print("=" * 60)
print()
print("Chon character de train:")
for key, char in AVAILABLE_CHARACTERS.items():
    print(f"  {key}. {char['display']}")
print()

choice = input("Nhap so (1/2): ").strip()
if choice not in AVAILABLE_CHARACTERS:
    print("Lua chon khong hop le!")
    sys.exit(1)

selected_char = AVAILABLE_CHARACTERS[choice]
char_name = selected_char["name"]
char_display = selected_char["display"]
char_suffix = selected_char["suffix"]

print()
print(f"Da chon: {char_display}")
print("=" * 60)
print()

# ============================================
# BUOC 1: Check API key
# ============================================
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Khong tim thay OPENAI_API_KEY trong .env!")
    print()
    print("Tao file .env voi noi dung:")
    print("  OPENAI_API_KEY=sk-proj-...")
    print()
    print("Lay API key tai: https://platform.openai.com/api-keys")
    sys.exit(1)

try:
    client = OpenAI(api_key=api_key)
    print("API key OK!")
except Exception as e:
    print(f"Loi ket noi OpenAI: {e}")
    sys.exit(1)

# ============================================
# BUOC 2: Load training data
# ============================================
print()
print("Doc training data...")

# Load personality and conversations for selected character
personality_path = f'training_data/{char_name}/personality_profile.json'
conversations_path = f'training_data/{char_name}/conversations.json'

if not os.path.exists(personality_path):
    print(f"Khong tim thay: {personality_path}")
    sys.exit(1)

if not os.path.exists(conversations_path):
    print(f"Khong tim thay: {conversations_path}")
    print(f"Hay tao file conversations.json cho {char_display}")
    sys.exit(1)

with open(personality_path, 'r', encoding='utf-8') as f:
    personality = json.load(f)

with open(conversations_path, 'r', encoding='utf-8') as f:
    conversations = json.load(f)

# System prompt - dynamic based on character
character_name = personality['character_name']
system_prompt = f"""Ban la {character_name}.

Tinh cach: {personality['communication_style']['tone']}
Tu hay dung: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

Hay tra loi nhu {character_name} - mem mai, de thuong, casual Gen Z Viet."""

# Convert to OpenAI format
training_examples = []
for conv in conversations:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conv['conversation'])
    training_examples.append({"messages": messages})

# Save JSONL
output_file = Path("training_data/openai_finetune.jsonl")
with open(output_file, 'w', encoding='utf-8') as f:
    for example in training_examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

print(f"Da tao {len(training_examples)} training examples")

# ============================================
# BUOC 3: Upload file
# ============================================
print()
print("Uploading file to OpenAI...")

with open(output_file, 'rb') as f:
    file_response = client.files.create(
        file=f,
        purpose='fine-tune'
    )

file_id = file_response.id
print(f"File uploaded: {file_id}")

# ============================================
# BUOC 4: Create fine-tune job
# ============================================
print()
print("Tao fine-tune job...")
print("Model: gpt-4o-mini-2024-07-18")
print()

job = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={"n_epochs": 3},
    suffix=char_suffix
)

job_id = job.id
print(f"Job created: {job_id}")
print(f"Status: {job.status}")

# Save job ID
with open('openai_job_id.txt', 'w') as f:
    f.write(job_id)

print()
print("=" * 60)
print("TRAINING DANG CHAY...")
print("=" * 60)
print()
print("Training se mat 10-20 phut.")
print("Doi o day? (y/n)")

wait = input().lower() == 'y'

if wait:
    print()
    print("Dang doi training hoan thanh...")
    print("(Check moi 60 giay)")

    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status

        print(f"  [{time.strftime('%H:%M:%S')}] Status: {status}")

        if status == "succeeded":
            print()
            print("=" * 60)
            print("TRAINING HOAN THANH!")
            print("=" * 60)
            print()
            print(f"Model ID: {job.fine_tuned_model}")

            # Save model ID
            with open('openai_model_id.txt', 'w') as f:
                f.write(job.fine_tuned_model)

            print()
            print("Chay bot:")
            print("  python bot.py")
            break

        elif status in ["failed", "cancelled"]:
            print()
            print(f"Training {status}!")
            if job.error:
                print(f"Loi: {job.error}")
            break

        time.sleep(60)
else:
    print()
    print("Check status tai: https://platform.openai.com/finetune")
    print()
    print("Sau khi xong, chay:")
    print("  python bot.py")
