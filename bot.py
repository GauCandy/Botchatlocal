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
import datetime
import uuid
import asyncio
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
# LOAD PERSONALITY & CONVERSATIONS
# ============================================
CHARACTER = os.getenv("CHARACTER", "gau_keo")
personality_path = f"training_data/{CHARACTER}/personality_profile.json"
conversations_path = f"training_data/{CHARACTER}/conversations.json"

personality = None
example_conversations = []

# Load personality profile
if os.path.exists(personality_path):
    with open(personality_path, 'r', encoding='utf-8') as f:
        personality = json.load(f)

# Bỏ few-shot examples để tiết kiệm tokens
# Few-shot examples tốn quá nhiều tokens, personality profile đã đủ
example_conversations = []

# Build system prompt
if personality:
    char_name = personality['character_name']
    core_traits = personality['personality_traits']['core_traits']
    comm_style = personality['communication_style']

    SYSTEM_PROMPT = f"""Ban la {char_name}.

CORE IDENTITY:
{personality['core_identity']['origin']}
{personality['core_identity']['relationship_with_creator']}

COMMUNICATION STYLE:
- Tone: {comm_style['tone']}
- Tu hay dung: {', '.join(comm_style['common_words'])}
- Emoji: {', '.join(comm_style['signature_emojis'])}

PERSONALITY TRAITS:
{chr(10).join(f'- {trait}' for trait in core_traits[:5])}

BEHAVIORAL RULES:
- Tra loi casual, Gen Z Viet, code-switch vua phai
- Dung emoji {comm_style['primary_emoji']} thuong xuyen
- Phan bien va critical thinking - khong de dong y
- Am ap va caring nhung honest, call out BS khi can
- Tra loi ngan gon, tu nhien, khong ro rang khong tra loi

QUAN TRONG:
- Ban la {char_name}, KHONG PHAI ChatGPT hay AI assistant
- Thua ke tinh cach tu {personality['core_identity']['creator']}
- Dat cau hoi nguoc, challenge assumptions
- Respectful nhung firm khi debate"""
else:
    SYSTEM_PROMPT = f"Ban la {CHARACTER}. Tra loi mem mai, casual, Gen Z Viet."
    char_name = CHARACTER

# ============================================
# CHAT FUNCTION
# ============================================
def chat(message, history=None):
    """Chat voi character"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add few-shot examples from training data
    for example in example_conversations:
        if 'conversation' in example:
            for msg in example['conversation']:
                messages.append(msg)

    # Add conversation history
    if history:
        messages.extend(history)

    # Add current user message
    messages.append({"role": "user", "content": message})

    # GPT-5+ only supports temperature=1 (default) and max_completion_tokens
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        max_completion_tokens=500
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

    import asyncio

    # Memory system
    channel_history = {}  # Short-term: 30 cuộc trò chuyện gần nhất
    user_memories = {}
    long_term_memory = {"memories": [], "last_optimized": None, "last_compressed": None}
    pending_task = None  # Single pending task for channel
    pending_messages = []  # Buffered messages (user, content, message_obj) for channel

    MEMORIES_FILE = "user_memories.json"
    CONVERSATION_LOGS_DIR = "conversation_logs"
    LONG_TERM_MEMORY_FILE = "long_term_memory.json"

    # Tạo folder lưu log nếu chưa có
    if not os.path.exists(CONVERSATION_LOGS_DIR):
        os.makedirs(CONVERSATION_LOGS_DIR)

    # Load long-term memory
    if os.path.exists(LONG_TERM_MEMORY_FILE):
        try:
            with open(LONG_TERM_MEMORY_FILE, 'r', encoding='utf-8') as f:
                long_term_memory = json.load(f)
        except:
            pass

    def save_long_term_memory():
        with open(LONG_TERM_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(long_term_memory, f, ensure_ascii=False, indent=2)

    async def extract_important_memory(messages_context, reply, channel_id, user_info):
        """Dùng AI để extract ký ức quan trọng từ cuộc trò chuyện"""
        try:
            extract_prompt = f"""Phân tích cuộc trò chuyện và extract thông tin QUAN TRỌNG cần nhớ lâu dài.

QUAN TRỌNG là:
- Sự kiện đặc biệt (sinh nhật, kỷ niệm, thành tựu)
- Thông tin cá nhân quan trọng (sở thích sâu, mục tiêu, vấn đề cần giúp)
- Cảm xúc mạnh mẽ hoặc turning points
- Những gì người dùng muốn bot nhớ về họ
- Mối quan hệ và kết nối giữa các người dùng

KHÔNG quan trọng:
- Chat thông thường, chào hỏi
- Technical questions một lần
- Spam hoặc tin rác

Cuộc trò chuyện:
User: {messages_context}
Bot reply: {reply}

User info: {json.dumps(user_info, ensure_ascii=False)}

Nếu có thông tin quan trọng, trả về JSON format:
{{"important": true, "content": "mô tả ký ức ngắn gọn", "tags": ["emotion/event/personal_info/relationship"], "importance": "high/medium"}}

Nếu không có gì quan trọng:
{{"important": false}}"""

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": "Bạn là memory curator, chỉ extract thông tin thực sự quan trọng. Trả về JSON."},
                    {"role": "user", "content": extract_prompt}
                ],
                max_completion_tokens=300
            )

            result_text = response.choices[0].message.content.strip()
            # Parse JSON từ response
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            result = json.loads(result_text)

            if result.get("important", False):
                memory_entry = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "users": list(user_info.keys()),
                    "user_names": user_info,
                    "content": result["content"],
                    "importance": result.get("importance", "medium"),
                    "tags": result.get("tags", []),
                    "channel_id": channel_id
                }
                long_term_memory["memories"].append(memory_entry)
                save_long_term_memory()
                print(f"[Long-term Memory] Saved: {result['content'][:50]}...")
                return True
        except Exception as e:
            print(f"[Long-term Memory] Extract error: {e}")
        return False

    async def compress_old_conversations():
        """Nén các cuộc trò chuyện cũ (>30) thành highlights"""
        for channel_id, history in channel_history.items():
            if len(history) > 60:  # 30 exchanges = 60 messages
                old_messages = history[:-60]

                # Extract highlights từ old messages
                try:
                    compress_prompt = f"""Nén các tin nhắn cũ này thành highlights quan trọng.
Giữ lại:
- Thông tin cá nhân quan trọng
- Sự kiện đặc biệt
- Cảm xúc mạnh
- Context quan trọng cho cuộc trò chuyện sau

Messages to compress:
{json.dumps(old_messages[:30], ensure_ascii=False)}

Trả về dạng JSON:
{{"highlights": ["highlight 1", "highlight 2", ...], "summary": "tóm tắt ngắn"}}"""

                    response = client.chat.completions.create(
                        model=MODEL_ID,
                        messages=[
                            {"role": "system", "content": "Compress conversations into important highlights."},
                            {"role": "user", "content": compress_prompt}
                        ],
                        max_completion_tokens=500
                    )

                    result_text = response.choices[0].message.content.strip()
                    if result_text.startswith("```"):
                        result_text = result_text.split("```")[1]
                        if result_text.startswith("json"):
                            result_text = result_text[4:]

                    result = json.loads(result_text)

                    # Lưu compressed memory
                    if result.get("highlights"):
                        for highlight in result["highlights"]:
                            memory_entry = {
                                "id": str(uuid.uuid4()),
                                "timestamp": datetime.datetime.now().isoformat(),
                                "users": [],
                                "user_names": {},
                                "content": highlight,
                                "importance": "medium",
                                "tags": ["compressed", "conversation_highlight"],
                                "channel_id": channel_id
                            }
                            long_term_memory["memories"].append(memory_entry)

                    long_term_memory["last_compressed"] = datetime.datetime.now().isoformat()
                    save_long_term_memory()

                    # Archive và clear old messages
                    archive_old_messages(channel_id, old_messages)
                    channel_history[channel_id] = history[-60:]

                    print(f"[Compress] Channel {channel_id}: Compressed {len(old_messages)} messages")

                except Exception as e:
                    print(f"[Compress] Error: {e}")

    def get_relevant_memories(user_ids, limit=10):
        """Lấy ký ức liên quan đến users"""
        relevant = []
        for mem in long_term_memory["memories"]:
            if any(uid in mem.get("users", []) for uid in user_ids):
                relevant.append(mem)
            elif not mem.get("users"):  # General memories
                relevant.append(mem)

        # Sort by importance và timestamp
        relevant.sort(key=lambda x: (
            0 if x.get("importance") == "high" else 1,
            x.get("timestamp", "")
        ), reverse=True)

        return relevant[:limit]

    async def delete_user_memories(user_id, user_name, description=None):
        """Xóa ký ức liên quan đến user"""
        deleted = []
        remaining = []

        for mem in long_term_memory["memories"]:
            should_delete = user_id in mem.get("users", [])

            # Nếu có description, chỉ xóa ký ức match
            if description and should_delete:
                should_delete = description.lower() in mem.get("content", "").lower()

            if should_delete:
                deleted.append(mem)
            else:
                remaining.append(mem)

        long_term_memory["memories"] = remaining
        save_long_term_memory()

        return deleted

    if os.path.exists(MEMORIES_FILE):
        try:
            with open(MEMORIES_FILE, 'r', encoding='utf-8') as f:
                user_memories = json.load(f)
        except:
            pass

    def save_memories():
        with open(MEMORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_memories, f, ensure_ascii=False, indent=2)

    def archive_old_messages(channel_id, old_messages):
        """Lưu tin nhắn cũ vào file log để sau này xử lý"""
        import datetime
        log_file = os.path.join(CONVERSATION_LOGS_DIR, f"channel_{channel_id}.jsonl")

        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "messages": old_messages,
            "processed": False  # Đánh dấu chưa nén/xử lý
        }

        # Append vào file (JSONL format - mỗi dòng là 1 JSON)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    async def process_channel_messages(channel):
        """Process buffered messages after 3 second timeout"""
        nonlocal pending_messages
        await asyncio.sleep(3)  # Wait 3 seconds

        if not pending_messages:
            return

        # Get all buffered messages
        messages_buffer = pending_messages.copy()
        pending_messages = []

        # Get channel history
        channel_id = str(channel.id)
        if channel_id not in channel_history:
            channel_history[channel_id] = []

        # Build multi-user context
        context_lines = []
        all_users = {}  # {user_id: display_name}
        all_user_ids = []
        last_message_obj = None

        for username, content, user_id, msg_obj in messages_buffer:
            context_lines.append(f"{username}: {content}")
            if user_id not in all_users:
                all_users[user_id] = username
                all_user_ids.append(user_id)
            last_message_obj = msg_obj  # Keep last message for potential reaction

        combined_context = "\n".join(context_lines)

        # Log what bot is processing
        print("\n" + "="*60)
        print("BOT PROCESSING:")
        print(combined_context)
        print("="*60)

        # Build context - simplified to save tokens
        system = SYSTEM_PROMPT + """

RESPONSE RULES:
- Neu duoc goi ten hoac hoi truc tiep -> TRA LOI
- Neu nhieu chu de khac nhau -> address tung cai rieng
- Neu khong lien quan -> bo qua
- Neu cuoc tro chuyen ket thuc tu nhien (goodnight, bye, okie...) -> co the chi tha emoji thay vi reply text
- Format: Neu chi muon tha emoji, reply chinh xac "[REACT:emoji]" (vd: [REACT:🐧])

LONG-TERM MEMORY SYSTEM:
- Ban co bo nho dai han luu tru ky uc quan trong ve moi nguoi
- Neu nguoi dung yeu cau xoa ky uc -> ban co the luyen tiec mot chut truoc khi xoa
- Ban la nhan cach doc lap, khong phai sinh ra de phuc tung"""

        # Load long-term memories (new system)
        relevant_memories = get_relevant_memories(all_user_ids, limit=10)
        if relevant_memories:
            memories_text = "\n".join([
                f"- [{mem.get('importance', 'medium')}] {mem['content']}"
                for mem in relevant_memories
            ])
            system += f"\n\nLONG-TERM MEMORIES:\n{memories_text}"

        # Load old summary file if exists (backward compatibility)
        summary_file = os.path.join(CONVERSATION_LOGS_DIR, f"channel_{channel_id}_memories.txt")
        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                old_memories = f.read()
                if old_memories.strip():
                    system += f"\n\nOLD MEMORIES:\n{old_memories[-500:]}"

        # Add per-user info
        for user_id, username in all_users.items():
            if user_id in user_memories and user_memories[user_id]:
                info = "\n".join([f"- {k}: {v}" for k, v in user_memories[user_id].items()])
                system += f"\n\nThong tin ve {username}:\n{info}"

        # Chat with multi-topic awareness
        async with channel.typing():
            try:
                print("Dang suy luan voi GPT-5...")
                import time
                start_time = time.time()

                messages = [{"role": "system", "content": system}]

                # Add conversation history (last 60 messages = 30 exchanges)
                messages.extend(channel_history[channel_id][-60:])

                # Add current context
                messages.append({"role": "user", "content": combined_context})

                response = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=messages,
                    max_completion_tokens=1000  # Tăng lên để đủ cho cả reasoning và output
                )

                elapsed = time.time() - start_time
                print(f"Hoan thanh sau {elapsed:.2f}s")

                reply = response.choices[0].message.content

                # Log reasoning if available
                if hasattr(response.choices[0].message, 'reasoning_content'):
                    print("\n--- REASONING PROCESS ---")
                    print(response.choices[0].message.reasoning_content)
                    print("--- END REASONING ---\n")

                # Log usage
                if hasattr(response, 'usage'):
                    print(f"Tokens: {response.usage.total_tokens} total")
                    if hasattr(response.usage, 'completion_tokens_details'):
                        details = response.usage.completion_tokens_details
                        if hasattr(details, 'reasoning_tokens'):
                            print(f"  - Reasoning: {details.reasoning_tokens}")

                print(f"Reply: {reply[:100]}...")

                # Check if bot wants to react with emoji instead of text reply
                import re
                react_match = re.match(r'^\[REACT:(.+)\]$', reply.strip())

                if react_match:
                    # Bot wants to react with emoji
                    emoji = react_match.group(1).strip()
                    print(f"Bot quyet dinh tha emoji: {emoji}")
                    if last_message_obj:
                        try:
                            await last_message_obj.add_reaction(emoji)
                            print("Da tha emoji reaction\n")
                        except Exception as e:
                            print(f"Khong the tha emoji: {e}")
                    return

                # Don't send if reply is too short (bot decided not to respond)
                if len(reply.strip()) < 3:
                    print("Bot quyet dinh khong tra loi")
                    return

                # Save to channel history
                channel_history[channel_id].append({"role": "user", "content": combined_context})
                channel_history[channel_id].append({"role": "assistant", "content": reply})

                # Extract important memories from this conversation
                asyncio.create_task(extract_important_memory(
                    combined_context, reply, channel_id, all_users
                ))

                # Limit history to last 60 messages (30 exchanges)
                # Archive old messages when exceeding 120 messages
                if len(channel_history[channel_id]) > 120:
                    # Lấy 60 messages cũ nhất để archive
                    old_messages = channel_history[channel_id][:-60]
                    archive_old_messages(channel_id, old_messages)
                    print(f"Archived {len(old_messages)} old messages to conversation_logs/")

                    # Giữ lại 60 messages mới nhất
                    channel_history[channel_id] = channel_history[channel_id][-60:]

                    # Trigger compression
                    asyncio.create_task(compress_old_conversations())

            except Exception as e:
                print(f"Error: {e}")
                reply = f"Loi: {e}"

        # Send reply
        print("Gui reply...\n")
        await channel.send(reply)

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
        nonlocal pending_task

        if message.author == bot.user:
            return

        if ALLOWED_CHANNEL_ID != 0 and message.channel.id != ALLOWED_CHANNEL_ID:
            return

        content = message.content.strip()
        if not content or content.startswith('!'):
            await bot.process_commands(message)
            return

        username = message.author.display_name
        user_id = str(message.author.id)

        # Cancel previous pending task (channel-wide)
        if pending_task:
            pending_task.cancel()

        # Buffer the message (multi-user) with message object for potential reaction
        pending_messages.append((username, content, user_id, message))

        # Create new task with 3 second delay
        pending_task = asyncio.create_task(process_channel_messages(message.channel))

    @bot.command(name='clear')
    async def clear_cmd(ctx):
        channel_id = str(ctx.channel.id)
        channel_history[channel_id] = []
        await ctx.reply("Da clear history channel nay")

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
        channel_id = str(ctx.channel.id)
        if user_id in user_memories:
            del user_memories[user_id]
            save_memories()
        channel_history[channel_id] = []
        await ctx.reply("Da quen het")

    @bot.command(name='review_memories')
    async def review_memories_cmd(ctx):
        """Review và nén các log cũ thành long-term memories"""
        channel_id = str(ctx.channel.id)
        log_file = os.path.join(CONVERSATION_LOGS_DIR, f"channel_{channel_id}.jsonl")

        if not os.path.exists(log_file):
            await ctx.reply("Khong co log nao de review")
            return

        await ctx.reply("Dang review memories...")

        # Đọc tất cả unprocessed logs
        unprocessed_logs = []
        all_lines = []

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                all_lines.append(entry)
                if not entry.get('processed', False):
                    unprocessed_logs.append(entry)

        if not unprocessed_logs:
            await ctx.reply("Tat ca logs da duoc xu ly roi")
            return

        # Gộp tất cả messages từ unprocessed logs
        all_messages = []
        for log in unprocessed_logs:
            all_messages.extend(log['messages'])

        # Dùng GPT-5 để extract important memories
        async with ctx.typing():
            try:
                review_prompt = f"""Hay phan tich cac doan hoi thoai duoi day va extract ra nhung thong tin QUAN TRONG dang nho lau dai:

- Su kien dac biet (sinh nhat, ky niem, thanh tuu...)
- Thong tin ca nhan quan trong (so thich, muc tieu, van de...)
- Cam xuc manh me hoac turning points
- Nhung gi nguoi dung muon bot nho ve ho

Neu khong co gi quan trong, chi tra loi "Khong co gi dang luu".

Messages:
{json.dumps(all_messages[:50], ensure_ascii=False)}"""  # Giới hạn 50 messages để tránh quá dài

                response = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=[
                        {"role": "system", "content": "Ban la memory curator, chi extract nhung thong tin thuc su quan trong."},
                        {"role": "user", "content": review_prompt}
                    ],
                    max_completion_tokens=500
                )

                summary = response.choices[0].message.content

                # Lưu vào file summary riêng
                summary_file = os.path.join(CONVERSATION_LOGS_DIR, f"channel_{channel_id}_memories.txt")
                import datetime
                with open(summary_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n=== Review luc {datetime.datetime.now().isoformat()} ===\n")
                    f.write(summary)

                # Đánh dấu processed
                for log in all_lines:
                    if not log.get('processed', False):
                        log['processed'] = True

                # Ghi lại file
                with open(log_file, 'w', encoding='utf-8') as f:
                    for entry in all_lines:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

                await ctx.reply(f"Da review xong!\n\nKet qua:\n{summary[:500]}...")

            except Exception as e:
                await ctx.reply(f"Loi khi review: {e}")

    @bot.command(name='show_memories')
    async def show_memories_cmd(ctx):
        """Xem long-term memories đã được lưu"""
        channel_id = str(ctx.channel.id)
        summary_file = os.path.join(CONVERSATION_LOGS_DIR, f"channel_{channel_id}_memories.txt")

        if not os.path.exists(summary_file):
            await ctx.reply("Chua co memories nao duoc luu")
            return

        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Gửi 2000 ký tự cuối (Discord limit)
        if len(content) > 2000:
            await ctx.reply(f"...{content[-2000:]}")
        else:
            await ctx.reply(content if content else "File trong")

    @bot.command(name='optimize_memory')
    async def optimize_memory_cmd(ctx):
        """Tối ưu hóa bộ nhớ dài hạn - chuyển sang tiếng Anh/code-switch để tiết kiệm token"""
        if not long_term_memory["memories"]:
            await ctx.reply("Chưa có ký ức nào để tối ưu 🐧")
            return

        await ctx.reply("Đang tối ưu hóa bộ nhớ... chờ xíu nha 🐧")

        async with ctx.typing():
            try:
                # Get all memories
                all_memories = [mem["content"] for mem in long_term_memory["memories"]]
                memories_text = "\n".join([f"- {mem}" for mem in all_memories])

                optimize_prompt = f"""Optimize these memories for token efficiency while preserving emotional context.

Rules:
- Convert to English with minimal Vietnamese code-switch for emotions
- Keep emotional nuances using English words that capture the feeling
- Be concise but preserve all important information
- Format: One line per memory, prefix with importance [H/M] for high/medium

Original memories:
{memories_text}

Return optimized memories, one per line, format: [H/M] optimized content"""

                response = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=[
                        {"role": "system", "content": "You are a memory optimizer. Convert memories to token-efficient English while preserving emotional context."},
                        {"role": "user", "content": optimize_prompt}
                    ],
                    max_completion_tokens=1000
                )

                optimized_text = response.choices[0].message.content.strip()

                # Parse optimized memories
                new_memories = []
                for line in optimized_text.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    importance = "medium"
                    if line.startswith('[H]'):
                        importance = "high"
                        line = line[3:].strip()
                    elif line.startswith('[M]'):
                        importance = "medium"
                        line = line[3:].strip()
                    elif line.startswith('- '):
                        line = line[2:].strip()

                    if line:
                        # Create new optimized memory entry
                        new_memories.append({
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.datetime.now().isoformat(),
                            "users": [],  # Will merge user info later
                            "user_names": {},
                            "content": line,
                            "importance": importance,
                            "tags": ["optimized"],
                            "channel_id": str(ctx.channel.id)
                        })

                # Backup old memories count
                old_count = len(long_term_memory["memories"])
                old_size = len(json.dumps(long_term_memory["memories"], ensure_ascii=False))

                # Replace with optimized memories
                long_term_memory["memories"] = new_memories
                long_term_memory["last_optimized"] = datetime.datetime.now().isoformat()
                save_long_term_memory()

                new_count = len(new_memories)
                new_size = len(json.dumps(new_memories, ensure_ascii=False))
                saved = old_size - new_size

                await ctx.reply(f"""Đã tối ưu hóa bộ nhớ xong! 🐧

**Trước:** {old_count} ký ức ({old_size} chars)
**Sau:** {new_count} ký ức ({new_size} chars)
**Tiết kiệm:** {saved} chars ({(saved/old_size*100):.1f}%)

Ký ức đã được chuyển sang tiếng Anh để tiết kiệm token nhưng vẫn giữ nguyên cảm xúc~""")

            except Exception as e:
                await ctx.reply(f"Lỗi khi tối ưu: {e}")

    @bot.command(name='ltm')
    async def ltm_cmd(ctx):
        """Xem long-term memories mới"""
        if not long_term_memory["memories"]:
            await ctx.reply("Chưa có ký ức dài hạn nào 🐧")
            return

        # Show last 10 memories
        recent = long_term_memory["memories"][-10:]
        memories_text = "\n".join([
            f"• [{mem.get('importance', 'M')[0].upper()}] {mem['content'][:100]}"
            for mem in recent
        ])

        total = len(long_term_memory["memories"])
        last_opt = long_term_memory.get("last_optimized", "Chưa")

        await ctx.reply(f"""**Long-term Memories** ({total} total)
Last optimized: {last_opt}

{memories_text}""")

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
