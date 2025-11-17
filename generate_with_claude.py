#!/usr/bin/env python3
"""
Sinh dữ liệu training bằng Claude Code
Không cần API key - dùng trực tiếp Claude!

Cách dùng:
1. Chạy script này
2. Tương tác với Claude để sinh từng batch
3. Dữ liệu được lưu tự động
"""

import json
from datetime import datetime
from pathlib import Path

def create_prompt_for_claude(scenarios, batch_num):
    """Tạo prompt để gửi cho Claude"""

    scenario_list = "\n".join([
        f"{i+1}. {s['topic']} - {s['context']} (Goal: {s['goal']}, {s.get('turns', 6)} turns)"
        for i, s in enumerate(scenarios)
    ])

    prompt = f"""Hãy sinh {len(scenarios)} conversations chất lượng cao cho training AI chatbot.

📋 SCENARIOS (Batch #{batch_num}):
{scenario_list}

📝 YÊU CẦU:
- Mỗi conversation phải TỰ NHIÊN như người thật
- User: hỏi không rõ ràng, follow-up questions, thay đổi chủ đề nhẹ
- AI: trả lời hữu ích, yêu cầu clarify nếu cần, đưa ví dụ cụ thể
- Độ dài response: 50-1000 ký tự
- Đa dạng: thông tin, hướng dẫn, so sánh, troubleshooting

🎯 OUTPUT FORMAT - Trả về JSON array:
```json
[
  {{
    "scenario": {{"topic": "...", "context": "...", "goal": "..."}},
    "conversation": [
      {{"role": "user", "content": "..."}},
      {{"role": "assistant", "content": "..."}},
      ...
    ],
    "metadata": {{"difficulty": "easy|medium|hard", "quality_score": 8-10}}
  }},
  ...
]
```

CHỈ trả về JSON array, không text khác!"""

    return prompt


def save_batch(data, batch_num):
    """Lưu batch data"""
    output_dir = Path("training_data")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"claude_batch_{batch_num}_{timestamp}.json"

    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu batch #{batch_num}: {filename}")
    return filename


def merge_all_batches():
    """Gộp tất cả batches thành 1 file"""
    output_dir = Path("training_data")
    batch_files = sorted(output_dir.glob("claude_batch_*.json"))

    if not batch_files:
        print("Chưa có batch nào!")
        return

    all_data = []
    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_file = output_dir / f"all_conversations_{timestamp}.json"

    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # JSONL
    jsonl_file = output_dir / f"all_conversations_{timestamp}.jsonl"
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for conv in all_data:
            f.write(json.dumps(conv, ensure_ascii=False) + '\n')

    # OpenAI format
    openai_file = output_dir / f"openai_format_{timestamp}.jsonl"
    with open(openai_file, 'w', encoding='utf-8') as f:
        for conv in all_data:
            f.write(json.dumps({"messages": conv['conversation']}, ensure_ascii=False) + '\n')

    print(f"\n🎉 Đã gộp {len(all_data)} conversations từ {len(batch_files)} batches!")
    print(f"📁 Files:")
    print(f"   • {merged_file.name}")
    print(f"   • {jsonl_file.name}")
    print(f"   • {openai_file.name}")


# Scenarios chia thành batches nhỏ (5 scenarios/batch)
ALL_SCENARIOS = [
    {"topic": "Lập trình Python cơ bản", "context": "Người dùng muốn học Python", "goal": "Hướng dẫn bắt đầu", "turns": 6},
    {"topic": "Debug lỗi code", "context": "Developer gặp lỗi", "goal": "Giúp tìm và sửa lỗi", "turns": 5},
    {"topic": "Machine Learning", "context": "Tìm hiểu AI/ML", "goal": "Giải thích ML đơn giản", "turns": 7},
    {"topic": "Web Development", "context": "Muốn tạo website", "goal": "Tư vấn công nghệ", "turns": 6},
    {"topic": "Database SQL", "context": "Thiết kế database", "goal": "Hướng dẫn SQL", "turns": 6},

    {"topic": "Nấu ăn món Việt", "context": "Học nấu món truyền thống", "goal": "Hướng dẫn công thức", "turns": 7},
    {"topic": "Tập thể dục", "context": "Tập không cần thiết bị", "goal": "Gợi ý bài tập", "turns": 6},
    {"topic": "Du lịch Việt Nam", "context": "Lên kế hoạch du lịch", "goal": "Tư vấn địa điểm", "turns": 8},
    {"topic": "Quản lý tài chính", "context": "Tiết kiệm và đầu tư", "goal": "Hướng dẫn quản lý tiền", "turns": 7},
    {"topic": "Học tiếng Anh", "context": "Cải thiện English", "goal": "Tư vấn phương pháp", "turns": 6},

    {"topic": "Toán học phổ thông", "context": "Giải bài toán", "goal": "Giải thích cách làm", "turns": 5},
    {"topic": "Lịch sử Việt Nam", "context": "Tìm hiểu lịch sử", "goal": "Kể chuyện lịch sử", "turns": 6},
    {"topic": "Khởi nghiệp", "context": "Mở doanh nghiệp", "goal": "Tư vấn khởi nghiệp", "turns": 8},
    {"topic": "Marketing online", "context": "Quảng cáo sản phẩm", "goal": "Chiến lược marketing", "turns": 7},
    {"topic": "Nhiếp ảnh", "context": "Chụp ảnh điện thoại", "goal": "Kỹ thuật chụp ảnh", "turns": 6},
]

BATCH_SIZE = 5  # Sinh 5 conversations mỗi lần


def main():
    print("=" * 70)
    print("🤖 SINH DỮ LIỆU TRAINING BẰNG CLAUDE CODE")
    print("=" * 70)
    print()
    print("📌 Hướng dẫn:")
    print("   1. Script này sẽ tạo prompts cho từng batch")
    print("   2. Copy prompt và gửi cho Claude Code")
    print("   3. Claude sẽ trả về JSON data")
    print("   4. Copy JSON và paste vào file được chỉ định")
    print("   5. Lặp lại cho các batches tiếp theo")
    print()
    print(f"📊 Tổng scenarios: {len(ALL_SCENARIOS)}")
    print(f"📦 Batch size: {BATCH_SIZE}")
    print(f"🔢 Số batches: {(len(ALL_SCENARIOS) + BATCH_SIZE - 1) // BATCH_SIZE}")
    print()

    choice = input("Bắt đầu? (y/n): ").lower()
    if choice != 'y':
        return

    # Chia scenarios thành batches
    batches = [ALL_SCENARIOS[i:i+BATCH_SIZE] for i in range(0, len(ALL_SCENARIOS), BATCH_SIZE)]

    print(f"\n🚀 Bắt đầu sinh {len(batches)} batches...")
    print()

    for i, batch_scenarios in enumerate(batches, 1):
        print("=" * 70)
        print(f"📦 BATCH #{i}/{len(batches)}")
        print("=" * 70)
        print()

        # Tạo prompt
        prompt = create_prompt_for_claude(batch_scenarios, i)

        print("📋 COPY PROMPT SAU ĐÂY VÀ GỬI CHO CLAUDE CODE:")
        print("-" * 70)
        print(prompt)
        print("-" * 70)
        print()
        print("⏳ Đợi Claude trả về JSON, sau đó:")
        print(f"   1. Copy toàn bộ JSON array (bắt đầu từ [ đến ])")
        print(f"   2. Lưu vào file: training_data/temp_batch_{i}.json")
        print()

        input(f"Nhấn Enter khi đã lưu xong batch #{i}...")

        # Đọc và validate
        temp_file = Path(f"training_data/temp_batch_{i}.json")
        if temp_file.exists():
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Add IDs
                for conv in data:
                    conv['id'] = f"conv_claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                    conv['timestamp'] = datetime.now().isoformat()
                    conv['source'] = "claude_code"

                # Save as permanent batch
                save_batch(data, i)

                # Delete temp file
                temp_file.unlink()

                print(f"✅ Batch #{i} hoàn thành: {len(data)} conversations")
                print()

            except Exception as e:
                print(f"❌ Lỗi đọc batch #{i}: {e}")
                print("   Vui lòng thử lại!")
        else:
            print(f"⚠️ Không tìm thấy file temp_batch_{i}.json")
            print("   Bỏ qua batch này...")

        print()

    print("=" * 70)
    print("🎉 ĐÃ XONG TẤT CẢ BATCHES!")
    print("=" * 70)
    print()

    # Merge all batches
    merge = input("Gộp tất cả batches thành 1 file? (y/n): ").lower()
    if merge == 'y':
        merge_all_batches()

    print()
    print("✅ HOÀN THÀNH!")
    print("📁 Kiểm tra thư mục training_data/ để xem kết quả")
    print()


if __name__ == "__main__":
    main()
