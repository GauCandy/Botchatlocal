#!/usr/bin/env python3
"""
Quick Start Script - Bắt đầu nhanh với ví dụ đơn giản
Chỉ sinh 5 conversations để test
"""

import asyncio
import os
from training_data_generator import TrainingDataGenerator, VIETNAMESE_SCENARIOS
import random


async def main():
    print("=" * 60)
    print("🚀 QUICK START - Test Generator")
    print("=" * 60)
    print()

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ Lỗi: Không tìm thấy API key!")
        print()
        print("Để test nhanh, hãy chạy:")
        print("  export OPENAI_API_KEY='your-key'")
        print()
        print("Hoặc tạo file .env với nội dung:")
        print("  OPENAI_API_KEY=your-key-here")
        return

    # Determine API type
    if os.getenv("OPENAI_API_KEY"):
        api_type = "openai"
    else:
        api_type = "anthropic"

    print(f"✓ API: {api_type}")

    # Initialize generator
    generator = TrainingDataGenerator(api_key=api_key, api_type=api_type)
    print(f"✓ Model: {generator.model}")
    print()

    # Chọn ngẫu nhiên 5 scenarios để test
    test_scenarios = random.sample(VIETNAMESE_SCENARIOS, min(5, len(VIETNAMESE_SCENARIOS)))
    print(f"📋 Testing với {len(test_scenarios)} scenarios:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"  {i}. {scenario['topic']}")
    print()

    # Generate
    print("🔄 Đang sinh dữ liệu test...")
    print("(Mất khoảng 30-60 giây)")
    print()

    conversations = await generator.generate_batch(
        scenarios=test_scenarios,
        batch_size=3
    )

    if not conversations:
        print("❌ Không sinh được conversation nào. Check logs để biết lỗi.")
        return

    print()
    print("=" * 60)
    print(f"✅ Thành công! Đã sinh {len(conversations)} conversations")
    print("=" * 60)
    print()

    # Save
    generator.save_to_json("test_conversations.json")
    generator.save_to_jsonl("test_conversations.jsonl")

    # Show sample
    print("📄 Ví dụ conversation đầu tiên:")
    print("-" * 60)
    sample = conversations[0]
    print(f"Chủ đề: {sample['scenario']['topic']}")
    print(f"Số turns: {len(sample['conversation'])}")
    print()

    for i, turn in enumerate(sample['conversation'][:4], 1):  # Hiển thị 4 turns đầu
        role_display = "👤 User" if turn['role'] == 'user' else "🤖 AI"
        content = turn['content'][:150] + "..." if len(turn['content']) > 150 else turn['content']
        print(f"{role_display}: {content}")
        print()

    if len(sample['conversation']) > 4:
        print(f"... và {len(sample['conversation']) - 4} turns nữa")

    print("-" * 60)
    print()

    # Show stats
    stats = generator.get_statistics()
    print("📊 Thống kê:")
    print(f"  • Tổng turns: {stats['total_turns']}")
    print(f"  • Trung bình: {stats['avg_turns_per_conversation']:.1f} turns/conversation")
    print()

    print("=" * 60)
    print("✅ QUICKSTART HOÀN TẤT!")
    print("=" * 60)
    print()
    print("📁 Files được tạo:")
    print("  • training_data/test_conversations.json")
    print("  • training_data/test_conversations.jsonl")
    print()
    print("🎯 Tiếp theo:")
    print("  1. Xem file JSON để kiểm tra chất lượng")
    print("  2. Nếu OK, chạy: python advanced_generator.py")
    print("  3. Điều chỉnh config.py theo nhu cầu")
    print("  4. Sinh dữ liệu lớn hơn!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
