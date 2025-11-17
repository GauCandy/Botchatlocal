# 🤖 AI Training Data Generator

Công cụ sinh dữ liệu training chất lượng cao cho AI Chatbot sử dụng OpenAI GPT hoặc Anthropic Claude.

## ✨ Tính năng

- 🎯 **Tự động sinh dữ liệu**: Tạo hàng trăm cuộc hội thoại chất lượng cao tự động
- 🌐 **Đa ngôn ngữ**: Hỗ trợ Tiếng Việt và nhiều ngôn ngữ khác
- 🔌 **Nhiều API**: Hỗ trợ OpenAI, Anthropic Claude
- 📊 **Nhiều format**: JSON, JSONL, CSV, OpenAI fine-tuning format
- ⚡ **Xử lý song song**: Batch processing để tăng tốc độ
- 🎨 **Tùy biến cao**: Dễ dàng thêm scenarios và cấu hình
- 📈 **Quality control**: Lọc và kiểm tra chất lượng dữ liệu
- 🐍 **Python & Node.js**: Cả hai phiên bản đều có sẵn

## 🚀 Bắt đầu nhanh

### Cài đặt Python Version

```bash
# Clone hoặc download repository này
cd Botchatlocal

# Cài đặt dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-openai-api-key-here'
# hoặc
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'

# Chạy generator cơ bản
python training_data_generator.py

# Hoặc chạy advanced version với nhiều tính năng
python advanced_generator.py
```

### Cài đặt Node.js Version

```bash
# Cài đặt dependencies
npm install

# Set API key
export OPENAI_API_KEY='your-openai-api-key-here'
# hoặc
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'

# Chạy generator
npm start
# hoặc
node generator.js
```

## 📖 Hướng dẫn chi tiết

### 1. Lấy API Key

#### OpenAI (Khuyến nghị cho người mới)
1. Truy cập: https://platform.openai.com/api-keys
2. Đăng ký/đăng nhập tài khoản
3. Tạo API key mới
4. Copy và lưu lại key (chỉ hiện 1 lần)
5. Nạp tiền vào tài khoản (tối thiểu $5)

**Chi phí**:
- `gpt-4o-mini`: ~$0.15/1000 conversations (RẺ NHẤT)
- `gpt-4o`: ~$2.50/1000 conversations

#### Anthropic Claude
1. Truy cập: https://console.anthropic.com/
2. Đăng ký tài khoản
3. Lấy API key
4. Nạp credits

**Chi phí**:
- `claude-3-5-haiku`: ~$0.25/1000 conversations (RẺ)
- `claude-3-5-sonnet`: ~$3.00/1000 conversations

### 2. Cấu hình

Chỉnh sửa file `config.py` để tùy chỉnh:

```python
# Chọn API
API_TYPE = "openai"  # hoặc "anthropic"

# Chọn model
MODEL_NAME = "gpt-4o-mini"  # Rẻ nhất, chất lượng tốt

# Số conversations muốn sinh
NUM_CONVERSATIONS = 50

# Batch size (số requests đồng thời)
BATCH_SIZE = 5

# Temperature (0-1, cao hơn = sáng tạo hơn)
TEMPERATURE = 0.8
```

### 3. Chạy Generator

#### Python - Basic Version

```bash
python training_data_generator.py
```

Tính năng:
- Sinh 30 conversations mặc định
- Xuất ra JSON, JSONL, CSV, OpenAI format
- Hiển thị thống kê cơ bản

#### Python - Advanced Version (KHUYẾN NGHỊ)

```bash
python advanced_generator.py
```

Tính năng:
- Quality filtering
- Progress bar
- Retry logic khi gặp lỗi
- Detailed statistics
- Logging
- Tuỳ biến cao qua config.py

#### Node.js Version

```bash
node generator.js
```

### 4. Kết quả

Sau khi chạy, dữ liệu được lưu trong thư mục `training_data/`:

```
training_data/
├── conversations_20241117.json       # JSON format
├── conversations_20241117.jsonl      # JSONL format (mỗi dòng 1 object)
├── conversations_20241117.csv        # CSV format
└── openai_format_20241117.jsonl      # OpenAI fine-tuning format
```

## 📊 Định dạng dữ liệu

### JSON Format

```json
[
  {
    "id": "conv_20241117_120530_1234",
    "timestamp": "2024-11-17T12:05:30.123Z",
    "scenario": {
      "topic": "Lập trình Python cơ bản",
      "context": "Người dùng muốn học Python",
      "goal": "Giải thích cách bắt đầu học Python",
      "turns": 6
    },
    "conversation": [
      {
        "role": "user",
        "content": "Tôi muốn học lập trình Python nhưng chưa biết bắt đầu từ đâu. Bạn có thể hướng dẫn được không?"
      },
      {
        "role": "assistant",
        "content": "Chào bạn! Tuyệt vời khi bạn muốn học Python. Đây là ngôn ngữ rất phù hợp cho người mới bắt đầu. Để bắt đầu, bạn cần..."
      }
    ],
    "metadata": {
      "topic": "Lập trình Python cơ bản",
      "difficulty": "easy",
      "language": "vi"
    },
    "source": "openai_gpt-4o-mini"
  }
]
```

### OpenAI Fine-tuning Format

```jsonl
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Dùng format này để fine-tune model OpenAI: https://platform.openai.com/docs/guides/fine-tuning

## 🎨 Tùy chỉnh Scenarios

### Thêm scenarios của riêng bạn

Chỉnh sửa `config.py`:

```python
CUSTOM_SCENARIOS = [
    {
        "topic": "Chủ đề của bạn",
        "context": "Ngữ cảnh cuộc hội thoại",
        "goal": "Mục tiêu của conversation",
        "turns": 6  # Số lượt hội thoại
    },
    {
        "topic": "Tư vấn mua laptop",
        "context": "Sinh viên cần mua laptop học tập",
        "goal": "Tư vấn laptop phù hợp với budget và nhu cầu",
        "turns": 8
    },
    # Thêm nhiều scenarios khác...
]
```

### Chọn categories

```python
ENABLED_CATEGORIES = {
    "technology": True,      # Công nghệ
    "lifestyle": True,       # Đời sống
    "education": True,       # Giáo dục
    "business": False,       # Tắt category này
    "entertainment": True,   # Giải trí
}
```

## 🛠️ Sử dụng nâng cao

### 1. Tạo dữ liệu lớn

```bash
# Sinh 500 conversations
python advanced_generator.py
```

Chỉnh trong `config.py`:
```python
NUM_CONVERSATIONS = 500
BATCH_SIZE = 10  # Tăng nếu API cho phép
```

### 2. Tạo dữ liệu chất lượng cao

```python
# Trong config.py
TEMPERATURE = 0.7  # Giảm để output ổn định hơn
ENABLE_QUALITY_FILTER = True
MIN_RESPONSE_LENGTH = 50  # Tăng độ dài tối thiểu
```

### 3. Dùng model tốt hơn

```python
# OpenAI
MODEL_NAME = "gpt-4o"  # Chất lượng cao hơn nhưng đắt hơn

# Anthropic
MODEL_NAME = "claude-3-5-sonnet-20241022"  # Chất lượng cao nhất
```

### 4. Xử lý lỗi và retry

Generator tự động retry khi gặp lỗi:
- Rate limit errors
- Timeout errors
- API errors

Logs được lưu trong `training_generation.log`

## 💡 Use Cases

### 1. Fine-tune OpenAI model

```bash
# Sinh dữ liệu
python advanced_generator.py

# Upload và fine-tune
openai api fine_tunes.create \
  -t "training_data/openai_format_20241117.jsonl" \
  -m gpt-3.5-turbo
```

### 2. Train custom chatbot

```python
import json

# Đọc dữ liệu
with open('training_data/conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Dùng cho training model của bạn
for conv in data:
    messages = conv['conversation']
    # Train your model...
```

### 3. Tạo dataset cho RAG

```python
# Dùng conversations làm knowledge base cho RAG system
# Vector embedding + similarity search
```

### 4. Testing chatbot

```python
# Dùng conversations để test chatbot của bạn
# So sánh output với expected responses
```

## 📈 Tips để có dữ liệu tốt

1. **Đa dạng scenarios**: Càng nhiều scenarios khác nhau càng tốt
2. **Tăng turns**: Conversations dài hơn = ngữ cảnh phong phú hơn
3. **Quality over quantity**: 100 conversations chất lượng > 1000 conversations kém
4. **Review manually**: Xem qua 1 số conversations để đảm bảo chất lượng
5. **Iterative approach**: Sinh ít trước, xem kết quả, điều chỉnh, sinh nhiều hơn
6. **Mix topics**: Đừng tập trung 1 chủ đề duy nhất
7. **Realistic scenarios**: Scenarios càng gần với use case thực tế càng tốt

## 🐛 Troubleshooting

### Lỗi: "No API key found"

```bash
# Đảm bảo đã set environment variable
export OPENAI_API_KEY='sk-...'

# Hoặc sửa trực tiếp trong config.py
OPENAI_API_KEY = 'sk-...'
```

### Lỗi: Rate limit exceeded

```python
# Trong config.py
BATCH_SIZE = 3  # Giảm batch size
BATCH_DELAY = 2  # Tăng delay giữa batches
```

### Lỗi: Timeout

```python
# Trong config.py
REQUEST_TIMEOUT = 120  # Tăng timeout lên 120s
```

### Chất lượng kém

```python
# Tăng temperature
TEMPERATURE = 0.9

# Sử dụng model tốt hơn
MODEL_NAME = "gpt-4o"

# Tăng số turns
DEFAULT_TURNS = 8
```

### Conversations bị lọc nhiều

```python
# Nới lỏng quality filter
MIN_RESPONSE_LENGTH = 20
ENABLE_QUALITY_FILTER = False  # Hoặc tắt hẳn
```

## 📚 Tài nguyên tham khảo

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [OpenAI Fine-tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Best practices for training data](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Thêm scenarios mới
- Cải thiện prompt templates
- Thêm API providers khác
- Fix bugs
- Improve documentation

## 📝 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.

## ⚠️ Lưu ý

- **Chi phí**: Sử dụng API có tính phí. Hãy theo dõi usage và set budget limits.
- **API Keys**: Giữ API keys bí mật, không commit vào git
- **Rate Limits**: Mỗi API có rate limits khác nhau
- **Quality**: AI-generated data cần được review trước khi dùng production
- **Privacy**: Không dùng dữ liệu nhạy cảm trong scenarios

## 🎯 Roadmap

- [ ] Thêm support cho Gemini API
- [ ] Web UI để quản lý scenarios
- [ ] Auto-evaluation của conversations
- [ ] Multi-language support nâng cao
- [ ] Integration với vector databases
- [ ] Docker container
- [ ] CLI tool với arguments

## 💬 Hỗ trợ

Nếu có vấn đề hoặc câu hỏi:
1. Đọc phần Troubleshooting
2. Check logs trong `training_generation.log`
3. Tạo issue trên GitHub

---

**Happy training! 🚀**

Tạo bởi AI Training Data Generator - Powered by OpenAI & Anthropic
