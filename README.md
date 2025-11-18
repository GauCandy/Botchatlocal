# Gau Keo AI

AI chatbot voi personality Gau Keo - mem mai, de thuong, Gen Z Viet.

## Yeu cau

- Python 3.10+
- OpenAI API key (~$3-5 de train)
- Discord Bot Token (cho Discord bot)

## Cai dat

### 1. Clone repo

```bash
git clone https://github.com/GauCandy/Botchatlocal.git
cd Botchatlocal
```

### 2. Cai dependencies

```bash
pip install openai discord.py python-dotenv
```

### 3. Tao file .env

```bash
cp .env.example .env
```

Chinh sua `.env`:

```env
OPENAI_API_KEY=sk-proj-...
DISCORD_TOKEN=your-discord-bot-token
DISCORD_CHANNEL_ID=0
```

## Su dung

### Train model

```bash
python train.py
```

- Chi phi: ~$3-5
- Thoi gian: 10-20 phut
- Model ID se luu vao `openai_model_id.txt`

### Test trong console

```bash
python bot.py --test
```

### Chay Discord bot

```bash
python bot.py
```

## Setup Discord Bot

1. Vao https://discord.com/developers/applications
2. **New Application** -> Dat ten
3. **Bot** -> **Reset Token** -> Copy
4. Paste vao `.env`: `DISCORD_TOKEN=...`
5. **Bot** settings -> Bat **Message Content Intent**
6. **OAuth2** -> **URL Generator**:
   - Scopes: `bot`
   - Permissions: Send Messages, Read Message History
7. Copy URL -> Mo trong browser -> Chon server

## Bot Commands

| Command | Mo ta |
|---------|-------|
| `!clear` | Xoa conversation history |
| `!info` | Xem Gau nho gi ve ban |
| `!remember key value` | Bao Gau nho thong tin |
| `!forget` | Gau quen het ve ban |

## Cau truc

```
Botchatlocal/
├── train.py             # Train model
├── bot.py               # Discord bot + test
├── .env                 # API keys (tu tao)
├── .env.example         # Template
├── openai_model_id.txt  # Model ID sau khi train
├── user_memories.json   # Bot memories
└── training_data/
    └── gau_keo/
        ├── conversations.json
        └── personality_profile.json
```

## Quick Start

```bash
# 1. Cai dat
pip install openai discord.py python-dotenv
cp .env.example .env
# Chinh sua .env: them API keys

# 2. Train
python train.py

# 3. Test
python bot.py --test

# 4. Chay Discord bot
python bot.py
```
