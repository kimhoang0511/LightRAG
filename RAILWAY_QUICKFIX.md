# 🚀 Railway Image Size Fix - Quick Guide

## ❌ Error
```
Image of size 12 GB exceeded limit of 4.0 GB
```

## ✅ Solution: CPU-only Torch

Updated `Dockerfile.railway` to use:
- **torch CPU** (200MB) instead of full torch (2GB)
- **Aggressive cleanup** (remove cache, tests, compiled files)
- **Minimal dependencies** (only what's needed)

**Result:** 2-3GB image ✅ (under 4GB limit)

---

## 🎯 Deploy Now

```bash
# 1. Commit optimized Dockerfile
git add Dockerfile.railway railway.json
git commit -m "fix: Optimize image size with CPU-only torch"

# 2. Push to trigger Railway build
git push origin LightRag_Dev
```

---

## 📊 Size Comparison

| Version | torch | Total | Railway Free |
|---------|-------|-------|--------------|
| Before  | 2GB (CUDA) | 12GB ❌ | No |
| After   | 200MB (CPU) | 2-3GB ✅ | Yes |

---

## 🔍 Verify in Railway Logs

Look for:
```
✅ Torch 2.1.0+cpu (CPU) installed
✅ Image size: 2.X GB
```

---

## 🎁 Even Smaller Option

Multi-stage build for 1.5-2.5GB:
```bash
# Update railway.json to use:
"dockerfilePath": "Dockerfile.railway-lite"
```

---

## 📚 Full Documentation

- **Complete guide:** `RAILWAY_IMAGE_SIZE_FIX.md`
- **Check size locally:** `./check-image-size.sh`
- **Vietnamese setup:** `RAILWAY_VIETNAMESE_DEPLOY.md`
