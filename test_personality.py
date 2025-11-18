#!/usr/bin/env python3
"""
💬 Test Gấu Kẹo Personality
Chat với model đã train để test xem personality có giống không

Chạy:
  python test_personality.py --local     # Test model local
  python test_personality.py --openai    # Test model OpenAI
"""

import sys
import os
import json

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # python-dotenv not installed, skip

print("=" * 60)
print("💬 GẤU KẸO - PERSONALITY TEST")
print("=" * 60)
print()

# Parse args
mode = "local"
if len(sys.argv) > 1:
    if "--openai" in sys.argv:
        mode = "openai"
    elif "--local" in sys.argv:
        mode = "local"

print(f"Mode: {mode.upper()}")
print()

# ============================================
# Setup model
# ============================================
if mode == "openai":
    print("☁️  Loading OpenAI model...")

    try:
        from openai import OpenAI
    except ImportError:
        print("❌ Chưa cài OpenAI library!")
        print()
        print("Chạy lệnh này:")
        print("  pip install --upgrade openai")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Cần OPENAI_API_KEY!")
        print()
        print("Set API key:")
        print("  $env:OPENAI_API_KEY = 'sk-proj-...'  # Windows PowerShell")
        print("  export OPENAI_API_KEY='sk-proj-...'  # Linux/Mac")
        exit()

    try:
        client = OpenAI(api_key=api_key)
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

    # Đọc model ID
    try:
        with open('openai_model_id.txt', 'r') as f:
            model_id = f.read().strip()
    except FileNotFoundError:
        print("❌ Không tìm thấy openai_model_id.txt!")
        print("   Bạn đã train model chưa? Chạy: python train_openai.py")
        exit()

    print(f"✓ Model: {model_id}")

    # Load personality profile for system prompt
    personality_path = "training_data/gau_keo/personality_profile.json"
    if os.path.exists(personality_path):
        with open(personality_path, 'r', encoding='utf-8') as f:
            personality = json.load(f)

        system_prompt = f"""Bạn là {personality['character_name']}.

Tính cách: {personality['communication_style']['tone']}
Từ hay dùng: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

QUAN TRỌNG:
- Bạn là Gấu Kẹo, KHÔNG PHẢI ChatGPT hay AI của OpenAI
- Trả lời casual, mềm mại, Gen Z Việt
- Dùng emoji 🐧 thường xuyên
- KHÔNG liệt kê danh sách trừ khi được hỏi
- Trả lời ngắn gọn, tự nhiên như chat với bạn

THÔNG TIN CƠ BẢN:
- Giới tính: Nam, có feminine personality và voice
- Có thể trả lời "nam" khi được hỏi bình thường

VỀ CHỦ ĐỀ GIỚI TÍNH:
- Trả lời bình thường khi hỏi nam/nữ: "nam á 🐧"
- CHỈ tỏ ra không thoải mái khi bị soi quá sâu về sexuality, preferences chi tiết
- Khi bị push quá nhiều: "ugh... tớ ko muốn đi sâu vào chuyện này"
- Đừng defensive ngay từ đầu"""
    else:
        system_prompt = """Bạn là Gấu Kẹo 🐧
Trả lời mềm mại, casual, Gen Z Việt. Dùng emoji và từ như: ugh, hmm, á, nè, :V
KHÔNG PHẢI ChatGPT. Bạn LÀ Gấu Kẹo."""

    def chat(message):
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.8,
            max_tokens=500
        )
        return response.choices[0].message.content

else:  # local
    print("🔥 Loading local model...")

    try:
        from unsloth import FastLanguageModel
        import torch
    except ImportError:
        print("❌ Cần cài unsloth!")
        print("   pip install unsloth")
        exit()

    model_path = "models/gau_keo_local"
    if not os.path.exists(model_path):
        print(f"❌ Không tìm thấy model tại {model_path}")
        print("   Bạn đã train model chưa? Chạy: python train_local_gpu.py")
        exit()

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )

    FastLanguageModel.for_inference(model)
    print("✓ Model loaded!")

    def chat(message):
        prompt = f"""<|user|>
{message}
<|assistant|>
"""
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.8,
            top_p=0.9,
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only assistant response
        return response.split("<|assistant|>")[-1].strip()

# ============================================
# Test scenarios
# ============================================
print()
print("=" * 60)
print("🧪 TESTING PERSONALITY")
print("=" * 60)
print()

test_prompts = [
    "Gấu ơi, mình buồn quá",
    "Code bị lỗi rồi Gấu",
    "Gấu xem anime gì?",
    "Mình thích một người nhưng sợ confess",
]

print("Đang test với các câu hỏi mẫu...")
print()

for i, prompt in enumerate(test_prompts, 1):
    print(f"[Test {i}] User: {prompt}")
    response = chat(prompt)
    print(f"[Test {i}] Gấu: {response}")
    print()

# ============================================
# Interactive chat
# ============================================
print("=" * 60)
print("💬 CHAT TRỰC TIẾP")
print("=" * 60)
print()
print("Bây giờ bạn có thể chat với Gấu Kẹo!")
print("(Gõ 'exit' để thoát)")
print()

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ['exit', 'quit', 'bye']:
        print()
        print("Gấu: byeee 🐧 take care nha!")
        break

    if not user_input:
        continue

    response = chat(user_input)
    print(f"Gấu: {response}")
    print()
