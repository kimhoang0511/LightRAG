#!/bin/bash
# Check Docker image size for Railway deployment

set -e

echo "🔍 Docker Image Size Check for Railway"
echo "========================================"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Cannot check image size locally."
    echo ""
    echo "To check on Railway:"
    echo "  1. Push your code"
    echo "  2. Monitor build logs"
    echo "  3. Look for 'Image size: X.X GB'"
    echo ""
    exit 0
fi

echo "✅ Docker found"
echo ""

# Build the image
echo "🏗️  Building Dockerfile.railway..."
if docker build -f Dockerfile.railway -t lightrag-railway-test . 2>&1 | tee /tmp/docker-build.log; then
    echo ""
    echo "✅ Build successful"
else
    echo ""
    echo "❌ Build failed. Check logs above."
    exit 1
fi

echo ""
echo "📊 Image Size Analysis"
echo "======================"

# Get image size
SIZE=$(docker images lightrag-railway-test --format "{{.Size}}")
echo "Total size: $SIZE"

# Convert to GB for comparison
SIZE_GB=$(docker images lightrag-railway-test --format "{{.Size}}" | grep -oE '[0-9.]+' | head -1)
UNIT=$(docker images lightrag-railway-test --format "{{.Size}}" | grep -oE '[A-Z]+' | head -1)

if [[ "$UNIT" == "GB" ]]; then
    if (( $(echo "$SIZE_GB < 4.0" | bc -l) )); then
        echo "✅ Size OK for Railway free tier (<4GB)"
    else
        echo "❌ Size too large for Railway free tier (>4GB)"
        echo "   Consider using Dockerfile.railway-lite"
    fi
elif [[ "$UNIT" == "MB" ]]; then
    echo "✅ Size OK for Railway free tier (<4GB)"
fi

echo ""
echo "📋 Layer Breakdown (largest first):"
docker history lightrag-railway-test --format "table {{.Size}}\t{{.CreatedBy}}" --no-trunc | head -15

echo ""
echo "📦 Largest packages in image:"
docker run --rm lightrag-railway-test du -sh /usr/local/lib/python3.10/site-packages/* 2>/dev/null | sort -h | tail -10 || echo "Could not analyze packages"

echo ""
echo "🧹 Cleanup"
read -p "Remove test image? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi lightrag-railway-test
    echo "✅ Test image removed"
fi

echo ""
echo "💡 Tips to reduce size:"
echo "  1. Use CPU-only torch (Dockerfile.railway already does this)"
echo "  2. Try multi-stage build (Dockerfile.railway-lite)"
echo "  3. Remove unnecessary dependencies"
echo "  4. Check .dockerignore to exclude large files"
