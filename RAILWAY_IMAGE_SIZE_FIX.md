# Fix Railway Image Size Limit Error

## ❌ Problem
```
Image of size 12 GB exceeded limit of 4.0 GB.
Upgrade your plan to increase the image size limit.
```

## 🔍 Root Cause
- **torch full version**: ~2GB (includes CUDA)
- **transformers + models**: ~1GB
- **Dependencies**: ~1GB
- **Build cache**: ~2GB
- **Python + system**: ~1GB
- **Multiple layers**: Adds up quickly
- **Total**: ~12GB ❌

## ✅ Solution: Optimize Docker Image

### Option 1: CPU-only torch (Recommended) ⭐

**File**: `Dockerfile.railway`

**Key optimizations:**
```dockerfile
# 1. Use CPU-only torch (200MB vs 2GB)
torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# 2. Minimal system packages
apt-get install --no-install-recommends

# 3. Aggressive cleanup
pip cache purge
find . -name "__pycache__" -exec rm -rf {} +
rm -rf tests/ *.pyc *.pyo
```

**Expected size**: ~2-3GB ✅

### Option 2: Multi-stage build (Most aggressive)

**File**: `Dockerfile.railway-lite`

**How it works:**
```dockerfile
# Stage 1: Build - install everything
FROM python:3.10-slim AS builder
RUN pip install torch transformers lightrag[api]

# Stage 2: Runtime - copy only what's needed
FROM python:3.10-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/
```

**Benefits:**
- Build artifacts not included in final image
- No build tools in final image
- Minimal runtime dependencies

**Expected size**: ~1.5-2.5GB ✅

### Option 3: Use requirements.txt with pinned versions

Create optimized requirements for Railway:

```txt
# requirements-railway-lite.txt
torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
transformers==4.35.0
sentencepiece==0.1.99
# ... other minimal deps
```

Then:
```dockerfile
RUN pip install --no-cache-dir -r requirements-railway-lite.txt
```

## 📊 Size Comparison

| Approach | Torch | Total Size | Railway Free |
|----------|-------|------------|--------------|
| Original (CUDA) | 2GB | 12GB ❌ | No |
| CPU-only | 200MB | 2-3GB ✅ | Yes |
| Multi-stage | 200MB | 1.5-2.5GB ✅ | Yes |
| Minimal deps | 200MB | 1-2GB ✅ | Yes |

## 🚀 Implementation Steps

### Step 1: Update railway.json

**Option A: Use optimized Dockerfile** (Recommended)
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway"
  }
}
```

**Option B: Use ultra-lite multi-stage**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway-lite"
  }
}
```

### Step 2: Commit and push

```bash
git add Dockerfile.railway railway.json
git commit -m "fix: Optimize Docker image size for Railway (<4GB)"
git push origin LightRag_Dev
```

### Step 3: Monitor build

Railway logs should show:
```
✅ Torch 2.1.0+cpu (CPU) installed
Image size: 2.1 GB (under 4GB limit) ✅
```

## 🔍 Verification Commands

### Check image size locally (if Docker available)
```bash
docker build -f Dockerfile.railway -t test .
docker images test
# Should show <4GB
```

### Check layer sizes
```bash
docker history test --format "{{.Size}}\t{{.CreatedBy}}" | head -20
```

### Identify large files in image
```bash
docker run --rm test du -sh /usr/local/lib/python3.10/site-packages/* | sort -h | tail -20
```

## 💡 Additional Optimizations

### 1. Remove unnecessary packages
```dockerfile
# Before
RUN pip install torch>=2.0.0 transformers>=4.30.0

# After - explicit CPU and minimal transformers
RUN pip install torch==2.1.0+cpu transformers==4.35.0 --no-deps
RUN pip install tokenizers sentencepiece  # Only what's needed
```

### 2. Use .dockerignore
```
# .dockerignore
*.pyc
__pycache__/
tests/
*.md
docs/
examples/
.git/
```

### 3. Combine RUN commands
```dockerfile
# Before (multiple layers)
RUN pip install torch
RUN pip install transformers
RUN pip install lightrag

# After (one layer)
RUN pip install torch transformers && \
    pip install lightrag && \
    pip cache purge
```

### 4. Remove build dependencies after use
```dockerfile
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install package && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

## 🎯 Target Sizes by Component

| Component | Size |
|-----------|------|
| Base image (python:3.10-slim) | ~150MB |
| torch (CPU-only) | ~200MB |
| transformers | ~100MB |
| LightRAG + dependencies | ~200MB |
| System packages | ~50MB |
| **Total Target** | **~700MB-2GB** |

## ⚠️ Trade-offs

### CPU-only torch
**Pros:**
- ✅ Much smaller (~200MB vs 2GB)
- ✅ Faster downloads
- ✅ Still works for embeddings

**Cons:**
- ⚠️ No GPU acceleration (but Railway doesn't have GPUs anyway)
- ⚠️ Slightly slower inference (acceptable for embeddings)

### Multi-stage build
**Pros:**
- ✅ Smallest final image
- ✅ Clean runtime environment
- ✅ No build artifacts

**Cons:**
- ⚠️ Longer build time
- ⚠️ More complex Dockerfile
- ⚠️ Harder to debug

## 🐛 Troubleshooting

### Image still too large?

**Check what's taking space:**
```bash
# In Railway build logs, add:
RUN du -sh /usr/local/lib/python3.10/site-packages/* | sort -h | tail -10
```

**Common culprits:**
- Old pip cache: `pip cache purge`
- Test files: `find . -name tests -type d -exec rm -rf {} +`
- Compiled files: `find . -name "*.pyc" -delete`
- Documentation: `rm -rf /usr/local/share/doc/*`

### torch CPU version not found?

Make sure you use the correct index:
```dockerfile
RUN pip install torch==2.1.0+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html
```

### Multi-stage build fails?

Check COPY paths:
```dockerfile
# Make sure paths exist in builder stage
COPY --from=builder /build/lightrag /app/lightrag
```

## 📈 Success Metrics

Build is successful when:
- ✅ Image size < 4GB (Railway free tier)
- ✅ Build completes without OOM
- ✅ Torch imports successfully
- ✅ Transformers works
- ✅ Vietnamese embedding functional
- ✅ API responds to queries

## 🔗 Related Files

- `Dockerfile.railway` - Optimized single-stage (2-3GB)
- `Dockerfile.railway-lite` - Ultra-lite multi-stage (1.5-2.5GB)
- `railway.json` - Railway configuration
- `.dockerignore` - Exclude unnecessary files

## 📚 References

- [PyTorch CPU-only builds](https://pytorch.org/get-started/locally/)
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Railway image size limits](https://docs.railway.app/reference/pricing)
