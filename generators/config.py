"""
File cấu hình cho Training Data Generator
Điều chỉnh các settings này theo nhu cầu của bạn
"""

# ============================================
# API CONFIGURATION
# ============================================

# Chọn API provider: "openai", "anthropic", "gemini"
API_TYPE = "openai"

# Model name (để trống sẽ dùng model mặc định)
# OpenAI: "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"
# Anthropic: "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"
MODEL_NAME = "gpt-4o-mini"

# API Keys (hoặc set qua environment variables)
OPENAI_API_KEY = None  # Hoặc set: export OPENAI_API_KEY='your-key'
ANTHROPIC_API_KEY = None  # Hoặc set: export ANTHROPIC_API_KEY='your-key'

# ============================================
# GENERATION SETTINGS
# ============================================

# Số conversations muốn sinh ra
NUM_CONVERSATIONS = 30

# Số requests đồng thời (giảm nếu gặp rate limit)
BATCH_SIZE = 5

# Temperature cho AI (0.0-1.0, cao hơn = sáng tạo hơn)
TEMPERATURE = 0.8

# Số lượt hội thoại mặc định cho mỗi conversation
DEFAULT_TURNS = 6

# ============================================
# OUTPUT SETTINGS
# ============================================

# Thư mục lưu output
OUTPUT_DIR = "training_data"

# Formats muốn export (có thể chọn nhiều)
EXPORT_FORMATS = {
    "json": True,      # File JSON thông thường
    "jsonl": True,     # JSON Lines (mỗi dòng 1 conversation)
    "csv": True,       # CSV format
    "openai": True,    # OpenAI fine-tuning format
}

# ============================================
# CUSTOM SCENARIOS
# ============================================

# Thêm scenarios của riêng bạn tại đây
# Để trống [] sẽ dùng scenarios mặc định
CUSTOM_SCENARIOS = [
    # Ví dụ:
    # {
    #     "topic": "Chủ đề của bạn",
    #     "context": "Ngữ cảnh cuộc hội thoại",
    #     "goal": "Mục tiêu của conversation",
    #     "turns": 6
    # },
]

# ============================================
# ADVANCED SETTINGS
# ============================================

# Retry settings cho API calls
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Timeout cho mỗi API request
REQUEST_TIMEOUT = 60  # seconds

# Delay giữa các batches để tránh rate limit
BATCH_DELAY = 1  # seconds

# ============================================
# LANGUAGE SETTINGS
# ============================================

# Ngôn ngữ chính của dữ liệu
PRIMARY_LANGUAGE = "vi"  # vi = Tiếng Việt, en = English

# Có thêm dữ liệu song ngữ không?
INCLUDE_BILINGUAL = False

# ============================================
# QUALITY CONTROL
# ============================================

# Độ dài tối thiểu của mỗi response (characters)
MIN_RESPONSE_LENGTH = 20

# Độ dài tối đa của mỗi response (characters)
MAX_RESPONSE_LENGTH = 2000

# Lọc conversations không đạt chất lượng
ENABLE_QUALITY_FILTER = True

# ============================================
# SCENARIO CATEGORIES
# ============================================

# Chọn categories muốn sinh dữ liệu
# Set False cho categories không muốn
ENABLED_CATEGORIES = {
    "technology": True,      # Công nghệ, lập trình
    "lifestyle": True,       # Đời sống, gia đình
    "education": True,       # Giáo dục, học tập
    "business": True,        # Kinh doanh, khởi nghiệp
    "entertainment": True,   # Giải trí, sở thích
    "health": True,          # Sức khỏe, y tế
    "finance": True,         # Tài chính, đầu tư
    "travel": True,          # Du lịch
    "food": True,            # Ẩm thực
    "sports": True,          # Thể thao
}

# ============================================
# LOGGING
# ============================================

# Hiển thị detailed logs
VERBOSE = True

# Lưu logs ra file
SAVE_LOGS = True
LOG_FILE = "training_generation.log"
