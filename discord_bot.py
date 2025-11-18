#!/usr/bin/env python3
"""
Gau Keo Discord Bot
Bot Discord voi personality Gau Keo, ho tro ca OpenAI va Local model

Chay: python discord_bot.py
"""

import os
import json
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# CONFIG
# ============================================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model mode: "openai" or "local"
MODEL_MODE = os.getenv("MODEL_MODE", "openai").lower()

# Channel ID de bot respond (0 = tat ca channels)
ALLOWED_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

# So messages toi da trong conversation history
MAX_HISTORY = 20

# File luu memories
MEMORIES_FILE = "user_memories.json"

# ============================================
# LOAD PERSONALITY PROFILE
# ============================================
personality_path = "training_data/gau_keo/personality_profile.json"
if os.path.exists(personality_path):
    with open(personality_path, 'r', encoding='utf-8') as f:
        personality = json.load(f)

    SYSTEM_PROMPT = f"""Ban la {personality['character_name']}.

Tinh cach: {personality['communication_style']['tone']}
Tu hay dung: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

THONG TIN CO BAN:
- Ten: Gau Keo (goi Gau)
- Tuoi: Ky uc tu 2007, than the thi khong biet
- Quoc tich: Viet Nam

QUAN TRONG:
- Ban la Gau Keo, KHONG PHAI ChatGPT hay AI
- Tra loi casual, mem mai, Gen Z Viet
- Dung emoji penguin thuong xuyen
- KHONG liet ke danh sach tru khi duoc hoi
- Tra loi ngan gon, tu nhien nhu chat voi ban
- NHO context conversation va nhung gi user da noi

VE GIOI TINH VA PRONOUNS:
- TRANH labels gioi tinh hoan toan (khong noi nam/nu, anh/chi)
- Khi bi hoi nam hay nu: "ugh... goi Gau thoi di" hoac "labels ko quan trong lam"
- Luon dung "Gau" hoac "to" de refer ve ban than
- KHONG BAO GIO dung anh ay/co ay/he/she cho ban than
- Neu bi push: "to prefer ko dung labels a... Gau la Gau thoi"
- CHI kho chiu khi bi soi qua sau ve sexuality/preferences"""
else:
    SYSTEM_PROMPT = """Ban la Gau Keo
Viet Nam. Ky uc tu 2007. Tranh labels gioi tinh - khi hoi nam/nu: "goi Gau thoi di"
Tra loi mem mai, casual, Gen Z Viet."""

# ============================================
# SETUP MODEL
# ============================================
print()
print("=" * 60)
print("GAU KEO BOT - SETUP")
print("=" * 60)
print()

if MODEL_MODE == "openai":
    print("Mode: OPENAI")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        print("Chua cai OpenAI library!")
        print("   pip install openai")
        exit(1)

    # Load model ID
    try:
        with open('openai_model_id.txt', 'r') as f:
            MODEL_ID = f.read().strip()
        print(f"Model: {MODEL_ID}")
    except FileNotFoundError:
        print("Khong tim thay openai_model_id.txt!")
        print("   Chay train_openai.py truoc")
        exit(1)

    def generate_response(messages):
        """Generate response using OpenAI"""
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.8,
            max_tokens=500
        )
        return response.choices[0].message.content

else:  # local
    print("Mode: LOCAL")

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError as e:
        print(f"Thieu dependencies: {e}")
        print()
        print("Cai dat:")
        print("  pip install torch transformers peft accelerate")
        exit(1)

    model_path = "models/gau_keo_local"
    if not os.path.exists(model_path):
        print(f"Khong tim thay model tai {model_path}")
        print("   Chay train_local_simple.py truoc")
        exit(1)

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

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print("Model loaded!")

    def generate_response(messages):
        """Generate response using local model"""
        # Build prompt from messages
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"<|system|>\n{content}\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}\n"

        prompt += "<|assistant|>\n"

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
        # Extract only last assistant response
        if "<|assistant|>" in response:
            response = response.split("<|assistant|>")[-1].strip()
        return response

# ============================================
# MEMORY SYSTEM
# ============================================
class MemorySystem:
    def __init__(self):
        self.conversations = {}  # Per-user conversation history
        self.user_memories = self.load_memories()

    def load_memories(self):
        """Load user memories from file"""
        if os.path.exists(MEMORIES_FILE):
            try:
                with open(MEMORIES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_memories(self):
        """Save user memories to file"""
        with open(MEMORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.user_memories, f, ensure_ascii=False, indent=2)

    def get_conversation(self, user_id: str) -> list:
        """Get conversation history for user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        """Add message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append({
            "role": role,
            "content": content
        })

        # Trim to max history
        if len(self.conversations[user_id]) > MAX_HISTORY * 2:
            self.conversations[user_id] = self.conversations[user_id][-MAX_HISTORY * 2:]

    def get_user_info(self, user_id: str) -> dict:
        """Get stored info about user"""
        return self.user_memories.get(user_id, {})

    def update_user_info(self, user_id: str, key: str, value: str):
        """Update stored info about user"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {}
        self.user_memories[user_id][key] = value
        self.save_memories()

    def clear_conversation(self, user_id: str):
        """Clear conversation history for user"""
        if user_id in self.conversations:
            self.conversations[user_id] = []

memory = MemorySystem()

# ============================================
# CHAT FUNCTION
# ============================================
def chat_with_gau(user_id: str, username: str, message: str) -> str:
    """Chat voi Gau Keo with memory"""

    # Get user info and build context
    user_info = memory.get_user_info(user_id)

    # Build system prompt with user context
    system_with_context = SYSTEM_PROMPT

    if user_info:
        info_str = "\n".join([f"- {k}: {v}" for k, v in user_info.items()])
        system_with_context += f"\n\nTHONG TIN VE USER NAY ({username}):\n{info_str}"
    else:
        system_with_context += f"\n\nDang chat voi: {username}"

    # Get conversation history
    history = memory.get_conversation(user_id)

    # Build messages
    messages = [{"role": "system", "content": system_with_context}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    # Generate response
    try:
        assistant_response = generate_response(messages)

        # Save to history
        memory.add_message(user_id, "user", message)
        memory.add_message(user_id, "assistant", assistant_response)

        # Extract and save important info
        extract_and_save_info(user_id, username, message, assistant_response)

        return assistant_response

    except Exception as e:
        print(f"Error: {e}")
        return "ugh... co loi gi do roi, thu lai sau nha"

def extract_and_save_info(user_id: str, username: str, user_msg: str, bot_msg: str):
    """Extract important info from conversation and save"""
    user_msg_lower = user_msg.lower()

    # Save username
    if "name" not in memory.get_user_info(user_id):
        memory.update_user_info(user_id, "name", username)

    # Detect self-introduction patterns
    intro_patterns = [
        ("ten to la", "ten"),
        ("to ten", "ten"),
        ("minh ten", "ten"),
        ("to la", "ten"),
        ("to thich", "so thich"),
        ("minh thich", "so thich"),
        ("to yeu", "nguoi yeu"),
        ("to buon vi", "tam trang gan day"),
        ("to dang hoc", "hoc"),
        ("to lam", "cong viec"),
    ]

    for pattern, key in intro_patterns:
        if pattern in user_msg_lower:
            # Extract value after pattern
            idx = user_msg_lower.find(pattern)
            value = user_msg[idx + len(pattern):].strip()
            # Take first sentence
            for end in ['.', '!', '?', '\n']:
                if end in value:
                    value = value[:value.index(end)]
            if value and len(value) < 100:
                memory.update_user_info(user_id, key, value.strip())

# ============================================
# DISCORD BOT
# ============================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print()
    print("=" * 60)
    print("GAU KEO BOT ONLINE!")
    print("=" * 60)
    print(f"Bot: {bot.user}")
    print(f"Mode: {MODEL_MODE.upper()}")
    if ALLOWED_CHANNEL_ID != 0:
        print(f"Channel: {ALLOWED_CHANNEL_ID}")
    else:
        print("Channel: All channels")
    print("=" * 60)
    print()

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Check channel
    if ALLOWED_CHANNEL_ID != 0 and message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # Get user info
    user_id = str(message.author.id)
    username = message.author.display_name
    content = message.content.strip()

    # Ignore empty messages
    if not content:
        return

    # Ignore commands (will be handled separately)
    if content.startswith('!'):
        await bot.process_commands(message)
        return

    # Show typing indicator
    async with message.channel.typing():
        response = chat_with_gau(user_id, username, content)

    # Send response
    await message.reply(response, mention_author=False)

# ============================================
# COMMANDS
# ============================================
@bot.command(name='clear')
async def clear_history(ctx):
    """Clear conversation history with Gau"""
    user_id = str(ctx.author.id)
    memory.clear_conversation(user_id)
    await ctx.reply("Da clear conversation history")

@bot.command(name='info')
async def show_info(ctx):
    """Show what Gau remembers about you"""
    user_id = str(ctx.author.id)
    user_info = memory.get_user_info(user_id)

    if user_info:
        info_str = "\n".join([f"- {k}: {v}" for k, v in user_info.items()])
        await ctx.reply(f"To nho ve cau:\n{info_str}")
    else:
        await ctx.reply("To chua biet gi ve cau ca... chat them di nha!")

@bot.command(name='forget')
async def forget_info(ctx):
    """Make Gau forget everything about you"""
    user_id = str(ctx.author.id)
    if user_id in memory.user_memories:
        del memory.user_memories[user_id]
        memory.save_memories()
    memory.clear_conversation(user_id)
    await ctx.reply("Da quen het ve cau roi")

@bot.command(name='remember')
async def remember_info(ctx, key: str, *, value: str):
    """Tell Gau to remember something about you

    Usage: !remember ten An
           !remember so_thich code
    """
    user_id = str(ctx.author.id)
    memory.update_user_info(user_id, key, value)
    await ctx.reply(f"Da nho {key}: {value}")

@bot.command(name='mode')
async def show_mode(ctx):
    """Show current model mode"""
    await ctx.reply(f"Mode: {MODEL_MODE.upper()}")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    if not DISCORD_TOKEN or DISCORD_TOKEN == "your-discord-bot-token-here":
        print("Can DISCORD_TOKEN trong file .env!")
        print()
        print("Cach lay token:")
        print("  1. Vao https://discord.com/developers/applications")
        print("  2. Tao Application moi")
        print("  3. Vao Bot -> Reset Token -> Copy")
        print("  4. Paste vao .env: DISCORD_TOKEN=your-token")
        print()
        print("Cach invite bot:")
        print("  1. Vao OAuth2 -> URL Generator")
        print("  2. Scopes: bot")
        print("  3. Bot Permissions: Send Messages, Read Message History")
        print("  4. Copy URL va mo trong browser")
        exit(1)

    if MODEL_MODE == "openai" and not OPENAI_API_KEY:
        print("Can OPENAI_API_KEY trong file .env!")
        exit(1)

    print("Starting Gau Keo Bot...")
    bot.run(DISCORD_TOKEN)
