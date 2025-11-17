#!/usr/bin/env python3
"""
Data Analyzer - Phân tích dữ liệu training đã sinh
Giúp đánh giá chất lượng và phân bố dữ liệu
"""

import json
import sys
from pathlib import Path
from collections import Counter
import statistics


def load_data(filepath):
    """Load data từ JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        if filepath.endswith('.jsonl'):
            # JSONL format
            data = []
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
            return data
        else:
            # JSON format
            return json.load(f)


def analyze_conversations(data):
    """Phân tích chi tiết dữ liệu conversations"""

    if not data:
        print("Không có dữ liệu để phân tích!")
        return

    print("=" * 70)
    print("📊 PHÂN TÍCH DỮ LIỆU TRAINING")
    print("=" * 70)
    print()

    # Basic stats
    total_convs = len(data)
    print(f"📈 Thống kê cơ bản:")
    print(f"  • Tổng số conversations: {total_convs}")

    # Turns analysis
    turns_counts = [len(conv.get('conversation', [])) for conv in data]
    if turns_counts:
        print(f"  • Tổng số turns: {sum(turns_counts)}")
        print(f"  • Trung bình turns/conv: {statistics.mean(turns_counts):.2f}")
        print(f"  • Min turns: {min(turns_counts)}")
        print(f"  • Max turns: {max(turns_counts)}")
        print(f"  • Median turns: {statistics.median(turns_counts)}")
    print()

    # Length analysis
    print(f"📏 Phân tích độ dài:")
    all_lengths = []
    user_lengths = []
    assistant_lengths = []

    for conv in data:
        for turn in conv.get('conversation', []):
            length = len(turn.get('content', ''))
            all_lengths.append(length)

            if turn.get('role') == 'user':
                user_lengths.append(length)
            elif turn.get('role') == 'assistant':
                assistant_lengths.append(length)

    if all_lengths:
        print(f"  • Trung bình ký tự/turn: {statistics.mean(all_lengths):.0f}")
        print(f"  • Min: {min(all_lengths)} ký tự")
        print(f"  • Max: {max(all_lengths)} ký tự")

    if user_lengths and assistant_lengths:
        print(f"  • TB User messages: {statistics.mean(user_lengths):.0f} ký tự")
        print(f"  • TB Assistant messages: {statistics.mean(assistant_lengths):.0f} ký tự")
    print()

    # Topics distribution
    print(f"📚 Phân bố theo chủ đề:")
    topics = []
    for conv in data:
        topic = conv.get('scenario', {}).get('topic', 'Unknown')
        topics.append(topic)

    topic_counts = Counter(topics)
    for topic, count in topic_counts.most_common(15):
        percentage = (count / total_convs) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {topic[:40]:40} {count:3} ({percentage:5.1f}%) {bar}")
    print()

    # Categories (if available)
    categories = []
    for conv in data:
        cat = conv.get('scenario', {}).get('category') or conv.get('metadata', {}).get('category')
        if cat:
            categories.append(cat)

    if categories:
        print(f"🏷️  Phân bố theo category:")
        cat_counts = Counter(categories)
        for cat, count in cat_counts.most_common():
            percentage = (count / len(categories)) * 100
            print(f"  {cat:20} {count:3} ({percentage:5.1f}%)")
        print()

    # Difficulty (if available)
    difficulties = []
    for conv in data:
        diff = conv.get('metadata', {}).get('difficulty')
        if diff:
            difficulties.append(diff)

    if difficulties:
        print(f"⭐ Phân bố độ khó:")
        diff_counts = Counter(difficulties)
        for diff, count in diff_counts.most_common():
            percentage = (count / len(difficulties)) * 100
            print(f"  {diff:10} {count:3} ({percentage:5.1f}%)")
        print()

    # Language distribution
    languages = []
    for conv in data:
        lang = conv.get('metadata', {}).get('language', 'unknown')
        languages.append(lang)

    if languages:
        print(f"🌐 Ngôn ngữ:")
        lang_counts = Counter(languages)
        for lang, count in lang_counts.most_common():
            percentage = (count / total_convs) * 100
            print(f"  {lang:10} {count:3} ({percentage:5.1f}%)")
        print()

    # Source models
    sources = []
    for conv in data:
        source = conv.get('source', 'unknown')
        sources.append(source)

    if sources:
        print(f"🤖 Models sử dụng:")
        source_counts = Counter(sources)
        for source, count in source_counts.most_common():
            percentage = (count / total_convs) * 100
            print(f"  {source:30} {count:3} ({percentage:5.1f}%)")
        print()

    # Quality metrics
    print(f"✅ Chất lượng:")

    # Check for very short responses
    short_responses = sum(1 for length in all_lengths if length < 20)
    if all_lengths:
        print(f"  • Responses quá ngắn (<20 chars): {short_responses} ({short_responses/len(all_lengths)*100:.1f}%)")

    # Check for very long responses
    long_responses = sum(1 for length in all_lengths if length > 1000)
    if all_lengths:
        print(f"  • Responses quá dài (>1000 chars): {long_responses} ({long_responses/len(all_lengths)*100:.1f}%)")

    # Check for conversations with odd number of turns (might be incomplete)
    odd_turns = sum(1 for count in turns_counts if count % 2 != 0)
    print(f"  • Conversations với lượt lẻ: {odd_turns} ({odd_turns/total_convs*100:.1f}%)")

    print()

    # Recommendations
    print("=" * 70)
    print("💡 KHUYẾN NGHỊ")
    print("=" * 70)

    issues = []

    if statistics.mean(turns_counts) < 4:
        issues.append("⚠️  Conversations hơi ngắn. Tăng DEFAULT_TURNS trong config.py")

    if short_responses > len(all_lengths) * 0.1:  # >10% responses ngắn
        issues.append("⚠️  Nhiều responses quá ngắn. Tăng MIN_RESPONSE_LENGTH")

    if len(topic_counts) < 5:
        issues.append("⚠️  Thiếu đa dạng chủ đề. Thêm scenarios mới")

    if len(set(topics)) < total_convs * 0.3:  # <30% unique topics
        issues.append("⚠️  Nhiều chủ đề bị duplicate. Thêm scenarios đa dạng hơn")

    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  ✅ Dữ liệu có chất lượng tốt!")
        print("  ✅ Phân bố đa dạng và cân bằng!")

    print()
    print("=" * 70)


def main():
    """Main function"""

    if len(sys.argv) < 2:
        # Tự động tìm file mới nhất trong training_data/
        data_dir = Path("training_data")
        if not data_dir.exists():
            print("❌ Thư mục training_data không tồn tại!")
            print()
            print("Sử dụng: python analyze_data.py <path_to_json_file>")
            return

        # Tìm file .json mới nhất
        json_files = list(data_dir.glob("*.json"))
        if not json_files:
            print("❌ Không tìm thấy file JSON nào trong training_data/")
            print()
            print("Sử dụng: python analyze_data.py <path_to_json_file>")
            return

        # Sắp xếp theo thời gian, lấy file mới nhất
        filepath = max(json_files, key=lambda p: p.stat().st_mtime)
        print(f"📂 Tự động phát hiện file: {filepath}")
        print()

    else:
        filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"❌ File không tồn tại: {filepath}")
        return

    # Load and analyze
    try:
        print(f"📖 Đang đọc file: {filepath}")
        print()
        data = load_data(filepath)
        analyze_conversations(data)

    except Exception as e:
        print(f"❌ Lỗi khi phân tích: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
