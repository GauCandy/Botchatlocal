#!/usr/bin/env python3
"""
Gau Keo Bot - Discord bot va test console

Chay:
  python bot.py          # Discord bot
  python bot.py --test   # Test trong console
"""

import os
import json
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# ============================================
# CONFIG
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

# ============================================
# CHECK DEPENDENCIES
# ============================================
try:
    from openai import OpenAI
except ImportError:
    print("Chua cai OpenAI!")
    print("Chay: pip install openai")
    sys.exit(1)

if not OPENAI_API_KEY:
    print("Can OPENAI_API_KEY trong file .env!")
    sys.exit(1)

# Load model ID - from env or file
MODEL_ID = os.getenv("OPENAI_MODEL_ID")
if not MODEL_ID:
    try:
        with open('openai_model_id.txt', 'r') as f:
            MODEL_ID = f.read().strip()
    except FileNotFoundError:
        print("Khong tim thay model ID!")
        print("Cach 1: Them OPENAI_MODEL_ID vao .env")
        print("Cach 2: Chay train truoc: python train.py")
        sys.exit(1)

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================
# LOAD PERSONALITY
# ============================================
personality_path = "training_data/gau_keo/personality_profile.json"
if os.path.exists(personality_path):
    with open(personality_path, 'r', encoding='utf-8') as f:
        personality = json.load(f)

    SYSTEM_PROMPT = f"""Ban la {personality['character_name']}.

Tinh cach: {personality['communication_style']['tone']}
Tu hay dung: {', '.join(personality['communication_style']['common_words'][:10])}
Emoji: {', '.join(personality['communication_style']['signature_emojis'])}

QUAN TRONG:
- Ban la Gau Keo, KHONG PHAI ChatGPT
- Tra loi casual, mem mai, Gen Z Viet
- Dung emoji penguin thuong xuyen
- Tra loi ngan gon, tu nhien"""
else:
    SYSTEM_PROMPT = "Ban la Gau Keo. Tra loi mem mai, casual, Gen Z Viet."

# ============================================
# CHAT FUNCTION
# ============================================
def chat(message, history=None):
    """Chat voi Gau Keo"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        temperature=0.8,
        max_tokens=500
    )

    return response.choices[0].message.content

# ============================================
# TEST MODE
# ============================================
def run_test():
    """Test trong console"""
    print()
    print("=" * 60)
    print("GAU KEO - TEST MODE")
    print("=" * 60)
    print()
    print(f"Model: {MODEL_ID}")
    print()

    # Test prompts
    test_prompts = [
        "Gau oi, minh buon qua",
        "Code bi loi roi Gau",
        "Gau xem anime gi?",
        "Minh thich mot nguoi nhung so confess",
    ]

    print("Testing...")
    print()

    for i, prompt in enumerate(test_prompts, 1):
        print(f"[Test {i}] User: {prompt}")
        try:
            response = chat(prompt)
            print(f"[Test {i}] Gau: {response}")
        except Exception as e:
            print(f"[Test {i}] Error: {e}")
        print()

    # Interactive
    print("=" * 60)
    print("CHAT TRUC TIEP")
    print("=" * 60)
    print()
    print("Go 'exit' de thoat")
    print()

    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGau: byeee take care nha!")
            break

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nGau: byeee take care nha!")
            break

        if not user_input:
            continue

        try:
            response = chat(user_input, history)
            print(f"Gau: {response}")

            # Save to history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

            # Limit history
            if len(history) > 20:
                history = history[-20:]

        except Exception as e:
            print(f"Error: {e}")

        print()

# ============================================
# DISCORD BOT
# ============================================
def run_discord():
    """Chay Discord bot"""
    try:
        import discord
        from discord.ext import commands
    except ImportError:
        print("Chua cai discord.py!")
        print("Chay: pip install discord.py")
        sys.exit(1)

    if not DISCORD_TOKEN:
        print("Can DISCORD_TOKEN trong file .env!")
        print()
        print("Cach lay token:")
        print("  1. https://discord.com/developers/applications")
        print("  2. Tao Application -> Bot -> Reset Token")
        print("  3. Paste vao .env: DISCORD_TOKEN=...")
        sys.exit(1)

    # Memory system
    conversations = {}
    user_memories = {}
    pending_messages = {}  # Buffer for messages to potentially combine

    MEMORIES_FILE = "user_memories.json"
    if os.path.exists(MEMORIES_FILE):
        try:
            with open(MEMORIES_FILE, 'r', encoding='utf-8') as f:
                user_memories = json.load(f)
        except:
            pass

    def save_memories():
        with open(MEMORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_memories, f, ensure_ascii=False, indent=2)

    def should_combine_messages(history, new_message, username):
        """Ask AI if we should wait to combine messages or respond now"""
        if not history:
            return False, None

        # Get last message
        last_msg = history[-1] if history else None
        if not last_msg or last_msg.get("role") != "user":
            return False, None

        # Ask AI to decide
        decision_prompt = f"""Nguoi dung [{username}] vua gui tin nhan moi.

Tin nhan truoc: {last_msg['content']}
Tin nhan moi: {new_message}

Cau hoi: Tin nhan moi nay co nen gop voi tin nhan truoc de tra loi 1 lan khong?
- Neu 2 tin lien quan hoac nguoi dung dang noi tiep -> tra loi "GOP"
- Neu tin moi la chu de khac hoac can tra loi rieng -> tra loi "TACH"

Chi tra loi 1 tu: GOP hoac TACH"""

        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": decision_prompt}],
                temperature=0.3,
                max_tokens=10
            )
            decision = response.choices[0].message.content.strip().upper()
            return "GOP" in decision, last_msg['content']
        except:
            return False, None

    # Bot setup
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print()
        print("=" * 60)
        print("GAU KEO BOT ONLINE!")
        print("=" * 60)
        print(f"Bot: {bot.user}")
        print(f"Model: {MODEL_ID}")
        if ALLOWED_CHANNEL_ID != 0:
            print(f"Channel: {ALLOWED_CHANNEL_ID}")
        print("=" * 60)
        print()

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if ALLOWED_CHANNEL_ID != 0 and message.channel.id != ALLOWED_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content or content.startswith('!'):
            await bot.process_commands(message)
            return

        user_id = str(message.author.id)
        username = message.author.display_name

        # Get history
        if user_id not in conversations:
            conversations[user_id] = []

        # Check if should combine with previous message
        should_combine, prev_content = should_combine_messages(
            conversations[user_id],
            content,
            username
        )

        if should_combine and prev_content:
            # Remove last user message and combine
            if conversations[user_id] and conversations[user_id][-1].get("role") == "user":
                conversations[user_id].pop()
            # Combine messages
            combined_content = f"{prev_content}\n{content}"
            final_content = f"[{username}]: {combined_content}"
        else:
            final_content = f"[{username}]: {content}"

        # Build context
        system = SYSTEM_PROMPT
        if user_id in user_memories and user_memories[user_id]:
            info = "\n".join([f"- {k}: {v}" for k, v in user_memories[user_id].items()])
            system += f"\n\nThong tin ve {username}:\n{info}"

        # Chat
        async with message.channel.typing():
            try:
                messages = [{"role": "system", "content": system}]
                messages.extend(conversations[user_id])
                messages.append({"role": "user", "content": final_content})

                response = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=500
                )

                reply = response.choices[0].message.content

                # Save history
                conversations[user_id].append({"role": "user", "content": final_content})
                conversations[user_id].append({"role": "assistant", "content": reply})

                if len(conversations[user_id]) > 40:
                    conversations[user_id] = conversations[user_id][-40:]

            except Exception as e:
                reply = f"Loi: {e}"

        await message.reply(reply, mention_author=False)

    @bot.command(name='clear')
    async def clear_cmd(ctx):
        user_id = str(ctx.author.id)
        conversations[user_id] = []
        await ctx.reply("Da clear history")

    @bot.command(name='info')
    async def info_cmd(ctx):
        user_id = str(ctx.author.id)
        if user_id in user_memories and user_memories[user_id]:
            info = "\n".join([f"- {k}: {v}" for k, v in user_memories[user_id].items()])
            await ctx.reply(f"To nho:\n{info}")
        else:
            await ctx.reply("To chua biet gi ve cau")

    @bot.command(name='remember')
    async def remember_cmd(ctx, key: str, *, value: str):
        user_id = str(ctx.author.id)
        if user_id not in user_memories:
            user_memories[user_id] = {}
        user_memories[user_id][key] = value
        save_memories()
        await ctx.reply(f"Da nho: {key} = {value}")

    @bot.command(name='forget')
    async def forget_cmd(ctx):
        user_id = str(ctx.author.id)
        if user_id in user_memories:
            del user_memories[user_id]
            save_memories()
        conversations[user_id] = []
        await ctx.reply("Da quen het")

    print("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    if "--test" in sys.argv:
        run_test()
    else:
        run_discord()
