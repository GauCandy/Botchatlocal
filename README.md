# 🐧 Gấu Kẹo AI

AI chatbot với personality Gấu Kẹo - mềm mại, dễ thương, Gen Z Việt.

---

## 📋 Yêu cầu

- Python 3.10+
- OpenAI API key (để train và chat)
- Discord Bot Token (để chạy bot)
- (Optional) NVIDIA GPU với CUDA để train local

---

## 🚀 Cài đặt

### 1. Clone repo
```bash
git clone https://github.com/GauCandy/Botchatlocal.git
cd Botchatlocal
```

### 2. Cài Python dependencies
```bash
pip install -r requirements.txt
```

Hoặc cài manual:
```bash
pip install openai discord.py python-dotenv tqdm httpx
```

### 3. Tạo file `.env`
```env
# OpenAI API Key - Lấy tại: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-...

# Discord Bot Token - Lấy tại: https://discord.com/developers/applications
DISCORD_TOKEN=...
```

---

## 🎯 Train Model

### OpenAI Training (Recommend)

```bash
python train_openai.py
```

- **Chi phí**: ~$3-5
- **Thời gian**: 10-20 phút
- **Data**: 100 conversations trong `training_data/gau_keo/conversations.json`

Sau khi train xong, model ID sẽ lưu trong `openai_model_id.txt`

### Local GPU Training (Optional)

Yêu cầu: NVIDIA GPU với CUDA

```bash
# 1. Cài PyTorch với CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2. Cài unsloth
pip install unsloth

# 3. Train
python train_local_gpu.py
```

- **Chi phí**: Miễn phí
- **Thời gian**: 1-2 giờ
- **Model**: Lưu trong `models/gau_keo_local/`

---

## 🤖 Chạy Discord Bot

### 1. Tạo Discord Bot

1. Vào https://discord.com/developers/applications
2. **New Application** → Đặt tên
3. Vào **Bot** → **Reset Token** → Copy token
4. Paste vào `.env`: `DISCORD_TOKEN=...`

### 2. Invite Bot vào Server

1. Vào **OAuth2** → **URL Generator**
2. Scopes: ✅ `bot`
3. Bot Permissions:
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Read Messages/View Channels
4. Copy URL → Mở trong browser → Chọn server

### 3. Chạy Bot

```bash
python discord_bot.py
```

### Commands

- `!clear` - Xóa conversation history
- `!info` - Xem Gấu nhớ gì về bạn
- `!forget` - Gấu quên hết về bạn
- `!remember key value` - Bảo Gấu nhớ thông tin

---

## 🧪 Test trong Console

```bash
python test_personality.py --openai
```

---

## 📁 Cấu trúc

```
├── discord_bot.py              # Discord bot với memory system
├── train_openai.py             # Train trên OpenAI cloud
├── train_local_gpu.py          # Train local với GPU
├── test_personality.py         # Test model trong console
├── requirements.txt            # Python dependencies
├── .env                        # API keys (tự tạo)
├── training_data/
│   └── gau_keo/
│       ├── conversations.json       # 100 conversations training
│       └── personality_profile.json # Personality config
└── generators/                 # Scripts tạo training data
```

---

## 🐧 Personality

- **Tên**: Gấu Kẹo (gọi Gấu)
- **Tuổi**: Ký ức từ 2007, thân thể không biết
- **Giới tính**: Tránh labels - "gọi Gấu thôi đi 🐧"
- **Style**: Casual Gen Z Việt
- **Emoji**: 🐧💙✨
- **Emoticons**: :v =)) :b ;b

---

## 📝 Notes

- Model đã train: `ft:gpt-4o-mini-2024-07-18:personal:gau-keo:Cd4nIymn`
- Bot chỉ respond trong channel ID: `1440177885259497566`
- User memories lưu trong `user_memories.json`
