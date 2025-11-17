"""
AI Training Data Generator
Sinh dữ liệu training chất lượng cao cho chatbot AI
"""

import json
import csv
import random
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
import os
from pathlib import Path


class TrainingDataGenerator:
    """
    Class để sinh dữ liệu training cho AI chatbot
    Hỗ trợ nhiều API: OpenAI, Anthropic, hoặc local models
    """

    def __init__(self, api_key: str = None, api_type: str = "openai", model: str = None):
        """
        Khởi tạo generator

        Args:
            api_key: API key cho service (OpenAI, Anthropic, etc.)
            api_type: Loại API ("openai", "anthropic", "gemini")
            model: Model name (mặc định sẽ chọn model phù hợp)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.api_type = api_type.lower()

        # Chọn model mặc định dựa trên API type
        if model:
            self.model = model
        elif self.api_type == "openai":
            self.model = "gpt-4o-mini"  # Rẻ và nhanh
        elif self.api_type == "anthropic":
            self.model = "claude-3-5-haiku-20241022"
        elif self.api_type == "gemini":
            self.model = "gemini-1.5-flash"
        else:
            self.model = "gpt-4o-mini"

        self.generated_data = []

    async def generate_conversation(self, scenario: Dict, session: aiohttp.ClientSession) -> Optional[Dict]:
        """
        Sinh một cuộc hội thoại dựa trên scenario

        Args:
            scenario: Dictionary chứa thông tin về tình huống
            session: aiohttp session để gọi API

        Returns:
            Dictionary chứa cuộc hội thoại
        """
        try:
            prompt = self._create_generation_prompt(scenario)

            if self.api_type == "openai":
                response = await self._call_openai(prompt, session)
            elif self.api_type == "anthropic":
                response = await self._call_anthropic(prompt, session)
            else:
                print(f"API type {self.api_type} chưa được hỗ trợ")
                return None

            # Parse response và tạo training data
            conversation = self._parse_conversation(response, scenario)
            return conversation

        except Exception as e:
            print(f"Lỗi khi sinh conversation: {e}")
            return None

    def _create_generation_prompt(self, scenario: Dict) -> str:
        """Tạo prompt để AI sinh cuộc hội thoại"""

        prompt = f"""Hãy tạo một cuộc hội thoại tự nhiên giữa người dùng và AI assistant trong tình huống sau:

Chủ đề: {scenario['topic']}
Ngữ cảnh: {scenario['context']}
Mục tiêu: {scenario['goal']}
Độ dài: {scenario.get('turns', 5)} lượt hội thoại

Yêu cầu:
1. Cuộc hội thoại phải tự nhiên, giống cách con người nói chuyện thực tế
2. AI assistant phải hữu ích, chính xác và thân thiện
3. Bao gồm nhiều dạng câu hỏi: thông tin, hướng dẫn, giải thích, so sánh
4. Người dùng có thể hỏi follow-up questions
5. AI có thể yêu cầu làm rõ nếu câu hỏi không rõ ràng

Trả về định dạng JSON với structure:
{{
    "conversation": [
        {{"role": "user", "content": "câu hỏi của user"}},
        {{"role": "assistant", "content": "câu trả lời của AI"}},
        ...
    ],
    "metadata": {{
        "topic": "{scenario['topic']}",
        "difficulty": "easy|medium|hard",
        "language": "vi"
    }}
}}

Chỉ trả về JSON, không thêm text nào khác."""

        return prompt

    async def _call_openai(self, prompt: str, session: aiohttp.ClientSession) -> str:
        """Gọi OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Bạn là một chuyên gia tạo dữ liệu training cho AI chatbot. Bạn tạo các cuộc hội thoại chất lượng cao, tự nhiên và đa dạng."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,  # Tăng creativity
            "response_format": {"type": "json_object"}
        }

        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            result = await response.json()
            return result['choices'][0]['message']['content']

    async def _call_anthropic(self, prompt: str, session: aiohttp.ClientSession) -> str:
        """Gọi Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "system": "Bạn là một chuyên gia tạo dữ liệu training cho AI chatbot. Bạn tạo các cuộc hội thoại chất lượng cao, tự nhiên và đa dạng. Luôn trả về JSON hợp lệ.",
            "temperature": 0.8
        }

        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            result = await response.json()
            return result['content'][0]['text']

    def _parse_conversation(self, response: str, scenario: Dict) -> Dict:
        """Parse response từ API thành format chuẩn"""
        try:
            # Parse JSON từ response
            data = json.loads(response)

            # Thêm thông tin metadata
            conversation_data = {
                "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                "timestamp": datetime.now().isoformat(),
                "scenario": scenario,
                "conversation": data.get("conversation", []),
                "metadata": data.get("metadata", {}),
                "source": f"{self.api_type}_{self.model}"
            }

            return conversation_data

        except json.JSONDecodeError as e:
            print(f"Lỗi parse JSON: {e}")
            print(f"Response: {response[:200]}")
            return None

    async def generate_batch(self, scenarios: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Sinh nhiều conversations cùng lúc (batch processing)

        Args:
            scenarios: List các scenarios
            batch_size: Số lượng requests đồng thời

        Returns:
            List các conversations đã sinh
        """
        conversations = []

        async with aiohttp.ClientSession() as session:
            # Chia scenarios thành batches
            for i in range(0, len(scenarios), batch_size):
                batch = scenarios[i:i + batch_size]
                print(f"Đang xử lý batch {i//batch_size + 1}/{(len(scenarios)-1)//batch_size + 1}...")

                # Gọi API đồng thời cho batch
                tasks = [self.generate_conversation(scenario, session) for scenario in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Lọc kết quả hợp lệ
                for result in results:
                    if isinstance(result, dict) and result is not None:
                        conversations.append(result)
                        self.generated_data.append(result)

                # Delay nhỏ giữa các batch để tránh rate limit
                if i + batch_size < len(scenarios):
                    await asyncio.sleep(1)

        return conversations

    def save_to_json(self, filename: str, data: List[Dict] = None):
        """Lưu dữ liệu ra file JSON"""
        data = data or self.generated_data
        output_dir = Path("training_data")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Đã lưu {len(data)} conversations vào {filepath}")

    def save_to_jsonl(self, filename: str, data: List[Dict] = None):
        """Lưu dữ liệu ra file JSONL (mỗi dòng là một JSON object)"""
        data = data or self.generated_data
        output_dir = Path("training_data")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        print(f"✓ Đã lưu {len(data)} conversations vào {filepath}")

    def save_to_csv(self, filename: str, data: List[Dict] = None):
        """Lưu dữ liệu ra file CSV"""
        data = data or self.generated_data
        output_dir = Path("training_data")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename

        # Flatten conversations thành rows
        rows = []
        for conv in data:
            for i, turn in enumerate(conv['conversation']):
                rows.append({
                    'conversation_id': conv['id'],
                    'turn': i,
                    'role': turn['role'],
                    'content': turn['content'],
                    'topic': conv['scenario']['topic'],
                    'timestamp': conv['timestamp']
                })

        if rows:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            print(f"✓ Đã lưu {len(rows)} turns vào {filepath}")

    def save_to_openai_format(self, filename: str, data: List[Dict] = None):
        """Lưu theo format của OpenAI fine-tuning"""
        data = data or self.generated_data
        output_dir = Path("training_data")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            for conv in data:
                # Format theo OpenAI fine-tuning
                messages = conv['conversation']
                training_example = {
                    "messages": messages
                }
                f.write(json.dumps(training_example, ensure_ascii=False) + '\n')

        print(f"✓ Đã lưu {len(data)} conversations vào {filepath} (OpenAI format)")

    def get_statistics(self, data: List[Dict] = None) -> Dict:
        """Lấy thống kê về dữ liệu đã sinh"""
        data = data or self.generated_data

        if not data:
            return {"total_conversations": 0}

        total_turns = sum(len(conv['conversation']) for conv in data)
        topics = {}

        for conv in data:
            topic = conv['scenario']['topic']
            topics[topic] = topics.get(topic, 0) + 1

        return {
            "total_conversations": len(data),
            "total_turns": total_turns,
            "avg_turns_per_conversation": total_turns / len(data) if data else 0,
            "topics_distribution": topics,
            "date_generated": datetime.now().isoformat()
        }


# Các scenarios mẫu đa dạng
VIETNAMESE_SCENARIOS = [
    # Công nghệ
    {
        "topic": "Lập trình Python cơ bản",
        "context": "Người dùng muốn học Python",
        "goal": "Giải thích cách bắt đầu học Python",
        "turns": 6
    },
    {
        "topic": "Khắc phục lỗi code",
        "context": "Người dùng gặp lỗi khi chạy code",
        "goal": "Giúp debug và giải thích lỗi",
        "turns": 5
    },
    {
        "topic": "Machine Learning cơ bản",
        "context": "Người dùng muốn hiểu về AI/ML",
        "goal": "Giải thích khái niệm ML đơn giản",
        "turns": 7
    },
    {
        "topic": "Web Development",
        "context": "Người dùng muốn tạo website",
        "goal": "Hướng dẫn công nghệ web cần học",
        "turns": 6
    },
    {
        "topic": "Database SQL",
        "context": "Người dùng cần truy vấn database",
        "goal": "Giải thích SQL queries",
        "turns": 5
    },

    # Đời sống
    {
        "topic": "Nấu ăn món Việt",
        "context": "Người dùng muốn học nấu món truyền thống",
        "goal": "Hướng dẫn công thức nấu ăn",
        "turns": 7
    },
    {
        "topic": "Tập thể dục tại nhà",
        "context": "Người dùng muốn tập luyện không cần thiết bị",
        "goal": "Gợi ý bài tập và lịch trình",
        "turns": 6
    },
    {
        "topic": "Du lịch Việt Nam",
        "context": "Người dùng lên kế hoạch du lịch",
        "goal": "Tư vấn địa điểm và lịch trình",
        "turns": 8
    },
    {
        "topic": "Chăm sóc sức khỏe",
        "context": "Người dùng muốn cải thiện sức khỏe",
        "goal": "Tư vấn thói quen lành mạnh",
        "turns": 6
    },
    {
        "topic": "Quản lý tài chính cá nhân",
        "context": "Người dùng muốn tiết kiệm tiền",
        "goal": "Tư vấn cách quản lý chi tiêu",
        "turns": 7
    },

    # Giáo dục
    {
        "topic": "Học tiếng Anh",
        "context": "Người dùng muốn cải thiện tiếng Anh",
        "goal": "Tư vấn phương pháp học hiệu quả",
        "turns": 6
    },
    {
        "topic": "Toán học phổ thông",
        "context": "Học sinh cần giải bài toán",
        "goal": "Giải thích cách làm bài toán",
        "turns": 5
    },
    {
        "topic": "Kỹ năng mềm",
        "context": "Người dùng muốn phát triển kỹ năng giao tiếp",
        "goal": "Tư vấn cách cải thiện kỹ năng",
        "turns": 6
    },
    {
        "topic": "Lịch sử Việt Nam",
        "context": "Người dùng muốn tìm hiểu lịch sử",
        "goal": "Giải thích sự kiện lịch sử",
        "turns": 6
    },
    {
        "topic": "Khoa học tự nhiên",
        "context": "Người dùng tò mò về hiện tượng tự nhiên",
        "goal": "Giải thích khoa học đơn giản",
        "turns": 5
    },

    # Kinh doanh
    {
        "topic": "Khởi nghiệp kinh doanh",
        "context": "Người dùng muốn mở doanh nghiệp",
        "goal": "Tư vấn các bước khởi nghiệp",
        "turns": 8
    },
    {
        "topic": "Marketing online",
        "context": "Người dùng muốn quảng cáo sản phẩm",
        "goal": "Hướng dẫn chiến lược marketing",
        "turns": 7
    },
    {
        "topic": "Quản lý nhân sự",
        "context": "Người quản lý cần tư vấn",
        "goal": "Giải quyết vấn đề quản lý",
        "turns": 6
    },
    {
        "topic": "Thương mại điện tử",
        "context": "Người dùng muốn bán hàng online",
        "goal": "Hướng dẫn setup shop online",
        "turns": 7
    },
    {
        "topic": "Dịch vụ khách hàng",
        "context": "Nhân viên cần xử lý khách hàng khó",
        "goal": "Tư vấn kỹ năng customer service",
        "turns": 5
    },

    # Giải trí & Sở thích
    {
        "topic": "Nhiếp ảnh di động",
        "context": "Người dùng muốn chụp ảnh đẹp bằng điện thoại",
        "goal": "Hướng dẫn kỹ thuật chụp ảnh",
        "turns": 6
    },
    {
        "topic": "Âm nhạc và nhạc cụ",
        "context": "Người dùng muốn học đàn guitar",
        "goal": "Tư vấn cách bắt đầu học nhạc cụ",
        "turns": 6
    },
    {
        "topic": "Làm vườn ban công",
        "context": "Người dùng muốn trồng cây trong nhà",
        "goal": "Hướng dẫn chăm sóc cây trồng",
        "turns": 5
    },
    {
        "topic": "Phim ảnh và review",
        "context": "Người dùng tìm phim hay để xem",
        "goal": "Gợi ý phim và giải thích",
        "turns": 6
    },
    {
        "topic": "Game và esports",
        "context": "Người dùng muốn cải thiện kỹ năng chơi game",
        "goal": "Tư vấn chiến thuật và tips",
        "turns": 5
    },

    # Kỹ thuật nâng cao
    {
        "topic": "DevOps và CI/CD",
        "context": "Developer muốn tự động hóa deployment",
        "goal": "Giải thích setup CI/CD pipeline",
        "turns": 7
    },
    {
        "topic": "Cloud Computing AWS",
        "context": "Người dùng muốn deploy app lên cloud",
        "goal": "Hướng dẫn sử dụng AWS services",
        "turns": 8
    },
    {
        "topic": "Bảo mật ứng dụng web",
        "context": "Developer lo ngại về security",
        "goal": "Tư vấn best practices bảo mật",
        "turns": 7
    },
    {
        "topic": "Mobile App Development",
        "context": "Người dùng muốn tạo app di động",
        "goal": "So sánh các framework và hướng dẫn",
        "turns": 6
    },
    {
        "topic": "Data Science với Python",
        "context": "Người dùng muốn phân tích dữ liệu",
        "goal": "Hướng dẫn pandas, numpy, visualization",
        "turns": 7
    },
]


async def main():
    """Hàm main để chạy generator"""
    print("=" * 60)
    print("AI TRAINING DATA GENERATOR")
    print("Sinh dữ liệu training chất lượng cao cho chatbot")
    print("=" * 60)
    print()

    # Cấu hình
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("⚠ Cảnh báo: Không tìm thấy API key!")
        print("Vui lòng set environment variable:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  hoặc")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Xác định API type dựa trên env var
    if os.getenv("OPENAI_API_KEY"):
        api_type = "openai"
        print(f"✓ Sử dụng OpenAI API")
    else:
        api_type = "anthropic"
        print(f"✓ Sử dụng Anthropic API")

    # Khởi tạo generator
    generator = TrainingDataGenerator(
        api_key=api_key,
        api_type=api_type
    )

    print(f"✓ Model: {generator.model}")
    print(f"✓ Số scenarios: {len(VIETNAMESE_SCENARIOS)}")
    print()

    # Sinh dữ liệu
    print("Đang sinh dữ liệu training...")
    print("(Quá trình này có thể mất vài phút)")
    print()

    conversations = await generator.generate_batch(
        scenarios=VIETNAMESE_SCENARIOS,
        batch_size=5  # Giảm nếu gặp rate limit
    )

    print()
    print("=" * 60)
    print(f"✓ Đã sinh {len(conversations)} conversations thành công!")
    print("=" * 60)
    print()

    # Lưu dữ liệu ra nhiều formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    generator.save_to_json(f"conversations_{timestamp}.json")
    generator.save_to_jsonl(f"conversations_{timestamp}.jsonl")
    generator.save_to_csv(f"conversations_{timestamp}.csv")
    generator.save_to_openai_format(f"openai_format_{timestamp}.jsonl")

    # Hiển thị thống kê
    print()
    print("=" * 60)
    print("THỐNG KÊ")
    print("=" * 60)
    stats = generator.get_statistics()
    print(f"Tổng số conversations: {stats['total_conversations']}")
    print(f"Tổng số turns: {stats['total_turns']}")
    print(f"Trung bình turns/conversation: {stats['avg_turns_per_conversation']:.1f}")
    print()
    print("Phân bố theo chủ đề:")
    for topic, count in sorted(stats['topics_distribution'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {topic}: {count} conversations")

    print()
    print("=" * 60)
    print("✓ HOÀN THÀNH!")
    print("=" * 60)
    print()
    print("Dữ liệu đã được lưu trong thư mục: training_data/")
    print("Bạn có thể dùng các file này để train chatbot của mình!")


if __name__ == "__main__":
    asyncio.run(main())
