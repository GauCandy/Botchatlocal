# Generators - Helper Scripts

Folder này chứa các scripts phụ để tạo thêm training data. **KHÔNG CẦN THIẾT** cho việc training AI.

## Files trong folder:

- `generate_gaukeo_data.py` - Tạo file JSON từ code (đơn giản hoá - 2 examples)
- `training_data_generator.py` - Generator chung (đơn giản hoá - 2 scenarios)
- `advanced_generator.py` - Generator nâng cao với nhiều options
- `generate_with_claude.py` - Generate data bằng Claude API
- `generate.py`, `quickstart.py` - Các tools khác
- `analyze_data.py` - Phân tích training data
- `config.py` - Config cho generators

## Khi nào dùng:

Chỉ dùng khi bạn muốn **tạo thêm** training data. Nếu chỉ muốn train với data hiện có, dùng 3 files ở root:
- `train_local_gpu.py` - Train với GPU local
- `train_openai.py` - Train với OpenAI API
- `test_personality.py` - Test model đã train

## Xoá được không?

Có! Nếu không cần generate thêm data thì có thể xoá hết folder này.
