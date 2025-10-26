#!/bin/bash
# Switch between different Dockerfiles for Railway

set -e

echo "🚀 Railway Dockerfile Selector"
echo "=============================="
echo ""

# Check if railway.json exists
if [ ! -f "railway.json" ]; then
    echo "❌ railway.json not found!"
    exit 1
fi

echo "Available Dockerfiles:"
echo ""
echo "1. Dockerfile.railway           (~3-4GB)   - Standard, stable"
echo "2. Dockerfile.railway-minimal   (~2-2.5GB) - Minimal deps [RECOMMENDED]"
echo "3. Dockerfile.railway-lite      (~1.5-2GB) - Ultra-lite"
echo ""

read -p "Select Dockerfile (1/2/3) [2]: " choice
choice=${choice:-2}

case $choice in
    1)
        dockerfile="Dockerfile.railway"
        size="3-4GB"
        ;;
    2)
        dockerfile="Dockerfile.railway-minimal"
        size="2-2.5GB"
        ;;
    3)
        dockerfile="Dockerfile.railway-lite"
        size="1.5-2GB"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📝 Updating railway.json to use: $dockerfile"
echo "   Expected size: $size"

# Update railway.json
cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "$dockerfile"
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

echo "✅ railway.json updated"
echo ""

# Show diff
if command -v git &> /dev/null; then
    echo "📊 Changes:"
    git diff railway.json || true
    echo ""
fi

echo "🎯 Next steps:"
echo "  1. Review the changes above"
echo "  2. Commit: git add railway.json && git commit -m 'Switch to $dockerfile'"
echo "  3. Push: git push origin LightRag_Dev"
echo "  4. Monitor Railway build logs"
echo ""
echo "Expected outcome: Image size ~$size"
