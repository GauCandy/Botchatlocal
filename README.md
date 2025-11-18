# Gau Keo AI

AI chatbot với personality tùy chỉnh - hỗ trợ nhiều nhân vật (Gấu Kẹo, WhiteCat, v.v.)

## Yêu cầu

- Python 3.10+
- OpenAI API key
- Discord Bot Token (cho Discord bot)

## Cài đặt

### 1. Clone repo

```bash
git clone https://github.com/GauCandy/Botchatlocal.git
cd Botchatlocal
```

### 2. Cài dependencies

```bash
pip install openai discord.py python-dotenv
```

### 3. Tạo file .env

```bash
cp .env.example .env
```

Chỉnh sửa `.env`:

```env
# Bắt buộc
OPENAI_API_KEY=sk-proj-...
DISCORD_TOKEN=your-discord-bot-token

# Tùy chọn
DISCORD_CHANNEL_ID=0                    # 0 = tất cả channels
CHARACTER=gau_keo                        # Nhân vật để train (gau_keo, whitecat)
OPENAI_MODEL_ID=                         # Model ID sau khi train
DECISION_MODEL=gpt-4o-mini               # Model cho quyết định gộp tin nhắn
FINETUNE_BASE_MODEL=gpt-4o-mini-2024-07-18  # Model base để fine-tune
```

## Sử dụng

### Train model

```bash
# Train nhân vật (đọc từ CHARACTER trong .env)
python train.py

# Xem danh sách jobs
python train.py --list

# Hủy job đang chạy
python train.py --cancel
python train.py --cancel <job_id>
```

**Lưu ý:**
- Có xác nhận trước khi train (tốn tiền)
- Chi phí: ~$0.05-0.10 mỗi lần train
- Thời gian: 10-20 phút
- Model ID lưu vào `openai_model_id.txt`

### Test trong console

```bash
python bot.py --test
```

### Chạy Discord bot

```bash
python bot.py
```

## Nhân vật

Mỗi nhân vật có folder riêng trong `training_data/`:

```
training_data/
├── gau_keo/
│   ├── personality_profile.json
│   ├── conversations.json
│   └── new_conversations_batch3.json
└── whitecat/
    ├── personality_profile.json
    ├── conversations.json
    └── new_conversations_batch3.json
```

Đổi nhân vật trong `.env`:
```env
CHARACTER=whitecat
```

## Setup Discord Bot

1. Vào https://discord.com/developers/applications
2. **New Application** -> Đặt tên
3. **Bot** -> **Reset Token** -> Copy
4. Paste vào `.env`: `DISCORD_TOKEN=...`
5. **Bot** settings -> Bật **Message Content Intent**
6. **OAuth2** -> **URL Generator**:
   - Scopes: `bot`
   - Permissions: Send Messages, Read Message History
7. Copy URL -> Mở trong browser -> Chọn server

## Bot Commands

| Command | Mô tả |
|---------|-------|
| `!clear` | Xóa conversation history |
| `!info` | Xem bot nhớ gì về bạn |
| `!remember key value` | Bảo bot nhớ thông tin |
| `!forget` | Bot quên hết về bạn |

## Tính năng

- **Nhận diện người dùng**: Bot biết ai đang nói chuyện qua username
- **Gộp tin nhắn**: AI tự quyết định gộp tin nhắn liên tiếp hay trả lời riêng
- **Memory**: Bot nhớ thông tin về người dùng qua sessions
- **Multi-character**: Hỗ trợ nhiều nhân vật với personality khác nhau

## Cấu trúc

```
Botchatlocal/
├── train.py             # Train model + quản lý jobs
├── bot.py               # Discord bot + test
├── .env                 # API keys (tự tạo)
├── .env.example         # Template
├── openai_model_id.txt  # Model ID sau khi train
├── openai_job_id.txt    # Job ID gần nhất
├── user_memories.json   # Bot memories
└── training_data/
    ├── gau_keo/
    │   ├── personality_profile.json
    │   ├── conversations.json
    │   └── new_conversations_batch3.json
    └── whitecat/
        ├── personality_profile.json
        ├── conversations.json
        └── new_conversations_batch3.json
```

## Quick Start

```bash
# 1. Cài đặt
pip install openai discord.py python-dotenv
cp .env.example .env
# Chỉnh sửa .env: thêm API keys

# 2. Train
python train.py

# 3. Test
python bot.py --test

# 4. Chạy Discord bot
python bot.py
```

## Tạo nhân vật mới

1. Tạo folder trong `training_data/`:
```bash
mkdir training_data/ten_nhan_vat
```

2. Tạo `personality_profile.json` với thông tin nhân vật

3. Tạo `conversations.json` với các cuộc hội thoại mẫu

4. Đổi `CHARACTER=ten_nhan_vat` trong `.env`

5. Chạy `python train.py`
