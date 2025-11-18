# Gau Keo AI

AI chatbot voi personality Gau Keo - mem mai, de thuong, Gen Z Viet.

---

## Yeu cau

- Python 3.10+
- OpenAI API key (de train qua API)
- NVIDIA GPU voi CUDA (de train local)
- Discord Bot Token (de chay bot)

---

## Cai dat

### 1. Clone repo

```bash
git clone https://github.com/GauCandy/Botchatlocal.git
cd Botchatlocal
```

### 2. Cai Python dependencies

```bash
pip install -r requirements.txt
```

Hoac cai manual:

```bash
# Core (bat buoc)
pip install openai discord.py python-dotenv tqdm httpx

# Cho local training (optional)
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers datasets peft accelerate
```

### 3. Tao file `.env`

Copy tu `.env.example`:

```bash
cp .env.example .env
```

Sau do chinh sua `.env`:

```env
# API Keys
OPENAI_API_KEY=sk-proj-...
DISCORD_TOKEN=your-discord-bot-token

# Discord Config
DISCORD_CHANNEL_ID=0        # 0 = all channels, hoac ID cu the

# Model mode cho Discord bot
MODEL_MODE=openai           # "openai" hoac "local"
```

---

## Train Model

### Option 1: Train qua OpenAI API (Recommend)

**Uu diem**: Nhanh, khong can GPU, chat luong tot
**Nhuoc diem**: Ton phi ~$3-5

```bash
python train_openai.py
```

- **Thoi gian**: 10-20 phut
- **Output**: `openai_model_id.txt`

Sau khi train xong, model ID se tu dong luu vao `openai_model_id.txt`.

### Option 2: Train Local voi GPU

**Uu diem**: Mien phi, du lieu private
**Nhuoc diem**: Can GPU 6GB+ VRAM, cham hon

#### Buoc 1: Check GPU

```bash
python check_gpu.py
```

#### Buoc 2: Cai dependencies

```bash
# PyTorch voi CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Training libraries
pip install transformers datasets peft accelerate
```

#### Buoc 3: Train

```bash
python train_local_simple.py
```

- **Thoi gian**: 30-60 phut
- **VRAM**: 6GB+
- **Model**: TinyLlama-1.1B
- **Output**: `models/gau_keo_local/`

---

## Test Model

### Test trong CMD

#### Test model OpenAI:

```bash
python test_personality.py --openai
```

#### Test model Local:

```bash
python test_personality.py --local
```

Script se:
1. Chay 4 test prompts tu dong
2. Cho ban chat truc tiep voi Gau Keo
3. Go `exit` de thoat

---

## Discord Bot

### 1. Tao Discord Bot

1. Vao https://discord.com/developers/applications
2. Click **New Application** -> Dat ten
3. Vao **Bot** -> **Reset Token** -> Copy token
4. Paste vao `.env`:
   ```env
   DISCORD_TOKEN=your-token-here
   ```

### 2. Enable Intents

Trong **Bot** settings, bat:
- **Message Content Intent**
- **Server Members Intent**

### 3. Invite Bot vao Server

1. Vao **OAuth2** -> **URL Generator**
2. **Scopes**: chon `bot`
3. **Bot Permissions**:
   - Send Messages
   - Read Message History
   - Read Messages/View Channels
4. Copy URL -> Mo trong browser -> Chon server

### 4. Cau hinh Channel (Optional)

Lay Channel ID:
1. Discord Settings -> Advanced -> Bat **Developer Mode**
2. Right-click channel -> **Copy ID**
3. Paste vao `.env`:
   ```env
   DISCORD_CHANNEL_ID=1234567890123456789
   ```

Neu de `0`, bot se respond trong tat ca channels.

### 5. Chon Model Mode

Trong `.env`:

```env
# Dung OpenAI model
MODEL_MODE=openai

# Hoac dung Local model
MODEL_MODE=local
```

### 6. Chay Bot

```bash
python discord_bot.py
```

### Bot Commands

| Command | Mo ta |
|---------|-------|
| `!clear` | Xoa conversation history |
| `!info` | Xem Gau nho gi ve ban |
| `!forget` | Gau quen het ve ban |
| `!remember key value` | Bao Gau nho thong tin |
| `!mode` | Xem dang dung model nao |

---

## Cau truc Project

```
Botchatlocal/
├── train_openai.py          # Train qua OpenAI API
├── train_local_simple.py    # Train local voi GPU
├── test_personality.py      # Test model trong CMD
├── discord_bot.py           # Discord bot
├── check_gpu.py             # Check GPU/CUDA
├── requirements.txt         # Dependencies
├── .env                     # API keys & config (tu tao)
├── .env.example             # Template cho .env
├── openai_model_id.txt      # Model ID sau khi train OpenAI
├── user_memories.json       # Bot memories
├── training_data/
│   └── gau_keo/
│       ├── conversations.json      # Training data
│       └── personality_profile.json # Personality config
├── models/
│   └── gau_keo_local/       # Model sau khi train local
└── generators/              # Scripts tao training data
```

---

## So sanh 2 phuong phap Train

| | OpenAI API | Local GPU |
|---|---|---|
| **Chi phi** | ~$3-5 | Mien phi |
| **Thoi gian** | 10-20 phut | 30-60 phut |
| **GPU** | Khong can | Can 6GB+ VRAM |
| **Chat luong** | Tot (GPT-4o-mini) | Kha (TinyLlama-1.1B) |
| **Privacy** | Data gui len cloud | Data o local |
| **Deployment** | Can internet + API key | Chay offline duoc |

---

## Troubleshooting

### Loi "CUDA not available"

```bash
# Check CUDA
python check_gpu.py

# Cai lai PyTorch voi CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Loi "openai_model_id.txt not found"

Ban chua train model. Chay:
```bash
python train_openai.py
```

### Loi "models/gau_keo_local not found"

Ban chua train local. Chay:
```bash
python train_local_simple.py
```

### Loi OpenAI API

```bash
# Upgrade openai library
pip install --upgrade openai httpx
```

### Discord bot khong respond

1. Check **Message Content Intent** da bat chua
2. Check `DISCORD_CHANNEL_ID` dung chua
3. Check bot da duoc invite voi dung permissions chua

---

## Personality

- **Ten**: Gau Keo (goi Gau)
- **Tuoi**: Ky uc tu 2007
- **Gioi tinh**: Tranh labels - "goi Gau thoi di"
- **Style**: Casual Gen Z Viet
- **Emoji**: penguin

---

## Quick Start

### Nhanh nhat - Dung OpenAI:

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env: them OPENAI_API_KEY va DISCORD_TOKEN

# 2. Train
python train_openai.py

# 3. Test
python test_personality.py --openai

# 4. Chay bot
python discord_bot.py
```

### Mien phi - Dung Local GPU:

```bash
# 1. Setup
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers datasets peft accelerate
cp .env.example .env
# Edit .env: them DISCORD_TOKEN, set MODEL_MODE=local

# 2. Train
python train_local_simple.py

# 3. Test
python test_personality.py --local

# 4. Chay bot
python discord_bot.py
```
