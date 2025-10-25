# Fix: Embedding Dimension Mismatch Error

## ❌ Lỗi

```python
AssertionError: Embedding dim mismatch, expected: 1024, but loaded: 1536
```

## 🔍 Giải thích

### Lỗi này xảy ra khi:

Bạn đã có **dữ liệu cũ** trong vector database được tạo bởi một embedding model với dimension khác, và bây giờ đang cố gắng load với model mới có dimension khác.

**Ví dụ:**
- **Trước đây**: Dùng OpenAI `text-embedding-3-large` → 1536 dimensions
- **Bây giờ**: Chuyển sang `AITeamVN/Vietnamese_Embedding` → 1024 dimensions
- **Kết quả**: ❌ Conflict!

### Tại sao không thể mix dimensions?

Vector database lưu trữ embeddings như vectors trong không gian nhiều chiều. Nếu dimensions khác nhau:
- **1536-dim vector**: [0.1, 0.2, ..., 0.5] (1536 số)
- **1024-dim vector**: [0.3, 0.4, ..., 0.8] (1024 số)

→ **Không thể so sánh hoặc tìm kiếm giữa chúng!**

## ✅ Giải pháp

### Cách 1: Xóa dữ liệu cũ và bắt đầu lại (RECOMMENDED)

#### Automatic (Dùng script):
```bash
python3 fix_embedding_dimension_mismatch.py
```

Script sẽ:
1. ✅ Kiểm tra dimension hiện tại
2. ✅ Backup dữ liệu cũ tự động
3. ✅ Xóa dữ liệu cũ
4. ✅ Sẵn sàng cho Vietnamese_Embedding

#### Manual:
```bash
# Backup dữ liệu cũ
mv ./rag_storage ./rag_storage_backup_$(date +%Y%m%d_%H%M%S)

# Hoặc xóa luôn nếu không cần
rm -rf ./rag_storage

# Start server - sẽ tạo database mới với 1024 dim
lightrag-server
```

### Cách 2: Quay lại dùng model cũ

Nếu bạn muốn giữ dữ liệu cũ, update `.env` để dùng lại model gốc:

```env
# Nếu dữ liệu cũ là 1536 dim (OpenAI)
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=1536
EMBEDDING_BINDING_API_KEY=your_openai_key
```

### Cách 3: Migrate dữ liệu (Advanced)

Nếu bạn muốn convert dữ liệu cũ sang Vietnamese_Embedding:

```python
# 1. Export documents từ database cũ
# 2. Xóa database cũ
# 3. Re-insert documents với Vietnamese_Embedding
# 4. Database mới sẽ có 1024 dim

# Script example (simplified):
from lightrag import LightRAG

# Load old documents
old_rag = LightRAG(working_dir="./rag_storage_old")
documents = old_rag.export_documents()  # hypothetical

# Clean and reinit
rm -rf ./rag_storage

# Insert with new embedding
new_rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=vietnamese_embedding_func
)
for doc in documents:
    new_rag.insert(doc)
```

## 🚂 Railway Deployment Fix

Nếu lỗi này xảy ra trên Railway:

### Option 1: Clean Start (Recommended)

```bash
# Railway Dashboard → Variables → Add
FORCE_CLEAN_START=true

# Hoặc trong code startup
if os.getenv("FORCE_CLEAN_START") == "true":
    shutil.rmtree(working_dir, ignore_errors=True)
    os.environ.pop("FORCE_CLEAN_START")  # Remove after first run
```

### Option 2: Use Different Working Directory

```env
# Railway Variables
WORKING_DIR=/app/rag_storage_vietnamese

# Mỗi embedding model dùng một directory riêng
```

### Option 3: Use Railway Volumes (Persistent Storage)

```json
// railway.json
{
  "deploy": {
    "volumeMounts": [
      {
        "mountPath": "/app/rag_storage",
        "volumeName": "storage"
      }
    ]
  }
}
```

Nếu cần reset:
```bash
# Railway Dashboard → Volume → Delete → Create new
```

## 🔍 Kiểm tra trước khi start

```bash
# Check vector database files
ls -lh ./rag_storage/vdb_*.json

# Check dimension trong file
python3 -c "
import json
with open('./rag_storage/vdb_entities.json', 'r') as f:
    data = json.load(f)
    print(f'Current dimension: {data.get(\"embedding_dim\")}')
"
```

## 📊 Dimension của các models phổ biến

| Model | Dimension | Provider |
|-------|-----------|----------|
| text-embedding-3-large | 3072 | OpenAI |
| text-embedding-3-small | 1536 | OpenAI |
| text-embedding-ada-002 | 1536 | OpenAI |
| **AITeamVN/Vietnamese_Embedding** | **1024** | **HuggingFace** |
| bge-m3 | 1024 | Ollama |
| nomic-embed-text | 768 | Ollama |
| jina-embeddings-v4 | 2048 | Jina AI |

## ⚠️ Ngăn ngừa lỗi này

### 1. Document embedding model trong project
```
# README.md hoặc docs/
Current embedding model: AITeamVN/Vietnamese_Embedding (1024 dim)
Do not change without rebuilding database!
```

### 2. Add validation trong code
```python
# lightrag_server.py startup
def validate_embedding_dimension():
    vdb_file = Path(working_dir) / "vdb_entities.json"
    if vdb_file.exists():
        with open(vdb_file) as f:
            data = json.load(f)
            stored_dim = data.get('embedding_dim')
            if stored_dim != args.embedding_dim:
                raise ValueError(
                    f"Dimension mismatch! "
                    f"Database has {stored_dim}, "
                    f"but config expects {args.embedding_dim}. "
                    f"See fix_embedding_dimension_mismatch.py"
                )
```

### 3. Separate storage per model
```python
# Use model name in working directory
working_dir = f"./rag_storage_{embedding_model.replace('/', '_')}"
```

## 📝 Checklist khi chuyển embedding model

- [ ] Backup dữ liệu cũ
- [ ] Update `.env` với EMBEDDING_BINDING mới
- [ ] Update EMBEDDING_MODEL mới
- [ ] Update EMBEDDING_DIM mới (quan trọng!)
- [ ] Xóa hoặc move working directory cũ
- [ ] Test với dữ liệu nhỏ trước
- [ ] Re-insert tất cả documents
- [ ] Verify queries hoạt động đúng

## 🎯 Tóm tắt

**Lỗi:** Embedding dimension mismatch (1024 vs 1536)

**Nguyên nhân:** Đổi embedding model nhưng giữ database cũ

**Giải pháp nhanh:**
```bash
# Backup và clean
mv ./rag_storage ./rag_storage_backup
lightrag-server  # Start fresh with Vietnamese_Embedding
```

**Script tự động:**
```bash
python3 fix_embedding_dimension_mismatch.py
```

**Quan trọng:** 
- ⚠️ Không thể mix dimensions khác nhau
- ✅ Phải rebuild database khi đổi model
- 💾 Luôn backup trước khi xóa
- 📋 Document model đang dùng

---

**Liên quan:**
- `VIETNAMESE_SERVER_INTEGRATION.md` - Vietnamese Embedding setup
- `RAILWAY_DEPLOYMENT_FIX.md` - Railway deployment
- `fix_embedding_dimension_mismatch.py` - Automatic fix script
