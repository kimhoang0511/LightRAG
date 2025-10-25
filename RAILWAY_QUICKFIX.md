# Quick Fix: Vietnamese Embedding on Railway

## ❌ Error
```
Exception: Failed to import vietnamese embedding: No module named 'torch'
```

## ✅ Solution

### Step 1: Use the Right Requirements File

Railway needs to install torch and transformers. Make sure you're using `requirements-railway.txt`:

**In Railway Dashboard:**
- Settings → Build → Build Command:
  ```
  pip install --no-cache-dir -r requirements-railway.txt
  ```

### Step 2: Verify railway.json

Ensure you have `railway.json` in root:
```json
{
  "build": {
    "buildCommand": "pip install --no-cache-dir -r requirements-railway.txt"
  },
  "deploy": {
    "startCommand": "lightrag-server"
  }
}
```

### Step 3: Set Environment Variables

In Railway Dashboard → Variables:
```
EMBEDDING_BINDING=vietnamese
EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding
EMBEDDING_DIM=1024
EMBEDDING_BINDING_API_KEY=hf_your_token_here
HUGGINGFACE_API_KEY=hf_your_token_here
```

### Step 4: Redeploy

```bash
# Via Railway CLI
railway up

# Or via Dashboard
Click "Deploy" → "Redeploy"
```

### Step 5: Verify

```bash
curl https://your-app.up.railway.app/health
```

Should show:
```json
{
  "configuration": {
    "embedding_binding": "vietnamese"
  }
}
```

## 🔧 Alternative: Use Lighter Requirements

If build is too slow, use CPU-only torch:

Create `requirements-railway-lite.txt`:
```txt
# ... other deps ...
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.0.0+cpu
transformers>=4.30.0
```

Then in Railway build command:
```
pip install --no-cache-dir -r requirements-railway-lite.txt
```

## 📊 Resource Requirements

- **Minimum RAM**: 2GB
- **Build Time**: 5-10 minutes (first time)
- **Disk Space**: ~3GB

Upgrade Railway plan if needed!

## ✅ Done!

Your Vietnamese Embedding should now work on Railway! 🎉
