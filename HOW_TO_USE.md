# Hướng dẫn sử dụng Gấu Kẹo Training Data

## 📁 File nào để TRAIN AI?

### **Chỉ cần 2 files này:**

1. **`training_data/gau_keo/personality_profile.json`**
   - Mô tả tính cách của Gấu Kẹo
   - Cách nói chuyện, emojis, style
   - Sử dụng file này để AI hiểu personality

2. **`training_data/gau_keo/conversations.json`**
   - Các cuộc hội thoại mẫu
   - Nhiều tình huống khác nhau
   - Sử dụng file này để fine-tune AI

## 🚫 File Python (KHÔNG cần thiết cho training)

Các file `.py` chỉ để **tạo thêm data**, không dùng để train:
- `generate_gaukeo_data.py` - Tạo file JSON từ code
- `training_data_generator.py` - Generator chung
- `advanced_generator.py` - Generator nâng cao
- `generate_with_claude.py` - Generate bằng Claude API
- `generate.py`, `quickstart.py`, `analyze_data.py` - Các tools khác

**➡️ Bạn có thể XÓA HẾT các file `.py` này nếu không dùng!**

## ✅ Để train AI:

1. Lấy 2 files JSON trong `training_data/gau_keo/`
2. Upload lên nền tảng fine-tuning (OpenAI, Claude, v.v.)
3. Hoặc sử dụng với prompt engineering

## 🔒 Privacy

- Đã xóa thông tin về bạn gái
- Giới tính và orientation được đánh dấu `[bí mật]`
- Chỉ giữ lại personality và communication style
