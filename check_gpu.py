#!/usr/bin/env python3
"""
🔍 Check GPU và PyTorch CUDA support
Chạy script này để kiểm tra GPU có hoạt động không
"""

import sys

print("=" * 60)
print("🔍 GPU & CUDA DIAGNOSTIC")
print("=" * 60)
print()

# 1. Check PyTorch
print("1️⃣  Checking PyTorch...")
try:
    import torch
    print(f"   ✓ PyTorch installed: {torch.__version__}")
except ImportError:
    print("   ❌ PyTorch chưa cài!")
    print()
    print("   Cài PyTorch với CUDA:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)

print()

# 2. Check CUDA availability
print("2️⃣  Checking CUDA...")
if torch.cuda.is_available():
    print(f"   ✅ CUDA available: {torch.version.cuda}")
    print()
    print("3️⃣  GPU Information:")
    print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print(f"   Compute Capability: {torch.cuda.get_device_capability(0)}")
    print()
    print("=" * 60)
    print("🎉 GPU SẴN SÀNG! Bạn có thể train local.")
    print("=" * 60)
    print()
    print("Chạy: python train_local_gpu.py")
else:
    print("   ❌ CUDA not available!")
    print()
    print("3️⃣  Possible reasons:")
    print("   - PyTorch CPU-only version (most common)")
    print("   - NVIDIA drivers not installed")
    print("   - CUDA toolkit not installed")
    print()

    # Check if PyTorch is CPU only
    if '+cpu' in torch.__version__ or 'cpu' in torch.__version__:
        print("   ⚠️  DETECTED: PyTorch CPU-only version")
        print()
        print("   FIX: Cài PyTorch với CUDA support")
        print()
        print("   Step 1: Uninstall current PyTorch")
        print("   pip uninstall torch torchvision torchaudio -y")
        print()
        print("   Step 2: Install PyTorch with CUDA 12.1 (cho RTX 3050)")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print()
        print("   Step 3: Chạy lại script này để verify")
        print("   python check_gpu.py")
    else:
        print("   ⚠️  PyTorch có CUDA support nhưng không detect GPU")
        print()
        print("   Check:")
        print("   1. NVIDIA drivers updated: https://www.nvidia.com/download/index.aspx")
        print("   2. GPU trong Device Manager (Windows)")
        print("   3. Chạy: nvidia-smi")
        print()
        print("   Nếu nvidia-smi không work, cài NVIDIA drivers mới")

    print()
    print("=" * 60)
    print("💡 TIP: Nếu không fix được GPU, dùng OpenAI training:")
    print("   python train_openai.py")
    print("=" * 60)
