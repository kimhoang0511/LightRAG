# Railway Deployment Fix Documentation

## Problem
Railway deployment fails with "No module named 'torch'" error despite torch being listed in:
- pyproject.toml [api] dependencies
- requirements-railway.txt
- nixpacks.toml install commands

## Root Cause Analysis

### Issue 1: Python Version Mismatch
- `nixpacks.toml` specified Python 3.10
- Railway actually used Python 3.12 (detected from error: `/app/.venv/lib/python3.12/`)
- Nixpacks configuration was being ignored

### Issue 2: Dependency Installation
- Railway's Nixpacks builder may not properly install heavy dependencies like torch
- The build process doesn't guarantee torch installation even when specified
- Virtual environment caching issues may prevent fresh installations

### Issue 3: Build System Unreliability
- Nixpacks is not deterministic for complex Python projects
- Build commands in railway.json may be executed in unexpected order
- Optional dependencies like `[api]` may not be resolved correctly

## Solution

### Switch from Nixpacks to Dockerfile

Created `Dockerfile.railway` with explicit, controlled build steps:

```dockerfile
FROM python:3.10-slim-bullseye

# System dependencies
RUN apt-get update && apt-get install -y build-essential git curl

# Install torch FIRST (separate layer for caching)
RUN pip install torch>=2.0.0 transformers>=4.30.0

# Then install LightRAG
RUN pip install -e .[api]

# Verify installation
RUN python -c "import torch; print('✅ Torch installed')"
```

**Key improvements:**
1. ✅ **Explicit Python version**: Uses Python 3.10 (not 3.12)
2. ✅ **Guaranteed torch installation**: Separate pip install step
3. ✅ **Verification step**: Build fails early if torch not installed
4. ✅ **Better caching**: Torch layer cached separately from app code
5. ✅ **Deterministic**: Same result every deployment

### Railway Configuration Update

Updated `railway.json`:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway"
  }
}
```

## Deployment Steps

1. **Commit changes:**
   ```bash
   git add Dockerfile.railway railway.json
   git commit -m "fix: Use Dockerfile for Railway deployment to ensure torch installation"
   git push origin main
   ```

2. **Railway will:**
   - Detect Dockerfile.railway
   - Build using Docker (not Nixpacks)
   - Install torch in separate layer
   - Verify torch before proceeding
   - Cache torch layer for faster rebuilds

3. **Verify deployment:**
   - Check Railway build logs for "✅ Torch ... installed successfully"
   - Server should start without "No module named 'torch'" error
   - Vietnamese embedding endpoint should be accessible

## Alternative Solutions (Not Recommended)

### Option A: Force Nixpacks Rebuild
```bash
# Clear Railway cache (in Railway dashboard)
# Settings -> Reset Build Cache
```
**Why not:** Still unreliable, doesn't solve root cause

### Option B: Use requirements.txt instead of pyproject.toml
```json
{
  "build": {
    "buildCommand": "pip install -r requirements-railway.txt"
  }
}
```
**Why not:** Loses benefits of pyproject.toml optional dependencies

### Option C: Pre-install torch in Railway environment
```bash
# Add to Railway environment variables
RAILWAY_RUN_BUILD_COMMAND=pip install torch>=2.0.0 && pip install -e .[api]
```
**Why not:** Environment variable commands are less reliable than Dockerfile

## Verification Checklist

After deployment, verify:
- [ ] Build logs show torch installation
- [ ] Build logs show verification step passed
- [ ] Server starts without import errors
- [ ] `/health` endpoint returns 200
- [ ] Vietnamese embedding can be selected
- [ ] Test query with Vietnamese text works

## Monitoring

Watch for these in Railway logs:
- ✅ `"✅ Torch ... installed successfully"` during build
- ✅ `"✅ ALL IMPORTS SUCCESSFUL - Vietnamese Embedding Ready!"` at startup
- ❌ Any `"No module named 'torch'"` errors indicate build failure

## Rollback Plan

If Dockerfile approach fails:
1. Revert railway.json to Nixpacks
2. Use Dockerfile.lite (lighter version without torch)
3. Set EMBEDDING_BINDING=openai (fallback to OpenAI embeddings)
4. Investigate Railway support for heavy dependencies

## Related Files

- `Dockerfile.railway` - Railway-specific Dockerfile
- `railway.json` - Railway configuration
- `lightrag/llm/vietnamese_embed.py` - Vietnamese embedding with debug logs
- `pyproject.toml` - Python project dependencies
- `requirements-railway.txt` - Fallback requirements file

## Success Criteria

Deployment is successful when:
1. Build completes without torch import errors
2. Server starts and health check passes
3. Vietnamese embedding binding is available
4. Can generate embeddings for Vietnamese text
5. No dimension mismatch errors

## Next Steps

If this fix works:
1. Remove nixpacks.toml (no longer needed)
2. Document Railway deployment in main README
3. Add Dockerfile.railway to deployment guide
4. Consider making it the default Railway deployment method
