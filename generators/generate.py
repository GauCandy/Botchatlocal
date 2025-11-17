#!/usr/bin/env python3
"""
🤖 AI TRAINING DATA GENERATOR - PHIÊN BẢN TỐI ƯU
Sinh dữ liệu training chất lượng cao cho AI Chatbot

Sử dụng đơn giản:
    python generate.py

Tính năng:
- Tự động sinh hàng trăm conversations chất lượng cao
- Hỗ trợ OpenAI & Anthropic
- Xử lý song song, retry tự động
- Quality filtering
- Export nhiều formats
- Progress tracking
"""

import json
import csv
import asyncio
import aiohttp
import random
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from collections import Counter

# ============================================================================
# CẤU HÌNH - Chỉnh ở đây
# ============================================================================

# API Settings
API_TYPE = "openai"  # "openai" hoặc "anthropic"
MODEL = "gpt-4o-mini"  # gpt-4o-mini (rẻ) | gpt-4o (tốt) | claude-3-5-haiku-20241022

# Generation Settings
NUM_CONVERSATIONS = 50  # Số conversations muốn sinh
BATCH_SIZE = 5  # Số requests đồng thời (giảm nếu gặp rate limit)
TEMPERATURE = 0.8  # 0.0-1.0 (cao hơn = đa dạng hơn)
DEFAULT_TURNS = 6  # Số lượt hội thoại mặc định

# Quality Control
MIN_RESPONSE_LENGTH = 20
MAX_RESPONSE_LENGTH = 2000
ENABLE_QUALITY_FILTER = True

# Output
OUTPUT_DIR = "training_data"

# ============================================================================
# SCENARIOS - Thêm của bạn vào đây
# ============================================================================

SCENARIOS = [
    # Công nghệ & Lập trình
    {"topic": "Lập trình Python cơ bản", "context": "Người dùng muốn học Python", "goal": "Hướng dẫn bắt đầu học Python", "turns": 6},
    {"topic": "Debug lỗi code", "context": "Developer gặp lỗi khi code", "goal": "Giúp tìm và sửa lỗi", "turns": 5},
    {"topic": "Machine Learning cơ bản", "context": "Người dùng muốn tìm hiểu AI/ML", "goal": "Giải thích ML đơn giản, dễ hiểu", "turns": 7},
    {"topic": "Web Development", "context": "Người dùng muốn tạo website", "goal": "Tư vấn công nghệ và roadmap", "turns": 6},
    {"topic": "Database và SQL", "context": "Developer cần thiết kế database", "goal": "Hướng dẫn SQL và database design", "turns": 6},
    {"topic": "Git và Version Control", "context": "Người mới học git", "goal": "Giải thích git workflow", "turns": 5},
    {"topic": "API Development", "context": "Developer muốn tạo REST API", "goal": "Hướng dẫn thiết kế API", "turns": 7},
    {"topic": "Cloud Computing AWS", "context": "Developer muốn deploy lên cloud", "goal": "Giới thiệu AWS services", "turns": 6},
    {"topic": "Docker và Containers", "context": "DevOps engineer cần containerize app", "goal": "Hướng dẫn Docker cơ bản", "turns": 6},
    {"topic": "Bảo mật ứng dụng web", "context": "Developer quan tâm security", "goal": "Tư vấn best practices bảo mật", "turns": 7},

    # Đời sống & Kỹ năng
    {"topic": "Nấu ăn món Việt", "context": "Người dùng muốn nấu món truyền thống", "goal": "Hướng dẫn công thức chi tiết", "turns": 7},
    {"topic": "Tập thể dục tại nhà", "context": "Người dùng muốn tập không cần thiết bị", "goal": "Gợi ý bài tập hiệu quả", "turns": 6},
    {"topic": "Du lịch Việt Nam", "context": "Khách du lịch lên kế hoạch", "goal": "Tư vấn địa điểm và lịch trình", "turns": 8},
    {"topic": "Chăm sóc sức khỏe", "context": "Người dùng muốn sống khỏe mạnh", "goal": "Tư vấn thói quen tốt", "turns": 6},
    {"topic": "Quản lý tài chính cá nhân", "context": "Người dùng muốn tiết kiệm và đầu tư", "goal": "Hướng dẫn quản lý tiền bạc", "turns": 7},
    {"topic": "Học tiếng Anh hiệu quả", "context": "Người dùng muốn cải thiện English", "goal": "Tư vấn phương pháp học", "turns": 6},
    {"topic": "Kỹ năng giao tiếp", "context": "Người dùng muốn giao tiếp tốt hơn", "goal": "Tư vấn cải thiện soft skills", "turns": 6},
    {"topic": "Nuôi dạy con cái", "context": "Cha mẹ cần lời khuyên parenting", "goal": "Tư vấn nuôi dạy con", "turns": 7},
    {"topic": "Thiền và mindfulness", "context": "Người dùng muốn giảm stress", "goal": "Hướng dẫn thiền cơ bản", "turns": 5},
    {"topic": "Làm vườn ban công", "context": "Người dùng muốn trồng cây trong nhà", "goal": "Hướng dẫn chăm sóc cây", "turns": 6},

    # Giáo dục & Học tập
    {"topic": "Toán học phổ thông", "context": "Học sinh cần giải bài toán", "goal": "Giải thích cách làm bài", "turns": 5},
    {"topic": "Lịch sử Việt Nam", "context": "Học sinh tìm hiểu lịch sử", "goal": "Kể chuyện lịch sử hấp dẫn", "turns": 6},
    {"topic": "Vật lý cơ bản", "context": "Học sinh hiểu khái niệm vật lý", "goal": "Giải thích đơn giản, có ví dụ", "turns": 6},
    {"topic": "Hóa học hữu cơ", "context": "Học sinh học hóa học", "goal": "Giảng giải dễ hiểu", "turns": 5},
    {"topic": "Kỹ năng viết luận", "context": "Học sinh viết essay", "goal": "Hướng dẫn cấu trúc bài viết", "turns": 6},

    # Kinh doanh & Nghề nghiệp
    {"topic": "Khởi nghiệp startup", "context": "Entrepreneur muốn start business", "goal": "Tư vấn các bước khởi nghiệp", "turns": 8},
    {"topic": "Marketing số", "context": "Marketer làm digital marketing", "goal": "Tư vấn chiến lược marketing", "turns": 7},
    {"topic": "Quản lý dự án", "context": "PM quản lý project", "goal": "Tư vấn project management", "turns": 6},
    {"topic": "Phát triển sự nghiệp", "context": "Người đi làm muốn thăng tiến", "goal": "Tư vấn career development", "turns": 7},
    {"topic": "Bán hàng online", "context": "Người bán hàng trên mạng", "goal": "Hướng dẫn e-commerce", "turns": 7},
    {"topic": "Viết CV xin việc", "context": "Người tìm việc cần CV tốt", "goal": "Tư vấn viết CV hiệu quả", "turns": 6},
    {"topic": "Phỏng vấn xin việc", "context": "Ứng viên chuẩn bị interview", "goal": "Tips trả lời phỏng vấn", "turns": 6},
    {"topic": "Làm việc remote", "context": "Nhân viên làm việc từ xa", "goal": "Tư vấn work from home hiệu quả", "turns": 5},
    {"topic": "Quản lý thời gian", "context": "Người bận rộn cần quản lý time", "goal": "Hướng dẫn time management", "turns": 6},
    {"topic": "Xây dựng thương hiệu cá nhân", "context": "Người muốn build personal brand", "goal": "Tư vấn branding", "turns": 7},

    # Giải trí & Sở thích
    {"topic": "Nhiếp ảnh smartphone", "context": "Người dùng chụp ảnh bằng điện thoại", "goal": "Hướng dẫn kỹ thuật chụp ảnh", "turns": 6},
    {"topic": "Học đàn guitar", "context": "Người mới học nhạc cụ", "goal": "Hướng dẫn bắt đầu học guitar", "turns": 6},
    {"topic": "Vẽ tranh", "context": "Người học vẽ", "goal": "Hướng dẫn kỹ thuật vẽ cơ bản", "turns": 5},
    {"topic": "Chơi cờ vua", "context": "Người học chơi chess", "goal": "Dạy chiến thuật cờ vua", "turns": 6},
    {"topic": "Review phim hay", "context": "Người tìm phim để xem", "goal": "Gợi ý và review phim", "turns": 6},
    {"topic": "Đọc sách hiệu quả", "context": "Người muốn đọc nhiều sách hơn", "goal": "Tư vấn thói quen đọc sách", "turns": 5},

    # Sức khỏe & Thể thao
    {"topic": "Chạy bộ cho người mới", "context": "Người bắt đầu tập chạy", "goal": "Hướng dẫn chạy đúng cách", "turns": 6},
    {"topic": "Yoga tại nhà", "context": "Người tập yoga ở nhà", "goal": "Hướng dẫn các tư thế yoga", "turns": 6},
    {"topic": "Ăn kiêng giảm cân", "context": "Người muốn giảm cân lành mạnh", "goal": "Tư vấn chế độ ăn", "turns": 7},
    {"topic": "Tăng cơ bắp", "context": "Người tập gym muốn tăng cơ", "goal": "Hướng dẫn tập luyện và dinh dưỡng", "turns": 7},
    {"topic": "Chăm sóc da mặt", "context": "Người quan tâm skincare", "goal": "Tư vấn chăm sóc da", "turns": 6},

    # Công nghệ nâng cao
    {"topic": "AI và ChatGPT", "context": "Người muốn sử dụng AI tools", "goal": "Hướng dẫn dùng AI hiệu quả", "turns": 7},
    {"topic": "Blockchain và Crypto", "context": "Người tìm hiểu cryptocurrency", "goal": "Giải thích blockchain đơn giản", "turns": 6},
    {"topic": "IoT và Smart Home", "context": "Người muốn nhà thông minh", "goal": "Tư vấn thiết bị IoT", "turns": 6},
    {"topic": "Data Analytics", "context": "Analyst phân tích dữ liệu", "goal": "Hướng dẫn công cụ analytics", "turns": 7},
    {"topic": "Mobile App Design", "context": "Designer thiết kế app", "goal": "Tư vấn UI/UX design", "turns": 6},
]

# ============================================================================
# GENERATOR CLASS
# ============================================================================

class OptimizedGenerator:
    """Generator tối ưu với tất cả tính năng"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.api_type = API_TYPE.lower()
        self.model = MODEL
        self.data = []
        self.stats = {"success": 0, "failed": 0, "filtered": 0}

    def create_prompt(self, scenario: Dict) -> str:
        """Tạo prompt tối ưu"""
        return f"""Tạo cuộc hội thoại TỰ NHIÊN giữa User và AI Assistant:

CHỦ ĐỀ: {scenario['topic']}
NGỮ CẢNH: {scenario['context']}
MỤC TIÊU: {scenario['goal']}
SỐ LƯỢT: {scenario.get('turns', DEFAULT_TURNS)} turns

YÊU CẦU:
1. Hội thoại PHẢI tự nhiên như người thật
2. User: hỏi không rõ ràng, follow-up, thay đổi chủ đề nhẹ
3. AI: trả lời hữu ích, yêu cầu clarify nếu cần, đưa ví dụ cụ thể
4. Đa dạng: thông tin, hướng dẫn, so sánh, troubleshooting, advice
5. Độ dài response: {MIN_RESPONSE_LENGTH}-{MAX_RESPONSE_LENGTH} chars

FORMAT JSON:
{{
    "conversation": [
        {{"role": "user", "content": "..."}},
        {{"role": "assistant", "content": "..."}},
        ...
    ],
    "metadata": {{
        "difficulty": "easy|medium|hard",
        "quality_score": 8-10
    }}
}}

CHỈ trả về JSON."""

    async def call_api(self, prompt: str, session: aiohttp.ClientSession) -> str:
        """Gọi API với retry logic"""
        if self.api_type == "openai":
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Chuyên gia tạo training data. Tạo conversations tự nhiên, chất lượng cao. Luôn trả về JSON hợp lệ."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": TEMPERATURE,
                    "response_format": {"type": "json_object"}
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                result = await resp.json()
                return result['choices'][0]['message']['content']
        else:  # anthropic
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={
                    "model": self.model,
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": prompt}],
                    "system": "Chuyên gia tạo training data. Tạo conversations tự nhiên, chất lượng cao. Luôn trả về JSON hợp lệ.",
                    "temperature": TEMPERATURE
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                result = await resp.json()
                return result['content'][0]['text']

    async def generate_one(self, scenario: Dict, session: aiohttp.ClientSession) -> Optional[Dict]:
        """Sinh 1 conversation với retry"""
        for attempt in range(3):
            try:
                response = await self.call_api(self.create_prompt(scenario), session)
                data = json.loads(response)

                conv = {
                    "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                    "timestamp": datetime.now().isoformat(),
                    "scenario": scenario,
                    "conversation": data["conversation"],
                    "metadata": data.get("metadata", {}),
                    "source": f"{self.api_type}_{self.model}"
                }

                if self.quality_check(conv):
                    self.stats["success"] += 1
                    return conv
                else:
                    self.stats["filtered"] += 1

            except Exception as e:
                if attempt == 2:
                    self.stats["failed"] += 1
                    print(f"✗ Failed: {scenario['topic'][:40]}")
                await asyncio.sleep(1)

        return None

    def quality_check(self, conv: Dict) -> bool:
        """Kiểm tra chất lượng"""
        if not ENABLE_QUALITY_FILTER:
            return True

        turns = conv["conversation"]
        if len(turns) < 4:
            return False

        for turn in turns:
            length = len(turn["content"])
            if length < MIN_RESPONSE_LENGTH or length > MAX_RESPONSE_LENGTH:
                return False

        return True

    async def generate_all(self, scenarios: List[Dict]) -> List[Dict]:
        """Sinh tất cả với progress"""
        print(f"\n🚀 Đang sinh {len(scenarios)} conversations...\n")

        async with aiohttp.ClientSession() as session:
            tasks = [self.generate_one(s, session) for s in scenarios]

            # Progress tracking
            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                result = await task
                if result:
                    self.data.append(result)

                # Progress bar
                progress = i / len(scenarios)
                bar_len = 40
                filled = int(bar_len * progress)
                bar = "█" * filled + "░" * (bar_len - filled)
                print(f"\r  [{bar}] {i}/{len(scenarios)} ({progress*100:.0f}%) | ✓ {self.stats['success']} | ✗ {self.stats['failed']} | ~ {self.stats['filtered']}", end="")

        print("\n")
        return self.data

    def save_all(self):
        """Lưu tất cả formats"""
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON
        with open(f"{OUTPUT_DIR}/conversations_{ts}.json", 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        # JSONL
        with open(f"{OUTPUT_DIR}/conversations_{ts}.jsonl", 'w', encoding='utf-8') as f:
            for item in self.data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        # CSV
        rows = []
        for conv in self.data:
            for i, turn in enumerate(conv['conversation']):
                rows.append({
                    'id': conv['id'],
                    'turn': i,
                    'role': turn['role'],
                    'content': turn['content'],
                    'topic': conv['scenario']['topic']
                })
        with open(f"{OUTPUT_DIR}/conversations_{ts}.csv", 'w', encoding='utf-8', newline='') as f:
            if rows:
                csv.DictWriter(f, rows[0].keys()).writeheader()
                csv.DictWriter(f, rows[0].keys()).writerows(rows)

        # OpenAI format
        with open(f"{OUTPUT_DIR}/openai_{ts}.jsonl", 'w', encoding='utf-8') as f:
            for conv in self.data:
                f.write(json.dumps({"messages": conv['conversation']}, ensure_ascii=False) + '\n')

        print(f"💾 Đã lưu vào {OUTPUT_DIR}/")
        print(f"   • conversations_{ts}.json")
        print(f"   • conversations_{ts}.jsonl")
        print(f"   • conversations_{ts}.csv")
        print(f"   • openai_{ts}.jsonl")

    def show_stats(self):
        """Hiển thị thống kê"""
        print("\n" + "=" * 70)
        print("📊 THỐNG KÊ")
        print("=" * 70)

        total_turns = sum(len(c['conversation']) for c in self.data)
        topics = Counter(c['scenario']['topic'] for c in self.data)

        print(f"\n✅ Kết quả:")
        print(f"   • Thành công: {self.stats['success']} conversations")
        print(f"   • Thất bại: {self.stats['failed']}")
        print(f"   • Filtered out: {self.stats['filtered']}")
        print(f"   • Tổng turns: {total_turns}")
        print(f"   • TB turns/conv: {total_turns/len(self.data):.1f}")

        print(f"\n📚 Top 10 chủ đề:")
        for topic, count in topics.most_common(10):
            print(f"   • {topic[:50]:50} {count}")

        print("\n" + "=" * 70)

# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("\n" + "=" * 70)
    print("🤖 AI TRAINING DATA GENERATOR - PHIÊN BẢN TỐI ƯU")
    print("=" * 70)

    # Validate
    gen = OptimizedGenerator()
    if not gen.api_key:
        print("\n❌ Lỗi: Không tìm thấy API key!")
        print("\nChạy command:")
        print("  export OPENAI_API_KEY='your-key'")
        print("\nHoặc:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        return

    # Config
    print(f"\n⚙️  Cấu hình:")
    print(f"   • API: {API_TYPE}")
    print(f"   • Model: {MODEL}")
    print(f"   • Scenarios: {len(SCENARIOS)} (lấy {NUM_CONVERSATIONS})")
    print(f"   • Batch size: {BATCH_SIZE}")
    print(f"   • Temperature: {TEMPERATURE}")

    # Generate
    selected = random.sample(SCENARIOS, min(NUM_CONVERSATIONS, len(SCENARIOS)))
    await gen.generate_all(selected)

    # Save & Stats
    if gen.data:
        gen.save_all()
        gen.show_stats()

        print("\n✅ HOÀN TẤT! Dữ liệu đã sẵn sàng để train AI! 🎉\n")
    else:
        print("\n❌ Không sinh được dữ liệu nào. Check API key và logs.\n")

if __name__ == "__main__":
    asyncio.run(main())
