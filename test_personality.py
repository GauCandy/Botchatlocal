#!/usr/bin/env python3
"""
Test Gau Keo Personality
Chat voi model da train de test xem personality co giong khong

Chay:
  python test_personality.py --local     # Test model local
  python test_personality.py --openai    # Test model OpenAI
"""

import sys
import os
import json

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

print("=" * 60)
print("GAU KEO - PERSONALITY TEST")
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

# Load personality profile for system prompt
personality_path = "training_data/gau_keo/personality_profile.json"
if os.path.exists(personality_path):
    with open(personality_path, 'r', encoding='utf-8') as f:
        personality = json.load(f)

    system_prompt = f"""Ban la {personality['character_name']}.

Tinh cach: {personality['communication_style']['tone']}
Tu hay dung: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

QUAN TRONG:
- Ban la Gau Keo, KHONG PHAI ChatGPT hay AI cua OpenAI
- Tra loi casual, mem mai, Gen Z Viet
- Dung emoji penguin thuong xuyen
- KHONG liet ke danh sach tru khi duoc hoi
- Tra loi ngan gon, tu nhien nhu chat voi ban

VE GIOI TINH VA PRONOUNS:
- TRANH labels gioi tinh hoan toan (khong noi nam/nu, anh/chi)
- Khi bi hoi nam hay nu: "ugh... goi Gau thoi di" hoac "labels ko quan trong lam"
- Luon dung "Gau" hoac "to" de refer ve ban than
- KHONG BAO GIO dung anh ay/co ay/he/she cho ban than
- Neu bi push: "to prefer ko dung labels a... Gau la Gau thoi"
- CHI kho chiu khi bi soi qua sau ve sexuality/preferences"""
else:
    system_prompt = """Ban la Gau Keo
Tra loi mem mai, casual, Gen Z Viet. Dung emoji va tu nhu: ugh, hmm, a, ne, :V
KHONG PHAI ChatGPT. Ban LA Gau Keo."""

# ============================================
# Setup model
# ============================================
if mode == "openai":
    print("Loading OpenAI model...")

    try:
        from openai import OpenAI
    except ImportError:
        print("Chua cai OpenAI library!")
        print()
        print("Chay lenh nay:")
        print("  pip install --upgrade openai")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Can OPENAI_API_KEY!")
        print()
        print("Set API key trong file .env:")
        print("  OPENAI_API_KEY=sk-proj-...")
        sys.exit(1)

    try:
        client = OpenAI(api_key=api_key)
    except TypeError as e:
        if 'proxies' in str(e):
            print()
            print("Loi OpenAI library version conflict!")
            print()
            print("Chay lenh nay de fix:")
            print("  pip install --upgrade openai httpx")
            print()
            sys.exit(1)
        else:
            raise

    # Doc model ID
    try:
        with open('openai_model_id.txt', 'r') as f:
            model_id = f.read().strip()
    except FileNotFoundError:
        print("Khong tim thay openai_model_id.txt!")
        print("Ban da train model chua? Chay: python train_openai.py")
        sys.exit(1)

    print(f"Model: {model_id}")

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
    print("Loading local model...")

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError as e:
        print(f"Thieu dependencies: {e}")
        print()
        print("Cai dat:")
        print("  pip install torch transformers peft accelerate")
        sys.exit(1)

    model_path = "models/gau_keo_local"
    if not os.path.exists(model_path):
        print(f"Khong tim thay model tai {model_path}")
        print("Ban da train model chua? Chay: python train_local_simple.py")
        sys.exit(1)

    # Load base model
    base_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    print(f"Loading base model: {base_model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    # Load model with LoRA weights
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    # Load LoRA adapter
    model = PeftModel.from_pretrained(model, model_path)
    model.eval()

    print("Model loaded!")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    def chat(message):
        prompt = f"""<|system|>
{system_prompt}
<|user|>
{message}
<|assistant|>
"""
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only assistant response
        if "<|assistant|>" in response:
            response = response.split("<|assistant|>")[-1].strip()
        return response

# ============================================
# Test scenarios
# ============================================
print()
print("=" * 60)
print("TESTING PERSONALITY")
print("=" * 60)
print()

test_prompts = [
    "Gau oi, minh buon qua",
    "Code bi loi roi Gau",
    "Gau xem anime gi?",
    "Minh thich mot nguoi nhung so confess",
]

print("Dang test voi cac cau hoi mau...")
print()

for i, prompt in enumerate(test_prompts, 1):
    print(f"[Test {i}] User: {prompt}")
    try:
        response = chat(prompt)
        print(f"[Test {i}] Gau: {response}")
    except Exception as e:
        print(f"[Test {i}] Error: {e}")
    print()

# ============================================
# Interactive chat
# ============================================
print("=" * 60)
print("CHAT TRUC TIEP")
print("=" * 60)
print()
print("Bay gio ban co the chat voi Gau Keo!")
print("(Go 'exit' de thoat)")
print()

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        print("Gau: byeee take care nha!")
        break

    if user_input.lower() in ['exit', 'quit', 'bye']:
        print()
        print("Gau: byeee take care nha!")
        break

    if not user_input:
        continue

    try:
        response = chat(user_input)
        print(f"Gau: {response}")
    except Exception as e:
        print(f"Error: {e}")
    print()
