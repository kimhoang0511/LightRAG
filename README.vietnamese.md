# Vietnamese Embedding Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install huggingface-hub>=0.20.0
```

### 2. Get HuggingFace API Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with "Read" access
3. Copy the token (starts with `hf_...`)

### 3. Configure Environment

Copy `.env.vietnamese` to `.env` and update:

```bash
cp .env.vietnamese .env
# Edit .env and replace hf_your_token_here with your actual token
```

Or set environment variable:

```bash
export EMBEDDING_BINDING_API_KEY=hf_your_token_here
```

### 4. Test Installation

```bash
python test_vietnamese_inference_api.py
```

Expected output:
```
✅ SUCCESS!
   Shape: (3, 1024)
   Dtype: float32
✅ Dimension check passed (1024 dims)
✅ ALL TESTS PASSED!
```

## Configuration Details

### Model: BAAI/bge-m3

- **Type**: Multilingual embedding model
- **Dimensions**: 1024
- **Languages**: 100+ including Vietnamese
- **Max Sequence**: 8192 tokens
- **Base**: XLM-RoBERTa
- **Parameters**: 560M

### Advantages

✅ **Small Docker Image**: <1GB (vs 3GB with local model)
✅ **Fast**: GPU-accelerated on HuggingFace servers
✅ **Simple**: Only requires huggingface-hub package
✅ **Multilingual**: Supports Vietnamese and 100+ languages
✅ **No Maintenance**: Auto-updated by HuggingFace

### Environment Variables

```bash
# Required
EMBEDDING_BINDING=vietnamese
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIM=1024
EMBEDDING_BINDING_API_KEY=hf_your_token

# Alternative token names (any one works)
# HUGGINGFACE_API_KEY=hf_your_token
# HF_TOKEN=hf_your_token
```

## Usage

### Python API

```python
from lightrag.llm.vietnamese_embed import vietnamese_embed

# Embed texts
embeddings = await vietnamese_embed([
    "Xin chào, đây là văn bản tiếng Việt",
    "Hello, this is English text"
])

print(embeddings.shape)  # (2, 1024)
```

### Server API

```bash
# Start server
lightrag-server

# Insert document
curl -X POST http://localhost:9621/insert \
  -H "Content-Type: application/json" \
  -d '{"text": "Đây là văn bản về AI"}'

# Query
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{"query": "AI là gì?", "mode": "hybrid"}'
```

## Railway Deployment

### 1. Push to GitHub

```bash
git add .
git commit -m "Add Vietnamese Embedding with Inference API"
git push origin main
```

### 2. Deploy to Railway

1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `EMBEDDING_BINDING_API_KEY`: Your HuggingFace token
   - `LLM_BINDING_API_KEY`: Your OpenAI API key
3. Railway will auto-detect `Dockerfile.railway` and deploy

### 3. Expected Results

- Build time: 3-5 minutes
- Image size: <1GB
- Memory usage: ~500MB
- Startup time: <30 seconds

## Troubleshooting

### Error: "HuggingFace API token required"

**Solution**: Set `EMBEDDING_BINDING_API_KEY` in `.env` file

```bash
echo "EMBEDDING_BINDING_API_KEY=hf_your_token" >> .env
```

### Error: "Model doesn't support feature-extraction"

**Solution**: Update model to `BAAI/bge-m3` in `.env`

```bash
EMBEDDING_MODEL=BAAI/bge-m3
```

Note: `AITeamVN/Vietnamese_Embedding` will auto-switch to `BAAI/bge-m3`

### Error: "Rate limit exceeded"

**Solutions**:
1. Wait and retry (automatic retry built-in)
2. Upgrade to HuggingFace Pro ($9/month)
3. Use local Ollama model instead

## Performance

### Inference API (Current)
```
100 texts: ~5 seconds
Docker image: <1GB
Memory: ~500MB
```

### Local Model (Alternative)
```
100 texts: ~25 seconds
Docker image: ~3GB
Memory: ~2GB
```

**→ 5x faster with Inference API!**

## Alternative: Local Ollama

If you prefer local model:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull bge-m3 model
ollama pull bge-m3:latest

# Update .env
EMBEDDING_BINDING=ollama
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_BINDING_HOST=http://localhost:11434
```

## Support

- Documentation: [docs/VietnameseEmbedding_InferenceAPI.md](docs/VietnameseEmbedding_InferenceAPI.md)
- Issues: https://github.com/HKUDS/LightRAG/issues
- Model: https://huggingface.co/BAAI/bge-m3

## License

This implementation uses BAAI/bge-m3 which is licensed under Apache 2.0.
