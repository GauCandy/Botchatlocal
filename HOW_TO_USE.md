# Hướng dẫn sử dụng Gấu Kẹo AI Training

## 🎯 TL;DR - Quick Start

```bash
# Có GPU? Train local miễn phí
python train_local_gpu.py

# Không GPU? Train với OpenAI (~$5)
export OPENAI_API_KEY='sk-...'
python train_openai.py

# Test xem model có giống Gấu Kẹo không
python test_personality.py --local
# hoặc
python test_personality.py --openai
```

## 📁 3 Files chính để TRAIN AI

### 1. **train_local_gpu.py** 🔥
- Train model local với GPU của bạn
- Miễn phí, nhưng cần GPU NVIDIA
- Dùng Unsloth + LoRA để train nhanh
- Output: Model được save vào `models/gau_keo_local/`

### 2. **train_openai.py** ☁️
- Train model trên cloud với OpenAI
- Có phí (~$3-5 cho 1 lần)
- Dễ dùng, không cần GPU
- Output: Fine-tuned model ID

### 3. **test_personality.py** 🧪
- Test model đã train
- Chạy scenarios tự động
- Interactive chat để verify personality
- Support cả local và OpenAI models

## 📊 Training Data (Đã có sẵn)

### **training_data/gau_keo/personality_profile.json**
- Định nghĩa personality của Gấu Kẹo
- Speaking style, emojis, traits
- Được load tự động bởi training scripts

### **training_data/gau_keo/conversations.json**
- 22 cuộc hội thoại mẫu
- Cover nhiều topics: tech, emotional support, casual chat
- Được dùng để fine-tune model

**⚠️ Không cần chỉnh gì cả!** Training scripts tự động đọc 2 files này.

## 📁 Folder `generators/` (Optional)

Folder này chứa các scripts để **tạo thêm** training data:
- `generate_gaukeo_data.py` - Generate training JSON từ code
- `training_data_generator.py` - Generator chung
- Các tools khác...

**Bạn có thể:**
- ✅ Bỏ qua folder này nếu training data hiện tại đã đủ
- ✅ Xóa folder này nếu không dùng
- ✅ Dùng nếu muốn tạo thêm conversations

## 🚀 Chi tiết cách train

### Option 1: Train Local (FREE)

**Yêu cầu:**
- GPU NVIDIA (8GB+ VRAM)
- hoặc Google Colab (T4 GPU miễn phí)

**Steps:**
```bash
# 1. Cài dependencies
pip install unsloth transformers datasets bitsandbytes accelerate

# 2. Train (30-60 phút)
python train_local_gpu.py

# 3. Test
python test_personality.py --local
```

**Output:**
- Model saved tại: `models/gau_keo_local/`
- Có thể dùng với transformers library

### Option 2: Train với OpenAI ($)

**Yêu cầu:**
- OpenAI API key
- ~$3-5 credits

**Steps:**
```bash
# 1. Set API key
export OPENAI_API_KEY='sk-proj-...'

# 2. Train (10-30 phút, chờ OpenAI xử lý)
python train_openai.py

# 3. Script sẽ print ra model ID
# Model ID được save vào: models/gau_keo_openai_model_id.txt

# 4. Test
python test_personality.py --openai
```

**Output:**
- Fine-tuned model ID: `ft:gpt-4o-mini:...`
- Dùng với OpenAI API

### Option 3: Không train (Prompt Engineering)

Nếu không muốn train, test trực tiếp với prompts:

```bash
python test_personality.py --openai --prompt-only
```

Model sẽ nhận personality từ system prompt thay vì fine-tuning.

## 🧪 Testing

### Test tự động với scenarios:

```bash
# Test local model
python test_personality.py --local

# Test OpenAI model
python test_personality.py --openai
```

Chạy 5 test scenarios:
- Debug Python code
- Emotional support
- Tech recommendations
- Casual chat
- Work stress

### Interactive chat:

```bash
python test_personality.py --local --interactive
# hoặc
python test_personality.py --openai --interactive
```

Chat trực tiếp với model để verify personality.

## 💰 Chi phí

### Local GPU Training
- **FREE** nếu có GPU
- Google Colab T4: **FREE** (limited hours)
- Google Colab A100: ~$10/month

### OpenAI Training
- Fine-tune: ~$3-5 (one-time)
- Usage: ~$0.30-2.40/1M tokens
- Testing: < $1

## 🔒 Privacy & Security

✅ **Đã xóa:**
- Thông tin về relationship
- Gender details
- Sexual orientation
- Personal identifying info

✅ **Giữ lại:**
- Personality traits
- Speaking style (Vietnamese Gen Z)
- Technical interests
- Communication patterns

## ❓ FAQ

**Q: Có cần chỉnh training data không?**
A: Không! Data đã ready to use. Chỉ chạy training script.

**Q: Train mất bao lâu?**
A: Local GPU: 30-60 phút. OpenAI: 10-30 phút (auto).

**Q: Cần bao nhiêu data để train tốt?**
A: Hiện có 22 conversations. Lý tưởng: 50-100+ conversations.

**Q: Làm sao thêm training data?**
A: Chỉnh `training_data/gau_keo/conversations.json` và thêm conversations mới.

**Q: Model có hoạt động offline không?**
A: Local model (train_local_gpu.py): YES. OpenAI model: NO (cần API).

**Q: Xóa được file nào?**
A: Folder `generators/` có thể xóa nếu không cần generate thêm data.

## 📚 More Info

- [README.md](README.md) - Chi tiết đầy đủ
- [PERSONALITY_GUIDE.md](PERSONALITY_GUIDE.md) - About Gấu Kẹo personality
- [generators/README.md](generators/README.md) - About data generators

---

**Happy training! 🐧**
