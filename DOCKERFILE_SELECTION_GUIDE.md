# Choose the Right Dockerfile for Railway

## 🎯 Quick Decision

| Your Situation | Use This | Expected Size |
|----------------|----------|---------------|
| **Just want it to work** | `Dockerfile.railway` | 3-4GB |
| **Need smallest size** | `Dockerfile.railway-minimal` | 2-2.5GB ⭐ |
| **Maximum optimization** | `Dockerfile.railway-lite` | 1.5-2.5GB |

---

## 📋 Dockerfile Comparison

### 1. Dockerfile.railway (Default)
**Best for:** Most users, stable and reliable

```dockerfile
# Multi-stage build
# CPU-only torch
# Standard cleanup
```

**Size:** ~3-4GB  
**Build time:** ~10 min  
**Stability:** ⭐⭐⭐⭐⭐  
**Pros:**
- ✅ Includes all API dependencies
- ✅ Well-tested and stable
- ✅ Easy to debug

**Cons:**
- ⚠️ May still exceed 4GB limit

**Use in railway.json:**
```json
{
  "build": {
    "dockerfilePath": "Dockerfile.railway"
  }
}
```

---

### 2. Dockerfile.railway-minimal (Recommended) ⭐
**Best for:** Railway free tier (4GB limit)

```dockerfile
# Multi-stage build
# CPU-only torch
# Minimal requirements (requirements-railway-optimized.txt)
# Ultra-aggressive cleanup
```

**Size:** ~2-2.5GB ✅  
**Build time:** ~8 min  
**Stability:** ⭐⭐⭐⭐  
**Pros:**
- ✅ Fits Railway free tier easily
- ✅ Only essential dependencies
- ✅ Faster downloads and deploys
- ✅ Uses optimized requirements file

**Cons:**
- ⚠️ May need to add back some optional features

**Use in railway.json:**
```json
{
  "build": {
    "dockerfilePath": "Dockerfile.railway-minimal"
  }
}
```

---

### 3. Dockerfile.railway-lite (Maximum optimization)
**Best for:** Advanced users, extreme size constraints

```dockerfile
# Multi-stage build
# CPU-only torch
# Manual package selection
# Extreme cleanup
```

**Size:** ~1.5-2.5GB  
**Build time:** ~7 min  
**Stability:** ⭐⭐⭐  
**Pros:**
- ✅ Smallest possible image
- ✅ Very fast deploys
- ✅ Minimal attack surface

**Cons:**
- ⚠️ May break some features
- ⚠️ Harder to debug
- ⚠️ Requires manual dependency management

**Use in railway.json:**
```json
{
  "build": {
    "dockerfilePath": "Dockerfile.railway-lite"
  }
}
```

---

## 🚀 Recommended Setup (For 5.9GB → <3GB)

### Step 1: Switch to minimal Dockerfile

```bash
cd /Users/kimtvh/Documents/repo_git/LightRAG

# Update railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway-minimal"
  },
  "deploy": {
    "startCommand": "lightrag-server",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 3000,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF
```

### Step 2: Commit and push

```bash
git add railway.json \
         Dockerfile.railway \
         Dockerfile.railway-minimal \
         Dockerfile.railway-lite \
         requirements-railway-optimized.txt

git commit -m "fix: Use minimal Dockerfile to reduce image size to <3GB"

git push origin LightRag_Dev
```

### Step 3: Monitor Railway build

Look for:
```
✅ Image size: 2.X GB (under 4GB limit)
```

---

## 🔍 Size Breakdown Comparison

| Component | Standard | Minimal | Lite |
|-----------|----------|---------|------|
| Base image | 150MB | 150MB | 150MB |
| torch | 200MB | 200MB | 200MB |
| transformers | 300MB | 200MB | 150MB |
| LightRAG deps | 800MB | 400MB | 200MB |
| System packages | 200MB | 100MB | 50MB |
| Build artifacts | 1GB | 0MB | 0MB |
| Tests/docs | 500MB | 0MB | 0MB |
| **Total** | **3-4GB** | **2-2.5GB** ✅ | **1.5-2GB** |

---

## 🐛 Troubleshooting

### Image still too large?

**Check what's using space:**

Add this to your Dockerfile before cleanup:
```dockerfile
RUN du -sh /usr/local/lib/python3.10/site-packages/* | sort -h | tail -20
```

**Common culprits:**
1. **torch** (200MB) - Already CPU-only ✓
2. **transformers** (150-300MB) - Can't reduce further
3. **numpy** (50MB) - Required
4. **Other ML libs** - Review if needed

### Missing dependencies after switching?

**Add back to requirements-railway-optimized.txt:**
```txt
# Add any missing packages
your-package==x.x.x
```

### Build fails with "No module named X"?

**Option 1: Add to requirements-railway-optimized.txt**
```txt
X==version
```

**Option 2: Switch back to standard**
```json
{
  "build": {
    "dockerfilePath": "Dockerfile.railway"
  }
}
```

---

## 💡 Additional Optimization Tips

### 1. Remove unused API endpoints

If you don't need all API features, comment them out in `lightrag_server.py`

### 2. Use lighter alternatives

| Heavy | Light | Savings |
|-------|-------|---------|
| pandas | numpy | ~50MB |
| pillow | N/A | ~10MB |
| matplotlib | N/A | ~100MB |

### 3. Pin all versions

This prevents accidental upgrades:
```txt
package==exact.version.number
```

---

## 📊 Success Metrics

Build is successful when:
- [ ] Image size < 4GB (Railway free tier)
- [ ] Build completes in < 15 minutes
- [ ] All imports work (check logs)
- [ ] Server starts successfully
- [ ] Health check passes
- [ ] Vietnamese embedding works

---

## 🎯 TL;DR - Quick Fix

```bash
# Use minimal Dockerfile
echo '{"build":{"builder":"DOCKERFILE","dockerfilePath":"Dockerfile.railway-minimal"}}' > railway.json

# Commit and push
git add railway.json Dockerfile.railway-minimal requirements-railway-optimized.txt
git commit -m "fix: Reduce image size to <3GB"
git push
```

Expected result: **2-2.5GB image** ✅
