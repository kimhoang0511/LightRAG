# Vietnamese Embedding Integration - Server Configuration Guide

## ✅ Implementation Complete

The Vietnamese Embedding model (`AITeamVN/Vietnamese_Embedding`) has been successfully integrated into the LightRAG server as a first-class binding option.

## 🎯 What Was Implemented

### 1. **New Embedding Binding: `vietnamese`**
   - Added `vietnamese` as a supported embedding binding type
   - Works alongside existing bindings: `ollama`, `openai`, `jina`, `azure_openai`, etc.

### 2. **Server Configuration Support**
   - Can be configured via `.env` file
   - Uses standard LightRAG configuration patterns
   - Automatic token detection from multiple environment variables

### 3. **Files Modified**

   **lightrag/api/config.py:**
   - Added `"vietnamese"` to `--embedding-binding` choices

   **lightrag/api/lightrag_server.py:**
   - Added `"vietnamese"` to validation list
   - Added Vietnamese embedding handler in `create_optimized_embedding_function()`

   **env.example:**
   - Added documentation for Vietnamese embedding configuration
   - Updated embedding binding list to include `vietnamese`

   **.env:**
   - Configured with Vietnamese embedding settings

## 📋 Configuration

### Required Environment Variables

```env
# Embedding Configuration
EMBEDDING_BINDING=vietnamese
EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding
EMBEDDING_DIM=1024
EMBEDDING_BINDING_API_KEY=your_hf_token_here

# Alternative token variables (any one works)
HUGGINGFACE_API_KEY=your_hf_token_here
HF_TOKEN=your_hf_token_here
```

### Optional LLM Configuration (for query responses)

```env
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_BINDING_HOST=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_key_here
```

## 🚀 Usage

### Starting the Server

```bash
# Make sure .env is configured
lightrag-server
```

The server will:
1. Read configuration from `.env`
2. Initialize Vietnamese Embedding model from HuggingFace
3. Use the model for all embedding operations
4. Expose REST API endpoints for document insertion and querying

### API Endpoints

All standard LightRAG API endpoints work with Vietnamese embedding:

- `POST /documents/text` - Insert Vietnamese text
- `POST /query` - Query in Vietnamese
- `GET /health` - Check server status (shows embedding configuration)

## 🧪 Testing

### 1. Test Configuration
```bash
python3 test_vietnamese_server_config.py
```
Validates that `.env` is properly configured.

### 2. Test Integration
```bash
python3 test_vietnamese_server_integration.py
```
Tests the full RAG pipeline with Vietnamese text.

### 3. Test Connection
```bash
python3 test_huggingface_connection.py
```
Verifies HuggingFace model access and token validity.

## 📊 Configuration Flow

```
1. .env file
   ├─ EMBEDDING_BINDING=vietnamese
   ├─ EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding
   └─ EMBEDDING_BINDING_API_KEY=hf_xxx

2. config.py parse_args()
   └─ Creates args object with all settings

3. lightrag_server.py create_app(args)
   └─ create_optimized_embedding_function()
      └─ Detects binding == "vietnamese"
         └─ Calls vietnamese_embed(texts, model_name, token)

4. vietnamese_embed.py
   └─ Loads model from HuggingFace
   └─ Generates 1024-dim embeddings
   └─ Returns normalized vectors
```

## ✨ Features

### Automatic Token Detection
The integration checks for tokens in this order:
1. `EMBEDDING_BINDING_API_KEY`
2. `HUGGINGFACE_API_KEY`
3. `HF_TOKEN`

### Model Caching
- Model is cached using `@lru_cache`
- Only loads once per server instance
- Reduces startup time on subsequent requests

### Device Detection
Automatically uses the best available device:
- CUDA (NVIDIA GPU)
- MPS (Apple Silicon GPU)
- CPU (fallback)

### Error Handling
- Token validation with HuggingFace API
- Retry logic for network issues
- Clear error messages for configuration problems

## 🔍 Verification

### Check Server Status
```bash
curl http://localhost:9621/health
```

Look for:
```json
{
  "configuration": {
    "embedding_binding": "vietnamese",
    "embedding_model": "AITeamVN/Vietnamese_Embedding",
    "embedding_binding_host": null
  }
}
```

### Test Query
```bash
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Thủ đô của Việt Nam là gì?", "mode": "hybrid"}'
```

## 📝 Notes

### vs Other Bindings
- **ollama/openai**: External API services
- **vietnamese**: Local model loaded from HuggingFace
- **Advantage**: No external API calls, full control, works offline after first download

### Model Specifications
- **Base Model**: BAAI/bge-m3
- **Fine-tuned For**: Vietnamese language
- **Training Data**: ~300,000 Vietnamese query-document triplets
- **Output Dimensions**: 1024
- **Max Sequence Length**: 2048 tokens
- **Similarity Function**: Dot product (embeddings are normalized)

### Performance
- **First Load**: Takes time to download model (~2GB)
- **Subsequent Loads**: Fast (uses cache)
- **Inference**: Depends on device (GPU recommended)
- **Batch Processing**: Supported and efficient

## 🐛 Troubleshooting

### Issue: "embedding binding not supported"
**Solution**: Update lightrag_server.py to include "vietnamese" in validation list (already done)

### Issue: "Invalid user token"
**Solution**: 
1. Check token validity: `python3 test_huggingface_connection.py`
2. Update `.env` with valid HuggingFace token
3. Token must have read access to models

### Issue: "Model not found"
**Solution**: 
1. Verify model name: `AITeamVN/Vietnamese_Embedding`
2. Check HuggingFace access: https://huggingface.co/AITeamVN/Vietnamese_Embedding
3. Ensure model is public or token has access

### Issue: Server starts but uses wrong embedding
**Solution**:
1. Check `.env` has `EMBEDDING_BINDING=vietnamese`
2. Restart server to reload configuration
3. Verify with: `curl http://localhost:9621/health`

## 📚 Related Documentation

- `docs/VietnameseEmbedding.md` - Complete API reference
- `docs/VietnameseEmbedding_QuickRef.md` - Quick start guide
- `examples/lightrag_vietnamese_embedding_simple.py` - Programmatic usage
- `examples/vietnamese_embedding_demo.py` - Comprehensive examples

## ✅ Success Criteria

- [x] Vietnamese embedding works as a binding option
- [x] Configuration via .env file
- [x] Server starts without errors
- [x] Model loads successfully
- [x] Embeddings generated correctly (1024 dimensions)
- [x] Integration tests pass
- [x] Health endpoint shows correct configuration
- [x] Vietnamese queries work end-to-end

## 🎉 Result

Vietnamese Embedding is now fully integrated into LightRAG server infrastructure. You can configure it just like any other embedding provider through environment variables, and it works seamlessly with all existing LightRAG features.
