# 🐧 Gấu Kẹo AI - Training Your Own Personality

Train AI model với personality Gấu Kẹo sử dụng dữ liệu training có sẵn.

## 🎯 Mục đích

Repository này giúp bạn:
- ✅ Train AI model local với GPU (Unsloth + LoRA)
- ✅ Train AI model trên cloud với OpenAI API
- ✅ Test personality đã train xem có giống Gấu Kẹo không

## 🚀 Bắt đầu nhanh

### Tổng quan file structure

```
Botchatlocal/
├── train_local_gpu.py          # 🔥 Train với GPU local
├── train_openai.py             # ☁️  Train với OpenAI API
├── test_personality.py         # 🧪 Test model đã train
├── training_data/
│   └── gau_keo/
│       ├── personality_profile.json    # Personality definition
│       └── conversations.json          # Training conversations (22 examples)
└── generators/                 # 📁 Helper scripts (optional)
```

### 3 cách để train AI:

#### 1️⃣  Train Local với GPU (FREE, cần GPU)

```bash
# Cài đặt dependencies
pip install unsloth transformers datasets bitsandbytes accelerate

# Train (mất ~30-60 phút với GPU)
python train_local_gpu.py

# Test personality
python test_personality.py --local
```

**Yêu cầu:**
- GPU NVIDIA với ít nhất 8GB VRAM (RTX 3060/4060 trở lên)
- Nếu không có GPU, dùng Google Colab với T4 GPU miễn phí

#### 2️⃣  Train với OpenAI API (Có phí, dễ nhất)

```bash
# Set API key
export OPENAI_API_KEY='sk-...'

# Hoặc tạo file .env
echo "OPENAI_API_KEY=sk-..." > .env

# Train (chờ OpenAI xử lý, ~10-30 phút)
python train_openai.py

# Test personality
python test_personality.py --openai
```

**Chi phí:** ~$3-5 cho 1 lần fine-tune GPT-4o-mini với 22 conversations

#### 3️⃣  Không train, chỉ test với personality prompts

Nếu không muốn train model, có thể dùng prompt engineering:

```bash
python test_personality.py --openai --prompt-only
```

## 📊 Training Data

### personality_profile.json
Định nghĩa tính cách của Gấu Kẹo:
- Vietnamese Gen Z tech enthusiast
- Personality traits, speaking style, interests
- Emotional patterns, values

### conversations.json
22 cuộc hội thoại mẫu showing Gấu Kẹo's personality:
- Technical help (debugging, coding)
- Emotional support (tâm sự, stress)
- Casual chat (random topics)
- Work/study discussions

## 🧪 Testing

### Test với scenarios có sẵn:

```bash
python test_personality.py --local
# hoặc
python test_personality.py --openai
```

### Interactive chat:

```bash
python test_personality.py --local --interactive
```

Chat với model để xem personality có giống Gấu Kẹo không.

## ⚙️  Advanced: Customize Training

### Train với model khác (Local GPU)

Mở `train_local_gpu.py`, sửa dòng:

```python
model_name = "unsloth/Qwen2.5-1.5B-bnb-4bit"  # Model nhẹ
# Đổi thành:
model_name = "unsloth/Qwen2.5-7B-bnb-4bit"    # Model mạnh hơn
```

### Train với model khác (OpenAI)

Mở `train_openai.py`, sửa:

```python
model = "gpt-4o-mini-2024-07-18"  # Rẻ nhất
# Đổi thành:
model = "gpt-4o-2024-08-06"       # Chất lượng cao hơn
```

### Thêm training data

Chỉnh `training_data/gau_keo/conversations.json`, thêm conversations mới:

```json
{
  "id": "gaukeo_023",
  "scenario": {
    "topic": "Topic của bạn",
    "category": "technical|emotional|casual",
    "mood": "focused|vulnerable|excited"
  },
  "conversation": [
    {"role": "user", "content": "User message"},
    {"role": "assistant", "content": "Gấu Kẹo response"}
  ]
}
```

## 📁 Folder `generators/` - Optional

Folder này chứa các scripts để **tạo thêm** training data. Không cần thiết để train AI.

- Nếu chỉ muốn train với data có sẵn → bỏ qua folder này
- Nếu muốn generate thêm conversations → xem `generators/README.md`

**Có thể xoá folder này** nếu không cần.

## 💰 Chi phí

### Local GPU Training
- **FREE** nếu có GPU
- Google Colab T4 GPU: FREE (giới hạn giờ sử dụng)
- Google Colab A100: ~$10/tháng

### OpenAI API Training
- Fine-tune GPT-4o-mini: ~$3-5 cho 22 conversations
- Sử dụng model: ~$0.30-$0.60/1M tokens input + ~$1.20-$2.40/1M tokens output
- Test conversations: vài cent

## 🛠️  Troubleshooting

### Lỗi: GPU out of memory

```python
# Trong train_local_gpu.py, giảm batch size:
per_device_train_batch_size=1  # giảm từ 2 xuống 1
```

### Lỗi: OpenAI API key không hợp lệ

```bash
# Check API key
echo $OPENAI_API_KEY

# Set lại
export OPENAI_API_KEY='sk-...'
```

### Fine-tuning job failed

```bash
# Check job status
python train_openai.py --check-status
```

### Model không giống personality

1. **Thêm training data:** Cần ít nhất 50-100 conversations để model học tốt
2. **Tăng epochs:** Sửa trong script từ 3 lên 5-10 epochs
3. **Dùng model lớn hơn:** GPT-4o thay vì 4o-mini

## 📚 Tài liệu thêm

- [HOW_TO_USE.md](HOW_TO_USE.md) - Hướng dẫn đơn giản
- [PERSONALITY_GUIDE.md](PERSONALITY_GUIDE.md) - Chi tiết về Gấu Kẹo personality
- [OpenAI Fine-tuning Docs](https://platform.openai.com/docs/guides/fine-tuning)
- [Unsloth Documentation](https://github.com/unslothai/unsloth)

## ⚠️  Lưu ý

- **Chi phí:** OpenAI API có phí. Set budget limits trên platform.
- **API Keys:** Đừng commit API keys vào git. Dùng `.env` file (đã có trong `.gitignore`)
- **Privacy:** Training data không chứa thông tin nhạy cảm
- **GPU:** Local training cần GPU NVIDIA. Không chạy được trên CPU/Mac M-series.

## 🎯 Quick Start Summary

**Không có GPU?** → Dùng `train_openai.py` (có phí ~$5)
**Có GPU?** → Dùng `train_local_gpu.py` (miễn phí)
**Không muốn train?** → Dùng prompt engineering với `test_personality.py --prompt-only`

---

**Happy training! 🐧**

Train bởi dữ liệu từ Gấu Kẹo personality - Vietnamese Gen Z tech enthusiast
