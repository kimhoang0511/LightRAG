# Railway Deployment với Vietnamese Embedding

## 🚨 Vấn đề đã fix

**Error trước đây:**
```
ImportError: No module named 'torch'
```

**Nguyên nhân:**
- Railway dùng Python 3.12 thay vì 3.10 như cấu hình
- Nixpacks không cài đặt torch đáng tin cậy
- Build command không được thực thi đúng cách

**Giải pháp:**
- ✅ Chuyển từ Nixpacks sang **Dockerfile**
- ✅ Cài torch và transformers trong layer riêng
- ✅ Verify installation trước khi build tiếp
- ✅ Python 3.10 cố định

---

## 🚀 Deployment Steps

### Option 1: Automatic (Recommended)

```bash
./deploy-railway.sh
```

Script sẽ:
- ✅ Kiểm tra files cần thiết
- ✅ Commit changes (nếu cần)
- ✅ Push to git
- ✅ Deploy lên Railway

### Option 2: Manual

```bash
# 1. Commit changes
git add Dockerfile.railway railway.json
git commit -m "fix: Railway deployment with Dockerfile for torch"
git push origin main

# 2. Railway tự động detect và build
# Monitor tại: https://railway.app/dashboard
```

---

## 📋 Files đã tạo/sửa

### Dockerfile.railway (MỚI)
```dockerfile
FROM python:3.10-slim-bullseye

# Install torch FIRST (separate layer)
RUN pip install torch>=2.0.0 transformers>=4.30.0

# Then install LightRAG
RUN pip install -e .[api]

# Verify installation
RUN python -c "import torch; print('✅ Torch installed')"
```

**Lợi ích:**
- ✅ Cài torch trong layer riêng → cache tốt hơn
- ✅ Verify trước khi build tiếp → fail fast
- ✅ Python 3.10 cố định → không bị version mismatch

### railway.json (ĐÃ SỬA)
```json
{
  "build": {
    "builder": "DOCKERFILE",  // Thay đổi từ NIXPACKS
    "dockerfilePath": "Dockerfile.railway"
  }
}
```

### vietnamese_embed.py (ĐÃ THÊM DEBUG)
- In detailed logs khi import torch
- Hiển thị Python version, sys.path
- List installed packages
- Giúp debug nếu vẫn có lỗi

---

## 🔍 Monitoring Build Logs

Trong Railway build logs, bạn sẽ thấy:

### ✅ Build thành công
```
🔧 Installing PyTorch and Transformers...
✅ PyTorch and Transformers installed
✅ Torch 2.x.x installed successfully
✅ Transformers installed successfully
✅ Vietnamese embedding module loaded
✅ All verifications passed
```

### ❌ Build thất bại
Nếu vẫn gặp lỗi:
1. Check Railway logs xem step nào fail
2. Share full logs để tôi debug
3. Có thể cần tăng Railway resources

---

## 🧪 Verification sau khi deploy

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Expected: `200 OK`

### 2. Check Vietnamese Embedding
```bash
curl -X POST https://your-app.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Xin chào thế giới",
    "mode": "hybrid"
  }'
```

Expected: Response với embeddings được tạo

### 3. Check Server Logs
Trong Railway logs, tìm:
```
✅ ALL IMPORTS SUCCESSFUL - Vietnamese Embedding Ready!
```

---

## ⚙️ Configuration

Đảm bảo Railway environment variables:

```env
EMBEDDING_BINDING=vietnamese
EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding
EMBEDDING_DIM=1024
HUGGINGFACE_API_KEY=hf_xxx...
```

**Lưu ý:** 
- HuggingFace API key cần có quyền đọc model
- Model sẽ được download lần đầu (~400MB)
- Lần sau sẽ dùng cache

---

## 🐛 Troubleshooting

### Vẫn thấy "No module named 'torch'"

**Check:**
1. Railway có dùng `Dockerfile.railway` không?
   - Vào Settings → Build → Builder = DOCKERFILE
   
2. Build logs có show verification steps không?
   - Tìm "✅ Torch ... installed successfully"
   
3. Python version có đúng 3.10 không?
   - Check logs: "Python 3.10.x"

**Fix:**
```bash
# Force rebuild without cache
# In Railway dashboard:
# Deployments → Latest → ... → Rebuild (without cache)
```

### Build timeout

Torch rất nặng (~2GB), build lần đầu có thể lâu.

**Fix:**
- Đợi thêm (có thể 10-15 phút)
- Nếu timeout, rebuild sẽ dùng cache nhanh hơn

### Out of memory

Railway free tier có thể không đủ RAM để build torch.

**Fix:**
- Upgrade Railway plan
- Hoặc dùng pre-built torch wheels

---

## 📚 Related Documentation

- [RAILWAY_DEPLOYMENT_FIX_TORCH.md](./RAILWAY_DEPLOYMENT_FIX_TORCH.md) - Chi tiết technical
- [VIETNAMESE_SERVER_INTEGRATION.md](./VIETNAMESE_SERVER_INTEGRATION.md) - Vietnamese embedding setup
- [Dockerfile.railway](./Dockerfile.railway) - Railway Dockerfile

---

## 🎯 Success Criteria

Deploy thành công khi:
- ✅ Build hoàn tất không lỗi
- ✅ Server khởi động được
- ✅ Health check pass
- ✅ Vietnamese embedding hoạt động
- ✅ Không có torch import errors
- ✅ Query Vietnamese text được kết quả

---

## 💡 Next Steps

Sau khi deploy thành công:

1. **Test thoroughly** với Vietnamese text
2. **Monitor logs** trong vài ngày đầu
3. **Document** bất kỳ issues nào
4. **Optimize** nếu cần (model caching, batch size, etc.)

---

## 📞 Support

Nếu vẫn gặp vấn đề:
1. Share **full Railway build logs**
2. Share **server startup logs** 
3. Check file `RAILWAY_DEPLOYMENT_FIX_TORCH.md`

Good luck! 🚀
