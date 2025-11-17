# 🤖 AI Training Data Generator - Tối Ưu

Công cụ sinh dữ liệu training cho AI Chatbot **SIÊU ĐƠN GIẢN** - chỉ 1 file Python!

## 🚀 Bắt đầu ngay (3 bước)

### Bước 1: Cài đặt

```bash
pip install aiohttp openai anthropic
```

### Bước 2: Lấy API Key

**OpenAI** (Khuyến nghị - Rẻ nhất):
- Vào https://platform.openai.com/api-keys
- Tạo key mới
- Nạp $5 (đủ tạo hàng nghìn conversations)

**Chi phí**: ~$0.15/1000 conversations với `gpt-4o-mini`

### Bước 3: Chạy

```bash
# Set API key
export OPENAI_API_KEY='sk-your-key-here'

# Chạy
python generate.py
```

**Xong!** Dữ liệu sẽ được lưu trong thư mục `training_data/`

## ⚙️ Tùy chỉnh

Mở file `generate.py` và sửa phần đầu:

```python
# Số conversations muốn tạo
NUM_CONVERSATIONS = 50  # Tăng lên 100, 500, 1000...

# Model (rẻ hơn = nhanh hơn, đắt hơn = tốt hơn)
MODEL = "gpt-4o-mini"  # Hoặc "gpt-4o" (tốt hơn nhưng đắt gấp 15x)

# Số requests đồng thời (tăng = nhanh hơn)
BATCH_SIZE = 5  # Tăng lên 10 nếu muốn nhanh

# Độ sáng tạo (0-1)
TEMPERATURE = 0.8  # Giảm xuống 0.6 nếu muốn ổn định hơn
```

## 📊 Kết quả

Sau khi chạy xong, bạn có 4 files:

```
training_data/
├── conversations_20241117.json       ← Đọc được dễ nhất
├── conversations_20241117.jsonl      ← Dùng để training
├── conversations_20241117.csv        ← Mở bằng Excel
└── openai_20241117.jsonl             ← Dùng để fine-tune OpenAI
```

## 🎨 Thêm chủ đề của bạn

Trong file `generate.py`, thêm vào list `SCENARIOS`:

```python
SCENARIOS = [
    # ... scenarios có sẵn ...

    # Thêm của bạn:
    {
        "topic": "Tư vấn mua xe máy",
        "context": "Người dùng muốn mua xe",
        "goal": "Tư vấn xe phù hợp với budget",
        "turns": 6
    },

    {
        "topic": "Học guitar fingerstyle",
        "context": "Người mới học guitar",
        "goal": "Hướng dẫn kỹ thuật fingerstyle",
        "turns": 7
    },
]
```

Đã có sẵn **50+ scenarios** đa dạng trong file!

## 📈 Ví dụ dữ liệu sinh ra

```json
{
  "id": "conv_20241117_123045_5678",
  "conversation": [
    {
      "role": "user",
      "content": "Tôi muốn học Python nhưng chưa biết bắt đầu từ đâu..."
    },
    {
      "role": "assistant",
      "content": "Chào bạn! Python là lựa chọn tuyệt vời cho người mới. Để bắt đầu, bạn cần..."
    },
    ...
  ],
  "scenario": {
    "topic": "Lập trình Python cơ bản"
  }
}
```

## 💡 Tips

### Tạo nhiều dữ liệu nhanh

```python
NUM_CONVERSATIONS = 500  # Tạo 500 conversations
BATCH_SIZE = 10          # Chạy 10 requests cùng lúc
```

### Chất lượng cao hơn

```python
MODEL = "gpt-4o"         # Dùng model tốt nhất (đắt hơn)
TEMPERATURE = 0.7        # Giảm độ random
DEFAULT_TURNS = 8        # Conversations dài hơn
```

### Tiết kiệm chi phí

```python
MODEL = "gpt-4o-mini"    # Model rẻ nhất
NUM_CONVERSATIONS = 30   # Tạo ít trước, test kết quả
```

## 🐛 Gặp lỗi?

**"No API key found"**
```bash
export OPENAI_API_KEY='sk-...'
```

**"Rate limit exceeded"** - API quá tải
```python
BATCH_SIZE = 3  # Giảm xuống
```

**Chất lượng kém** - Conversations không tốt
```python
MODEL = "gpt-4o"        # Dùng model tốt hơn
TEMPERATURE = 0.7       # Giảm temperature
```

## 📚 Dùng dữ liệu để làm gì?

1. **Fine-tune OpenAI model**
   ```bash
   openai api fine_tunes.create -t "training_data/openai_*.jsonl" -m gpt-3.5-turbo
   ```

2. **Train chatbot riêng** - Dùng với Rasa, Dialogflow, custom models

3. **RAG system** - Knowledge base cho vector search

4. **Testing** - Test chatbot của bạn với real conversations

## 🎯 Bảng giá ước tính

| Model | Giá/1000 convs | Chất lượng | Tốc độ |
|-------|----------------|-----------|---------|
| gpt-4o-mini | $0.15 | ⭐⭐⭐ | ⚡⚡⚡ |
| gpt-4o | $2.50 | ⭐⭐⭐⭐⭐ | ⚡⚡ |
| claude-haiku | $0.25 | ⭐⭐⭐⭐ | ⚡⚡⚡ |
| claude-sonnet | $3.00 | ⭐⭐⭐⭐⭐ | ⚡ |

**Khuyến nghị**: Bắt đầu với `gpt-4o-mini` - rẻ và chất lượng tốt!

## ✨ Tính năng

✅ Tự động sinh conversations tự nhiên
✅ 50+ scenarios đa dạng có sẵn
✅ Xử lý song song (nhanh!)
✅ Retry tự động khi lỗi
✅ Quality filtering
✅ Progress tracking real-time
✅ Export 4 formats
✅ 100% tiếng Việt
✅ Chỉ 1 file Python đơn giản

## 📞 Hỗ trợ

Nếu cần giúp:
1. Đọc lại README này
2. Check logs khi chạy
3. Giảm `NUM_CONVERSATIONS` để test
4. Thử với API key mới

---

**Chúc bạn tạo dữ liệu thành công! 🚀**

Chi phí thấp • Chất lượng cao • Siêu đơn giản
