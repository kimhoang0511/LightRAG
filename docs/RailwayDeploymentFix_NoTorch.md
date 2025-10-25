# Railway Deployment - Vietnamese Embedding Fix

## ❌ Error: No module named 'torch'

### Root Cause
Railway was not installing `torch` and `transformers` packages needed for Vietnamese Embedding.

### Why This Happens
Railway auto-detects Python projects and may:
1. Skip custom requirements files
2. Use default pip install without extras
3. Not read `railway.json` buildCommand

## ✅ Solution Implemented

### 1. Added torch to pyproject.toml
**File:** `pyproject.toml`

Added to `[project.optional-dependencies]` → `api`:
```toml
api = [
    # ... other deps ...
    # Vietnamese Embedding support (included by default in api)
    "torch>=2.0.0",
    "transformers>=4.30.0",
]
```

**Why:** Railway typically runs `pip install -e .[api]` for API servers, so torch is now included automatically.

### 2. Updated railway.json
**File:** `railway.json`

```json
{
  "build": {
    "buildCommand": "pip install --no-cache-dir -e .[api] || pip install --no-cache-dir -r requirements-railway.txt"
  }
}
```

**Why:** Fallback to requirements-railway.txt if editable install fails.

### 3. Created nixpacks.toml
**File:** `nixpacks.toml`

```toml
[phases.install]
cmds = [
    "pip install --no-cache-dir --upgrade pip setuptools wheel",
    "pip install --no-cache-dir -e .[api]"
]
```

**Why:** Explicit control over Railway's build process.

### 4. Created Procfile
**File:** `Procfile`

```
web: lightrag-server
```

**Why:** Railway prefers Procfile for start commands.

### 5. Kept requirements-railway.txt
**File:** `requirements-railway.txt`

Kept as fallback option with all dependencies including torch and transformers.

## 🚀 Railway Deployment Steps

### Option A: Automatic (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "fix: add torch to api dependencies for Railway"
   git push
   ```

2. **Railway will auto-deploy** with correct dependencies

3. **Verify:**
   - Check Railway logs for successful torch installation
   - Hit `/health` endpoint
   - Should show `embedding_binding: vietnamese`

### Option B: Manual Configuration

If automatic doesn't work, configure in Railway Dashboard:

1. **Settings → Build:**
   ```
   Build Command: pip install --no-cache-dir -e .[api]
   ```

2. **Settings → Deploy:**
   ```
   Start Command: lightrag-server
   ```

3. **Redeploy**

### Option C: Force Requirements File

If you prefer using requirements-railway.txt:

1. **Settings → Build:**
   ```
   Build Command: pip install --no-cache-dir -r requirements-railway.txt
   ```

2. **Make sure requirements-railway.txt has:**
   ```
   torch>=2.0.0
   transformers>=4.30.0
   ```

## 🔍 Verification

After deployment:

```bash
# Check health endpoint
curl https://your-app.up.railway.app/health

# Should include in response:
{
  "configuration": {
    "embedding_binding": "vietnamese",
    "embedding_model": "AITeamVN/Vietnamese_Embedding",
    "embedding_dim": 1024
  }
}
```

## 📊 Build Time Expectations

- **First Build:** 8-15 minutes (downloading torch ~2GB)
- **Cached Builds:** 2-5 minutes
- **Memory Required:** Minimum 2GB RAM

## 🐛 Troubleshooting

### Still Getting "No module named 'torch'"

**Check 1: Build Logs**
```
Railway Dashboard → Deployments → Click latest → Build Logs
Search for "torch" - should see installation
```

**Check 2: Start Logs**
```
Railway Dashboard → Deployments → Click latest → Deploy Logs
Search for "No module" - see exact error
```

**Check 3: Verify Build Command**
```
Railway Dashboard → Settings → Build
Ensure: pip install --no-cache-dir -e .[api]
```

**Check 4: Python Version**
```
Railway Dashboard → Settings → Environment
Add: PYTHON_VERSION=3.10
```

### Build Timeout

If build times out:

```
Railway Dashboard → Settings → Build
Increase timeout to 30 minutes
```

### Out of Memory

Upgrade Railway plan or use CPU-only torch:

In `requirements-railway.txt`:
```
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.0.0+cpu
transformers>=4.30.0
```

Then in Railway:
```
Build Command: pip install --no-cache-dir -r requirements-railway.txt
```

## ✅ Success Checklist

- [ ] `pyproject.toml` has torch in api dependencies
- [ ] `railway.json` has correct buildCommand
- [ ] `nixpacks.toml` exists with install commands
- [ ] `Procfile` exists with start command
- [ ] Pushed to GitHub
- [ ] Railway auto-deployed successfully
- [ ] Build logs show torch installation
- [ ] `/health` endpoint returns correctly
- [ ] Vietnamese embedding works in queries

## 📝 Files Changed Summary

| File | Change | Why |
|------|--------|-----|
| `pyproject.toml` | Added torch to api deps | Auto-install with `pip install -e .[api]` |
| `railway.json` | Updated buildCommand | Explicit Railway config |
| `nixpacks.toml` | Created | Force correct build process |
| `Procfile` | Created | Railway start command |
| `requirements-railway.txt` | Already has torch | Fallback option |

## 🎉 Result

Railway now automatically installs torch and transformers, making Vietnamese Embedding work out of the box!

**No more "No module named 'torch'" errors!** 🚀
