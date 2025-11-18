# 🐧 Gấu Kẹo AI

AI chatbot với personality Gấu Kẹo - mềm mại, dễ thương, Gen Z Việt.

## 🚀 Quick Start

### 1. Cài dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup API keys
Tạo file `.env`:
```env
OPENAI_API_KEY=sk-proj-...
DISCORD_TOKEN=your-discord-bot-token
```

### 3. Chạy Discord Bot
```bash
python discord_bot.py
```

---

## 📁 Cấu trúc

```
├── discord_bot.py          # Discord bot với memory
├── train_openai.py         # Train model trên OpenAI
├── test_personality.py     # Test model trong console
├── training_data/
│   └── gau_keo/
│       ├── conversations.json      # 100 conversations training
│       └── personality_profile.json # Personality config
└── .env                    # API keys (tự tạo)
```

---

## 🤖 Discord Bot

### Tính năng
- **Memory**: Nhớ conversation history per user
- **User info**: Lưu thông tin quan trọng về mỗi user
- **Channel lock**: Chỉ respond trong channel được chỉ định

### Commands
- `!clear` - Xóa conversation history
- `!info` - Xem Gấu nhớ gì về bạn
- `!forget` - Gấu quên hết về bạn
- `!remember key value` - Bảo Gấu nhớ thông tin

### Setup Discord Bot
1. Vào https://discord.com/developers/applications
2. New Application → Bot → Reset Token → Copy
3. Paste vào `.env`: `DISCORD_TOKEN=...`
4. OAuth2 → URL Generator → Scopes: bot → Permissions: Send Messages, Read Message History
5. Invite bot vào server

---

## 🎯 Training

### OpenAI Training (Recommend)
```bash
python train_openai.py
```
- Chi phí: ~$3-5
- Thời gian: 10-20 phút
- Model lưu trên cloud OpenAI

### Test model
```bash
python test_personality.py --openai
```

---

## 🐧 Personality

- **Tên**: Gấu Kẹo (gọi Gấu)
- **Tuổi**: Ký ức từ 2007, thân thể không biết
- **Giới tính**: Tránh labels - "gọi Gấu thôi đi 🐧"
- **Style**: Casual Gen Z Việt, dùng emoji 🐧💙✨
- **Emoticons**: :v =)) :b ;b

---

## 📝 Notes

- Model đã train: `ft:gpt-4o-mini-2024-07-18:personal:gau-keo:Cd4nIymn`
- Channel ID: `1440177885259497566`
- User memories lưu trong `user_memories.json`
