"""
Vietnamese Embedding Integration for LightRAG
Model: AITeamVN/Vietnamese_Embedding
Base: BAAI/bge-m3

Installation:
    pip install lightrag-hku[vietnamese-embedding]
    
    Or manually:
    pip install torch>=2.0.0 transformers>=4.30.0
"""

import os
import sys
import numpy as np
from functools import lru_cache

# Debug logging for import process
print("=" * 80, flush=True)
print("🔍 VIETNAMESE EMBEDDING - Import Debug", flush=True)
print("=" * 80, flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Python executable: {sys.executable}", flush=True)
print(f"Python path: {sys.path}", flush=True)
print("-" * 80, flush=True)

# Check if packages are installed
print("📦 Checking installed packages...", flush=True)
try:
    import pkg_resources
    installed = {pkg.key for pkg in pkg_resources.working_set}
    print(f"✓ Total packages installed: {len(installed)}", flush=True)
    
    if 'torch' in installed:
        torch_pkg = pkg_resources.get_distribution('torch')
        print(f"✓ torch found: version {torch_pkg.version}", flush=True)
    else:
        print("✗ torch NOT found in installed packages", flush=True)
    
    if 'transformers' in installed:
        trans_pkg = pkg_resources.get_distribution('transformers')
        print(f"✓ transformers found: version {trans_pkg.version}", flush=True)
    else:
        print("✗ transformers NOT found in installed packages", flush=True)
        
except Exception as e:
    print(f"⚠ Could not check pkg_resources: {e}", flush=True)

print("-" * 80, flush=True)

# Try to import torch with detailed error
print("🔧 Attempting to import torch...", flush=True)
try:
    import torch
    print(f"✅ torch imported successfully!", flush=True)
    print(f"   torch version: {torch.__version__}", flush=True)
    print(f"   torch file location: {torch.__file__}", flush=True)
    print(f"   CUDA available: {torch.cuda.is_available()}", flush=True)
    print(f"   MPS available: {torch.backends.mps.is_available()}", flush=True)
except ImportError as e:
    print(f"❌ Failed to import torch!", flush=True)
    print(f"   Error: {e}", flush=True)
    print(f"   Error type: {type(e).__name__}", flush=True)
    
    # Try to find torch manually
    print("\n🔍 Searching for torch in sys.path...", flush=True)
    for path in sys.path:
        if os.path.exists(path):
            try:
                items = os.listdir(path)
                torch_items = [item for item in items if 'torch' in item.lower()]
                if torch_items:
                    print(f"   Found in {path}:", flush=True)
                    for item in torch_items:
                        print(f"     - {item}", flush=True)
            except Exception:
                pass
    
    print("=" * 80, flush=True)
    raise ImportError(
        f"\n{'='*80}\n"
        f"❌ TORCH IMPORT FAILED\n"
        f"{'='*80}\n"
        f"Error: {e}\n\n"
        f"Vietnamese Embedding requires torch and transformers.\n\n"
        f"Installation commands:\n"
        f"  pip install lightrag-hku[vietnamese-embedding]\n"
        f"  OR\n"
        f"  pip install torch>=2.0.0 transformers>=4.30.0\n\n"
        f"For Railway deployment, ensure pyproject.toml includes:\n"
        f"  api = [..., 'torch>=2.0.0', 'transformers>=4.30.0']\n"
        f"{'='*80}\n"
    ) from e

print("-" * 80, flush=True)

# Try to import transformers
print("🔧 Attempting to import transformers...", flush=True)
try:
    from transformers import AutoTokenizer, AutoModel
    print(f"✅ transformers imported successfully!", flush=True)
    import transformers
    print(f"   transformers version: {transformers.__version__}", flush=True)
    print(f"   transformers file location: {transformers.__file__}", flush=True)
except ImportError as e:
    print(f"❌ Failed to import transformers!", flush=True)
    print(f"   Error: {e}", flush=True)
    print("=" * 80, flush=True)
    raise ImportError(
        f"\n{'='*80}\n"
        f"❌ TRANSFORMERS IMPORT FAILED\n"
        f"{'='*80}\n"
        f"Error: {e}\n\n"
        f"Install with: pip install transformers>=4.30.0\n"
        f"{'='*80}\n"
    ) from e

print("=" * 80, flush=True)
print("✅ ALL IMPORTS SUCCESSFUL - Vietnamese Embedding Ready!", flush=True)
print("=" * 80, flush=True)

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from lightrag.utils import wrap_embedding_func_with_attrs, logger
from lightrag.exceptions import APIConnectionError, RateLimitError, APITimeoutError

# Disable tokenizers parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"


@lru_cache(maxsize=1)
def initialize_vietnamese_embedding_model(
    model_name: str = "AITeamVN/Vietnamese_Embedding",
    token: str | None = None,
):
    """
    Initialize the Vietnamese Embedding model with caching.
    
    Args:
        model_name: HuggingFace model identifier
        token: HuggingFace API token for model access
        
    Returns:
        Tuple of (model, tokenizer)
    """
    logger.info(f"Loading Vietnamese Embedding model: {model_name}")
    
    # Get token from environment if not provided
    if token is None:
        token = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
    
    try:
        # Try fast tokenizer first for better performance
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=token,
                trust_remote_code=True,
                use_fast=True  # Try fast tokenizer first (10x faster)
            )
            logger.info("Vietnamese Embedding: Using fast tokenizer")
        except Exception as fast_error:
            # Fallback to slow tokenizer if fast fails (e.g., enum serialization error)
            logger.warning(f"Fast tokenizer failed ({fast_error}), falling back to slow tokenizer")
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=token,
                trust_remote_code=True,
                use_fast=False  # Force slow tokenizer as fallback
            )
            logger.info("Vietnamese Embedding: Using slow tokenizer (fallback)")
        
        model = AutoModel.from_pretrained(
            model_name,
            token=token,
            trust_remote_code=True
        )
        
        logger.info("Vietnamese Embedding model loaded successfully")
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Failed to load Vietnamese Embedding model: {e}")
        raise


@wrap_embedding_func_with_attrs(embedding_dim=1024)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError)
    ),
)
async def vietnamese_embed(
    texts: list[str],
    model_name: str = "AITeamVN/Vietnamese_Embedding",
    token: str | None = None,
) -> np.ndarray:
    """
    Generate embeddings for Vietnamese texts using AITeamVN/Vietnamese_Embedding model.
    
    This model is based on BGE-M3 and fine-tuned on Vietnamese data with:
    - Maximum sequence length: 2048 tokens
    - Output dimensionality: 1024 dimensions
    - Similarity function: Dot product similarity
    
    Args:
        texts: List of texts to embed (in Vietnamese or other languages)
        model_name: HuggingFace model identifier (default: AITeamVN/Vietnamese_Embedding)
        token: HuggingFace API token for model access
        
    Returns:
        numpy array of embeddings with shape (len(texts), 1024)
        
    Raises:
        APIConnectionError: If there is a connection error
        RateLimitError: If rate limit is exceeded
        APITimeoutError: If request times out
    """
    # Get token from environment if not provided
    if token is None:
        token = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
    
    # Initialize model and tokenizer
    model, tokenizer = initialize_vietnamese_embedding_model(model_name, token)
    
    # Detect the appropriate device
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.debug("Using CUDA device for embedding")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
        logger.debug("Using MPS device for embedding")
    else:
        device = torch.device("cpu")
        logger.debug("Using CPU device for embedding")
    
    # Move model to device
    model = model.to(device)
    model.eval()  # Set to evaluation mode
    
    try:
        # Tokenize texts with optimized max_length for Railway CPU
        # Using 512 instead of 2048 to reduce computation time
        # Most texts are shorter than 512 tokens anyway
        encoded_input = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,  # Reduced from 2048 for 4x speedup
            return_tensors="pt"
        ).to(device)
        
        # Generate embeddings
        with torch.no_grad():
            model_output = model(**encoded_input)
            # Use mean pooling on the token embeddings
            embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
            # Normalize embeddings for dot product similarity
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        # Convert to numpy array
        if embeddings.dtype == torch.bfloat16:
            embeddings_np = embeddings.to(torch.float32).cpu().numpy()
        else:
            embeddings_np = embeddings.cpu().numpy()
        
        logger.debug(f"Generated embeddings for {len(texts)} texts (max_len=512), shape: {embeddings_np.shape}")
        return embeddings_np
        
    except Exception as e:
        logger.error(f"Error generating Vietnamese embeddings: {e}")
        raise APIConnectionError(f"Vietnamese embedding generation failed: {e}") from e


def mean_pooling(model_output, attention_mask):
    """
    Perform mean pooling on token embeddings.
    
    Args:
        model_output: Model output containing token embeddings
        attention_mask: Attention mask to exclude padding tokens
        
    Returns:
        Pooled embeddings
    """
    token_embeddings = model_output[0]  # First element contains token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


# Convenience function for easier integration
@wrap_embedding_func_with_attrs(embedding_dim=1024)
async def vietnamese_embedding_func(texts: list[str]) -> np.ndarray:
    """
    Convenience wrapper for Vietnamese embedding that reads token from environment.
    
    Set HUGGINGFACE_API_KEY or HF_TOKEN environment variable with your HuggingFace token.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        numpy array of embeddings
    """
    return await vietnamese_embed(texts)
