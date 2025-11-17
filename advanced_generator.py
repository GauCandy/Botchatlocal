"""
Advanced Training Data Generator với nhiều tính năng
- Hỗ trợ custom scenarios
- Quality filtering
- Progress tracking
- Multiple languages
- Error handling và retry logic
"""

import json
import asyncio
import aiohttp
import random
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import logging
from tqdm.asyncio import tqdm
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO if config.VERBOSE else logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE) if config.SAVE_LOGS else logging.NullHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdvancedTrainingDataGenerator:
    """Advanced generator với nhiều tính năng nâng cao"""

    def __init__(self):
        self.api_key = config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY
        self.api_type = config.API_TYPE
        self.model = config.MODEL_NAME
        self.generated_data = []
        self.failed_generations = []
        self.stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0,
            "filtered_out": 0
        }

    async def generate_with_retry(self, scenario: Dict, session: aiohttp.ClientSession, max_retries: int = 3) -> Optional[Dict]:
        """Sinh conversation với retry logic"""

        for attempt in range(max_retries):
            try:
                self.stats["total_attempts"] += 1

                prompt = self._create_advanced_prompt(scenario)

                if self.api_type == "openai":
                    response = await self._call_openai(prompt, session)
                elif self.api_type == "anthropic":
                    response = await self._call_anthropic(prompt, session)
                else:
                    logger.error(f"Unsupported API type: {self.api_type}")
                    return None

                conversation = self._parse_and_validate(response, scenario)

                if conversation and self._quality_check(conversation):
                    self.stats["successful"] += 1
                    return conversation
                else:
                    self.stats["filtered_out"] += 1
                    logger.warning(f"Conversation filtered out: quality check failed")

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(config.RETRY_DELAY * (attempt + 1))
                else:
                    self.stats["failed"] += 1
                    self.failed_generations.append({
                        "scenario": scenario,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })

        return None

    def _create_advanced_prompt(self, scenario: Dict) -> str:
        """Tạo prompt nâng cao với nhiều yêu cầu chi tiết"""

        language = config.PRIMARY_LANGUAGE
        turns = scenario.get('turns', config.DEFAULT_TURNS)

        prompt = f"""Tạo một cuộc hội thoại chất lượng cao giữa User và AI Assistant:

THÔNG TIN:
- Chủ đề: {scenario['topic']}
- Ngữ cảnh: {scenario['context']}
- Mục tiêu: {scenario['goal']}
- Số lượt: {turns} turns
- Ngôn ngữ: {"Tiếng Việt" if language == "vi" else "English"}

YÊU CẦU CHẤT LƯỢNG:
1. Hội thoại phải TỰ NHIÊN như người thật nói chuyện
2. User có thể:
   - Hỏi câu không rõ ràng, thiếu thông tin
   - Hỏi follow-up questions
   - Thay đổi chủ đề nhẹ
   - Dùng ngôn ngữ thông tục, informal
3. AI Assistant phải:
   - Trả lời chính xác, hữu ích
   - Yêu cầu clarification nếu câu hỏi không rõ
   - Đưa ra ví dụ cụ thể khi cần
   - Giải thích đơn giản, dễ hiểu
   - Thể hiện empathy và friendliness
4. Độ dài response: {config.MIN_RESPONSE_LENGTH}-{config.MAX_RESPONSE_LENGTH} ký tự

CẤU TRÚC CÂU HỎI ĐA DẠNG:
- Informational: "Cho tôi biết về..."
- How-to: "Làm thế nào để..."
- Comparison: "So sánh A và B..."
- Troubleshooting: "Tôi gặp vấn đề..."
- Opinion/Advice: "Bạn nghĩ gì về..."

OUTPUT FORMAT (JSON):
{{
    "conversation": [
        {{"role": "user", "content": "..."}},
        {{"role": "assistant", "content": "..."}},
        ...
    ],
    "metadata": {{
        "topic": "{scenario['topic']}",
        "category": "{scenario.get('category', 'general')}",
        "difficulty": "easy|medium|hard",
        "language": "{language}",
        "quality_score": 8-10
    }}
}}

CHỈ trả về JSON, KHÔNG thêm text khác."""

        return prompt

    async def _call_openai(self, prompt: str, session: aiohttp.ClientSession) -> str:
        """Call OpenAI API với error handling"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia tạo dữ liệu training cho AI. Tạo conversations tự nhiên, chất lượng cao, đa dạng. Luôn trả về JSON hợp lệ."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": config.TEMPERATURE,
            "response_format": {"type": "json_object"}
        }

        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OpenAI API error {response.status}: {error_text}")

            result = await response.json()
            return result['choices'][0]['message']['content']

    async def _call_anthropic(self, prompt: str, session: aiohttp.ClientSession) -> str:
        """Call Anthropic API với error handling"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "system": "Bạn là chuyên gia tạo dữ liệu training cho AI. Tạo conversations tự nhiên, chất lượng cao, đa dạng. Luôn trả về JSON hợp lệ.",
            "temperature": config.TEMPERATURE
        }

        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Anthropic API error {response.status}: {error_text}")

            result = await response.json()
            return result['content'][0]['text']

    def _parse_and_validate(self, response: str, scenario: Dict) -> Optional[Dict]:
        """Parse và validate response"""
        try:
            # Parse JSON
            data = json.loads(response)

            # Validate structure
            if "conversation" not in data or not isinstance(data["conversation"], list):
                logger.warning("Invalid conversation structure")
                return None

            if len(data["conversation"]) < 2:
                logger.warning("Conversation too short")
                return None

            # Create formatted conversation
            conversation_data = {
                "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                "timestamp": datetime.now().isoformat(),
                "scenario": scenario,
                "conversation": data["conversation"],
                "metadata": data.get("metadata", {}),
                "source": f"{self.api_type}_{self.model}"
            }

            return conversation_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None

    def _quality_check(self, conversation: Dict) -> bool:
        """Kiểm tra chất lượng conversation"""

        if not config.ENABLE_QUALITY_FILTER:
            return True

        try:
            conv = conversation["conversation"]

            # Check minimum turns
            if len(conv) < 4:
                return False

            # Check response lengths
            for turn in conv:
                content_len = len(turn["content"])
                if content_len < config.MIN_RESPONSE_LENGTH:
                    logger.debug(f"Response too short: {content_len} chars")
                    return False
                if content_len > config.MAX_RESPONSE_LENGTH:
                    logger.debug(f"Response too long: {content_len} chars")
                    return False

            # Check alternating roles
            for i in range(len(conv) - 1):
                if conv[i]["role"] == conv[i+1]["role"]:
                    logger.debug("Roles not alternating properly")
                    return False

            return True

        except Exception as e:
            logger.error(f"Quality check error: {e}")
            return False

    async def generate_batch_with_progress(self, scenarios: List[Dict]) -> List[Dict]:
        """Sinh batch với progress bar"""

        conversations = []

        async with aiohttp.ClientSession() as session:
            # Create tasks with progress bar
            tasks = []
            for scenario in scenarios:
                task = self.generate_with_retry(scenario, session, config.MAX_RETRIES)
                tasks.append(task)

            # Run with progress bar
            results = []
            for coro in tqdm.as_completed(tasks, total=len(tasks), desc="Generating"):
                result = await coro
                if result:
                    results.append(result)
                    self.generated_data.append(result)

        return results

    def save_all_formats(self, base_filename: str):
        """Lưu tất cả formats được config"""

        output_dir = Path(config.OUTPUT_DIR)
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if config.EXPORT_FORMATS.get("json", False):
            self._save_json(output_dir / f"{base_filename}_{timestamp}.json")

        if config.EXPORT_FORMATS.get("jsonl", False):
            self._save_jsonl(output_dir / f"{base_filename}_{timestamp}.jsonl")

        if config.EXPORT_FORMATS.get("csv", False):
            self._save_csv(output_dir / f"{base_filename}_{timestamp}.csv")

        if config.EXPORT_FORMATS.get("openai", False):
            self._save_openai_format(output_dir / f"openai_{base_filename}_{timestamp}.jsonl")

    def _save_json(self, filepath: Path):
        """Save to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.generated_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Saved {len(self.generated_data)} conversations to {filepath}")

    def _save_jsonl(self, filepath: Path):
        """Save to JSONL"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in self.generated_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        logger.info(f"✓ Saved {len(self.generated_data)} conversations to {filepath}")

    def _save_csv(self, filepath: Path):
        """Save to CSV"""
        import csv

        rows = []
        for conv in self.generated_data:
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
            logger.info(f"✓ Saved {len(rows)} turns to {filepath}")

    def _save_openai_format(self, filepath: Path):
        """Save in OpenAI fine-tuning format"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for conv in self.generated_data:
                training_example = {"messages": conv['conversation']}
                f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
        logger.info(f"✓ Saved {len(self.generated_data)} conversations to {filepath} (OpenAI format)")

    def print_statistics(self):
        """In thống kê chi tiết"""
        print("\n" + "=" * 70)
        print("THỐNG KÊ CHI TIẾT")
        print("=" * 70)

        print(f"\n📊 Generation Stats:")
        print(f"  • Tổng attempts: {self.stats['total_attempts']}")
        print(f"  • Thành công: {self.stats['successful']} ✓")
        print(f"  • Thất bại: {self.stats['failed']} ✗")
        print(f"  • Filtered out: {self.stats['filtered_out']} ⚠")

        if self.stats['total_attempts'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total_attempts']) * 100
            print(f"  • Success rate: {success_rate:.1f}%")

        if self.generated_data:
            total_turns = sum(len(conv['conversation']) for conv in self.generated_data)
            avg_turns = total_turns / len(self.generated_data)

            print(f"\n💬 Conversation Stats:")
            print(f"  • Tổng conversations: {len(self.generated_data)}")
            print(f"  • Tổng turns: {total_turns}")
            print(f"  • Trung bình turns/conv: {avg_turns:.1f}")

            # Topics distribution
            topics = {}
            for conv in self.generated_data:
                topic = conv['scenario']['topic']
                topics[topic] = topics.get(topic, 0) + 1

            print(f"\n📚 Top Topics:")
            for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  • {topic}: {count}")

        if self.failed_generations:
            print(f"\n⚠ Failed Generations: {len(self.failed_generations)}")
            print("  Check logs for details")

        print("\n" + "=" * 70)


def load_scenarios() -> List[Dict]:
    """Load scenarios từ config hoặc default"""

    from training_data_generator import VIETNAMESE_SCENARIOS

    if config.CUSTOM_SCENARIOS:
        logger.info(f"Using {len(config.CUSTOM_SCENARIOS)} custom scenarios")
        return config.CUSTOM_SCENARIOS

    # Filter by enabled categories
    filtered_scenarios = []
    category_map = {
        "Lập trình": "technology",
        "Khắc phục lỗi": "technology",
        "Machine Learning": "technology",
        "Web Development": "technology",
        "Database": "technology",
        "Nấu ăn": "food",
        "Tập thể dục": "lifestyle",
        "Du lịch": "travel",
        "Chăm sóc sức khỏe": "health",
        "Quản lý tài chính": "finance",
        "Học tiếng Anh": "education",
        "Toán học": "education",
        "Khởi nghiệp": "business",
        "Marketing": "business",
    }

    for scenario in VIETNAMESE_SCENARIOS:
        # Determine category
        category = "general"
        for keyword, cat in category_map.items():
            if keyword.lower() in scenario['topic'].lower():
                category = cat
                break

        scenario['category'] = category

        # Check if category is enabled
        if config.ENABLED_CATEGORIES.get(category, True):
            filtered_scenarios.append(scenario)

    # Limit to configured number
    if len(filtered_scenarios) > config.NUM_CONVERSATIONS:
        filtered_scenarios = random.sample(filtered_scenarios, config.NUM_CONVERSATIONS)

    logger.info(f"Using {len(filtered_scenarios)} scenarios")
    return filtered_scenarios


async def main():
    """Main function"""
    print("=" * 70)
    print("🤖 ADVANCED AI TRAINING DATA GENERATOR")
    print("=" * 70)
    print()

    # Validate API key
    if not (config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY):
        print("❌ Lỗi: Không tìm thấy API key!")
        print("\nVui lòng:")
        print("1. Set environment variable:")
        print("   export OPENAI_API_KEY='your-key'")
        print("   hoặc")
        print("   export ANTHROPIC_API_KEY='your-key'")
        print("\n2. Hoặc sửa trong file config.py")
        return

    # Show config
    print(f"⚙️  Configuration:")
    print(f"  • API: {config.API_TYPE}")
    print(f"  • Model: {config.MODEL_NAME}")
    print(f"  • Conversations: {config.NUM_CONVERSATIONS}")
    print(f"  • Batch size: {config.BATCH_SIZE}")
    print(f"  • Temperature: {config.TEMPERATURE}")
    print()

    # Initialize generator
    generator = AdvancedTrainingDataGenerator()

    # Load scenarios
    scenarios = load_scenarios()
    print(f"📋 Loaded {len(scenarios)} scenarios")
    print()

    # Generate data
    print("🚀 Bắt đầu sinh dữ liệu...")
    print("(Quá trình này có thể mất vài phút)\n")

    await generator.generate_batch_with_progress(scenarios)

    # Save results
    print("\n💾 Đang lưu dữ liệu...")
    generator.save_all_formats("conversations")

    # Print statistics
    generator.print_statistics()

    # Save failed generations for debugging
    if generator.failed_generations:
        failed_path = Path(config.OUTPUT_DIR) / "failed_generations.json"
        with open(failed_path, 'w', encoding='utf-8') as f:
            json.dump(generator.failed_generations, f, ensure_ascii=False, indent=2)
        print(f"\n⚠  Saved failed generations to {failed_path}")

    print("\n✅ HOÀN THÀNH!")
    print(f"📁 Dữ liệu đã được lưu trong: {config.OUTPUT_DIR}/")
    print("\nBạn có thể dùng các file này để train chatbot! 🎉\n")


if __name__ == "__main__":
    asyncio.run(main())
