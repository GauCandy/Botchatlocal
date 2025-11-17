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

### Option B: Train với GPU Local (RTX 3050/3060/4060+)

**📋 Requirements:**
- NVIDIA GPU: RTX 3050 (6GB), RTX 3060 (8-12GB), RTX 4060+ (8GB+)
- Windows 10/11
- NVIDIA drivers updated

**Step 1: Check GPU**

```powershell
# Check nếu có GPU NVIDIA
nvidia-smi
```

Nếu lỗi "nvidia-smi not found", cài NVIDIA drivers tại: https://www.nvidia.com/download/index.aspx

**Step 2: Cài PyTorch với CUDA 12.1**

```powershell
# Uninstall PyTorch cũ (nếu có)
pip uninstall torch torchvision torchaudio -y

# Cài PyTorch với CUDA 12.1 (recommended cho RTX 30xx/40xx)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Step 3: Verify GPU**

```powershell
# Chạy script check GPU
python check_gpu.py
```

Phải thấy: "✅ CUDA available" và GPU name (RTX 3050/3060/etc.)

**Step 4: Cài Unsloth và dependencies**

```powershell
pip install "unsloth[cu121] @ git+https://github.com/unslothai/unsloth.git"
pip install transformers datasets trl bitsandbytes accelerate
```

**⚠️ Nếu GPU vẫn không work:**
- Dùng OpenAI training (Option A)
- Hoặc Google Colab miễn phí: https://colab.research.google.com/

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
