# Deploying LightRAG with Vietnamese Embedding to Railway

## 🚂 Railway Deployment Guide

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository with LightRAG code
- HuggingFace API token

### Step 1: Prepare Your Repository

Ensure these files are in your repository:
- `requirements-railway.txt` (includes torch and transformers)
- `.env.example` or railway.json for configuration
- `lightrag/` directory with all source code

### Step 2: Configure Environment Variables

In Railway dashboard, set these environment variables:

#### Required Variables
```env
# Server Configuration
HOST=0.0.0.0
PORT=8080

# LLM Configuration
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Vietnamese Embedding Configuration
EMBEDDING_BINDING=vietnamese
EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding
EMBEDDING_DIM=1024
EMBEDDING_BINDING_API_KEY=hf_your-huggingface-token-here
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here

# Storage Configuration
WORKING_DIR=/app/rag_storage
INPUT_DIR=/app/inputs

# Logging
LOG_LEVEL=INFO
LOG_DIR=/app/logs
```

#### Optional Variables
```env
# Performance
MAX_ASYNC=4
TIMEOUT=300

# Cache
ENABLE_LLM_CACHE=true

# CORS (if needed for frontend)
CORS_ORIGINS=https://yourdomain.com
```

### Step 3: Create railway.json

Create `railway.json` in repository root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements-railway.txt"
  },
  "deploy": {
    "startCommand": "lightrag-server",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Step 4: Deploy to Railway

#### Option A: Deploy via GitHub (Recommended)

1. **Connect Repository**
   ```
   Railway Dashboard → New Project → Deploy from GitHub
   ```

2. **Select Repository**
   - Choose your LightRAG repository
   - Railway will auto-detect Python project

3. **Configure Build**
   - Railway should detect `requirements-railway.txt`
   - If not, set build command: `pip install -r requirements-railway.txt`

4. **Set Start Command**
   ```
   lightrag-server
   ```

5. **Add Environment Variables**
   - Go to Variables tab
   - Add all required environment variables listed above

6. **Deploy**
   - Click Deploy
   - Wait for build (first time may take 5-10 minutes due to torch download)

#### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to project
railway link

# Set environment variables
railway variables set EMBEDDING_BINDING=vietnamese
railway variables set EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding
railway variables set EMBEDDING_DIM=1024
railway variables set EMBEDDING_BINDING_API_KEY=hf_xxx
# ... (add all other variables)

# Deploy
railway up
```

### Step 5: Verify Deployment

Once deployed, Railway will give you a URL like: `https://your-app.up.railway.app`

#### Test Health Endpoint
```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "configuration": {
    "embedding_binding": "vietnamese",
    "embedding_model": "AITeamVN/Vietnamese_Embedding",
    "embedding_dim": 1024
  }
}
```

#### Test Vietnamese Query
```bash
curl -X POST https://your-app.up.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Xin chào",
    "mode": "naive"
  }'
```

### Troubleshooting

#### Issue 1: "No module named 'torch'"
**Cause**: Missing dependencies

**Solution**:
1. Verify `requirements-railway.txt` includes:
   ```
   torch>=2.0.0
   transformers>=4.30.0
   ```
2. Check Railway build logs to ensure packages are installed
3. If build failed, increase build timeout in Railway settings

#### Issue 2: Build Timeout
**Cause**: Torch is large (~2GB) and takes time to download

**Solution**:
1. Railway Settings → Increase build timeout to 30 minutes
2. Use Railway's persistent build cache
3. Consider using Docker with pre-built torch image (see below)

#### Issue 3: Out of Memory
**Cause**: Vietnamese Embedding model loads into memory (~2GB)

**Solution**:
1. Upgrade Railway plan (minimum 2GB RAM recommended)
2. Or use CPU-only torch to save memory:
   ```
   requirements-railway.txt:
   torch>=2.0.0,<3.0.0; platform_machine != "arm64"
   --extra-index-url https://download.pytorch.org/whl/cpu
   ```

#### Issue 4: Slow First Request
**Cause**: Model downloads on first use

**Solution**:
1. Model will be cached after first download
2. Consider health check warmup:
   ```python
   # Add to startup
   await rag.initialize_storages()
   # Trigger model load
   await vietnamese_embed(["warmup"])
   ```

### Docker Deployment (Alternative)

If Railway build is slow, use Docker:

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements-railway.txt .
RUN pip install --no-cache-dir -r requirements-railway.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Start server
CMD ["lightrag-server"]
```

**Deploy**:
```bash
# Build
docker build -t lightrag-vietnamese .

# Push to registry (Railway supports Docker Hub)
docker push your-dockerhub/lightrag-vietnamese

# Deploy via Railway using Docker image
```

### Performance Optimization

#### 1. Use CPU-Only Torch (Smaller Size)
```txt
# In requirements-railway.txt
torch==2.0.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
```

#### 2. Enable Model Caching
Model is cached by default with `@lru_cache` - no action needed

#### 3. Optimize Worker Configuration
```env
# For Railway (limited resources)
MAX_ASYNC=2
EMBEDDING_FUNC_MAX_ASYNC=2
```

#### 4. Use Persistent Storage
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

### Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month
  - 500 hours execution
  - 8GB RAM, 8 vCPU
  - Sufficient for Vietnamese Embedding

- **Pro Plan**: $20/month
  - Unlimited execution
  - More resources

**Model Requirements**:
- Disk: ~2GB (model files)
- RAM: ~2-4GB (model in memory)
- CPU: Any (GPU not required but helpful)

### Security Best Practices

1. **Never commit secrets**
   ```bash
   # Add to .gitignore
   .env
   *.log
   rag_storage/
   ```

2. **Use Railway's secret management**
   - Store API keys in Railway variables
   - Don't include in code or repository

3. **Enable HTTPS**
   - Railway provides free SSL
   - Always use https:// URLs

4. **Set CORS properly**
   ```env
   CORS_ORIGINS=https://yourdomain.com
   ```

### Monitoring

Railway provides:
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Network usage
- **Alerts**: Set up alerts for failures

Access logs:
```bash
railway logs
```

### Updating Deployment

```bash
# Push to GitHub (if using GitHub integration)
git push origin main

# Or via CLI
railway up

# Or redeploy from dashboard
Railway Dashboard → Deployments → Redeploy
```

### Support

If issues persist:
1. Check Railway logs: `railway logs`
2. Check LightRAG logs: View LOG_DIR in Railway dashboard
3. Verify environment variables are set correctly
4. Test locally first with same configuration

### Summary

✅ **Working Configuration**:
- requirements-railway.txt with torch and transformers
- Environment variables properly set
- Sufficient RAM (2GB+)
- Health check endpoint configured

This should resolve the "No module named 'torch'" error on Railway! 🚀
