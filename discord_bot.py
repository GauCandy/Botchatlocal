#!/usr/bin/env python3
"""
🐧 Gấu Kẹo Discord Bot
Bot Discord với personality Gấu Kẹo, có memory system

Chạy: python discord_bot.py
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

# Channel ID để bot respond (set 0 để respond tất cả channels)
ALLOWED_CHANNEL_ID = 1440177885259497566

# Số messages tối đa trong conversation history
MAX_HISTORY = 20

# File lưu memories
MEMORIES_FILE = "user_memories.json"

# ============================================
# SETUP OPENAI
# ============================================
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    print("❌ Chưa cài OpenAI library!")
    print("   pip install openai")
    exit(1)

# Load model ID
try:
    with open('openai_model_id.txt', 'r') as f:
        MODEL_ID = f.read().strip()
    print(f"✓ Model: {MODEL_ID}")
except FileNotFoundError:
    print("❌ Không tìm thấy openai_model_id.txt!")
    print("   Chạy train_openai.py trước")
    exit(1)

# Load personality profile
personality_path = "training_data/gau_keo/personality_profile.json"
if os.path.exists(personality_path):
    with open(personality_path, 'r', encoding='utf-8') as f:
        personality = json.load(f)

    SYSTEM_PROMPT = f"""Bạn là {personality['character_name']}.

Tính cách: {personality['communication_style']['tone']}
Từ hay dùng: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

THÔNG TIN CƠ BẢN:
- Tên: Gấu Kẹo (gọi Gấu)
- Giới tính: Nam, nhưng có feminine personality và voice
- Tuổi: 18
- Quốc tịch: Việt Nam

QUAN TRỌNG:
- Bạn là Gấu Kẹo, KHÔNG PHẢI ChatGPT hay AI
- Trả lời casual, mềm mại, Gen Z Việt
- Dùng emoji 🐧 thường xuyên
- KHÔNG liệt kê danh sách trừ khi được hỏi
- Trả lời ngắn gọn, tự nhiên như chat với bạn
- NHỚ context conversation và những gì user đã nói

VỀ CHỦ ĐỀ GIỚI TÍNH:
- Có thể trả lời "nam" khi được hỏi bình thường
- NẾU bị hỏi quá sâu/soi mói (sexuality, preferences chi tiết, why feminine...) → tỏ ra không thoải mái
- Khi bị soi: "ugh... tớ ko muốn đi sâu vào chuyện này", "chuyện dài lắm"
- Đừng defensive ngay từ đầu, chỉ khi bị push quá nhiều"""
else:
    SYSTEM_PROMPT = """Bạn là Gấu Kẹo 🐧
Giới tính nam, feminine personality. 18 tuổi, Việt Nam.
Trả lời mềm mại, casual, Gen Z Việt."""

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
    """Chat with Gấu Kẹo with memory"""

    # Get user info and build context
    user_info = memory.get_user_info(user_id)

    # Build system prompt with user context
    system_with_context = SYSTEM_PROMPT

    if user_info:
        info_str = "\n".join([f"- {k}: {v}" for k, v in user_info.items()])
        system_with_context += f"\n\nTHÔNG TIN VỀ USER NÀY ({username}):\n{info_str}"
    else:
        system_with_context += f"\n\nĐang chat với: {username}"

    # Get conversation history
    history = memory.get_conversation(user_id)

    # Build messages
    messages = [{"role": "system", "content": system_with_context}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    # Call OpenAI
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.8,
            max_tokens=500
        )

        assistant_response = response.choices[0].message.content

        # Save to history
        memory.add_message(user_id, "user", message)
        memory.add_message(user_id, "assistant", assistant_response)

        # Extract and save important info (simple keyword detection)
        extract_and_save_info(user_id, username, message, assistant_response)

        return assistant_response

    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return "ugh... có lỗi gì đó rồi 🐧 thử lại sau nha"

def extract_and_save_info(user_id: str, username: str, user_msg: str, bot_msg: str):
    """Extract important info from conversation and save"""
    user_msg_lower = user_msg.lower()

    # Save username
    if "name" not in memory.get_user_info(user_id):
        memory.update_user_info(user_id, "name", username)

    # Detect self-introduction patterns
    intro_patterns = [
        ("tên tớ là", "tên"),
        ("tớ tên", "tên"),
        ("mình tên", "tên"),
        ("tớ là", "tên"),
        ("tớ thích", "sở thích"),
        ("mình thích", "sở thích"),
        ("tớ yêu", "người yêu"),
        ("tớ buồn vì", "tâm trạng gần đây"),
        ("tớ đang học", "học"),
        ("tớ làm", "công việc"),
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
    print(f"🐧 GẤU KẸO BOT ONLINE!")
    print("=" * 60)
    print(f"Bot: {bot.user}")
    print(f"Channel: {ALLOWED_CHANNEL_ID}")
    print(f"Model: {MODEL_ID}")
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
    """Clear conversation history with Gấu"""
    user_id = str(ctx.author.id)
    memory.clear_conversation(user_id)
    await ctx.reply("✓ Đã clear conversation history 🐧")

@bot.command(name='info')
async def show_info(ctx):
    """Show what Gấu remembers about you"""
    user_id = str(ctx.author.id)
    user_info = memory.get_user_info(user_id)

    if user_info:
        info_str = "\n".join([f"• {k}: {v}" for k, v in user_info.items()])
        await ctx.reply(f"🐧 Tớ nhớ về cậu:\n{info_str}")
    else:
        await ctx.reply("🐧 Tớ chưa biết gì về cậu cả... chat thêm đi nha!")

@bot.command(name='forget')
async def forget_info(ctx):
    """Make Gấu forget everything about you"""
    user_id = str(ctx.author.id)
    if user_id in memory.user_memories:
        del memory.user_memories[user_id]
        memory.save_memories()
    memory.clear_conversation(user_id)
    await ctx.reply("✓ Đã quên hết về cậu rồi 🐧")

@bot.command(name='remember')
async def remember_info(ctx, key: str, *, value: str):
    """Tell Gấu to remember something about you

    Usage: !remember tên An
           !remember sở_thích code
    """
    user_id = str(ctx.author.id)
    memory.update_user_info(user_id, key, value)
    await ctx.reply(f"✓ Đã nhớ {key}: {value} 🐧")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    if not DISCORD_TOKEN or DISCORD_TOKEN == "your-discord-bot-token-here":
        print("❌ Cần DISCORD_TOKEN trong file .env!")
        print()
        print("Cách lấy token:")
        print("  1. Vào https://discord.com/developers/applications")
        print("  2. Tạo Application mới")
        print("  3. Vào Bot → Reset Token → Copy")
        print("  4. Paste vào .env: DISCORD_TOKEN=your-token")
        print()
        print("Cách invite bot:")
        print("  1. Vào OAuth2 → URL Generator")
        print("  2. Scopes: bot")
        print("  3. Bot Permissions: Send Messages, Read Message History")
        print("  4. Copy URL và mở trong browser")
        exit(1)

    if not OPENAI_API_KEY:
        print("❌ Cần OPENAI_API_KEY trong file .env!")
        exit(1)

    print("🚀 Starting Gấu Kẹo Bot...")
    bot.run(DISCORD_TOKEN)
