# 🪟 Hướng dẫn cài đặt trên Windows

## ✅ Bước 1: Kiểm tra Python

Mở PowerShell và chạy:

```powershell
python --version
```

Cần Python 3.8 trở lên. Nếu chưa có, download tại: https://www.python.org/downloads/

## ✅ Bước 2: Cài đặt dependencies

### Option A: Chỉ train với OpenAI (Đơn giản nhất)

```powershell
pip install --upgrade openai python-dotenv
```

### Option B: Train với GPU Local

```powershell
# Cài PyTorch với CUDA support (nếu có NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Cài Unsloth và dependencies
pip install unsloth transformers datasets bitsandbytes accelerate
```

**⚠️ Lưu ý:** Local GPU training cần:
- NVIDIA GPU (RTX 3060/4060 trở lên với 8GB+ VRAM)
- CUDA toolkit installed
- Nếu không có GPU, dùng Option A (OpenAI) hoặc Google Colab

### Option C: Cài tất cả (Full)

```powershell
pip install -r requirements.txt
```

## ✅ Bước 3: Set API Key (nếu dùng OpenAI)

### Cách 1: Environment Variable (Recommended)

```powershell
# Temporary (chỉ session hiện tại)
$env:OPENAI_API_KEY = "sk-proj-..."

# Permanent (Windows)
setx OPENAI_API_KEY "sk-proj-..."
```

Sau khi set permanent, **đóng và mở lại PowerShell**.

### Cách 2: File .env

Tạo file `.env` trong folder project:

```
OPENAI_API_KEY=sk-proj-...
```

## ✅ Bước 4: Chạy Training

### Train với OpenAI API:

```powershell
python train_openai.py
```

Nếu chưa set API key, script sẽ hỏi bạn nhập.

### Train với GPU Local:

```powershell
python train_local_gpu.py
```

### Test model:

```powershell
# Test local model
python test_personality.py --local

# Test OpenAI model
python test_personality.py --openai
```

## 🐛 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'torch'"

```powershell
pip install torch
```

### Lỗi: "TypeError: Client.__init__() got an unexpected keyword argument 'proxies'"

OpenAI library version conflict. Update:

```powershell
pip install --upgrade openai httpx
```

### Lỗi: "Can't open file ... No such file or directory"

Đảm bảo bạn đang ở đúng folder:

```powershell
cd C:\Users\gau\Documents\gaucandy-ai\Botchatlocal
python train_openai.py
```

### Lỗi: GPU out of memory

Sửa `train_local_gpu.py`, giảm batch size xuống 1.

### Lỗi: CUDA not available

```powershell
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

Nếu False:
1. Cài NVIDIA CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Hoặc dùng OpenAI training thay vì local GPU

### Lỗi: "The term 'train_openai.py' is not recognized"

PowerShell cần `python` ở đầu:

```powershell
# ❌ Sai
train_openai.py

# ✅ Đúng
python train_openai.py
```

## 📋 Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install openai python-dotenv`)
- [ ] OpenAI API key set (nếu dùng OpenAI training)
- [ ] Ở đúng folder project (`cd Botchatlocal`)
- [ ] Run script: `python train_openai.py` hoặc `python train_local_gpu.py`

## 💡 Tips

1. **Dùng PowerShell**, không phải CMD
2. **Luôn thêm `python`** trước tên file (ví dụ: `python train_openai.py`)
3. **Check version:** `pip list | Select-String openai`
4. **Update pip:** `python -m pip install --upgrade pip`

---

**Need help?** Xem [README.md](README.md) hoặc [HOW_TO_USE.md](HOW_TO_USE.md)
