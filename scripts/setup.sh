#!/bin/bash

# LCF Civic Summaries - Railway Setup Script
# This script helps set up the project for Railway deployment

echo "🚂 LCF Civic Summaries - Railway Setup"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "Procfile" ]; then
    echo "❌ Error: Procfile not found. Please run this script from the project root directory."
    exit 1
fi

echo "✅ Project structure verified"

# Check for required files
required_files=("requirements.txt" "railway.json" ".env.example" "src/api_server.py" "src/scheduler.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ All required files present"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "🔧 Please edit .env and add your actual API keys and configuration"
else
    echo "✅ .env file exists"
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir -p data
    echo "✅ Created data directory"
fi

# Check Python dependencies
echo "🐍 Checking Python environment..."

if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi

if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
else
    echo "❌ pip3 not found. Please install pip."
    exit 1
fi

# Install dependencies (optional)
read -p "📦 Install Python dependencies now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Test basic functionality
echo "🧪 Running basic tests..."

# Test API server import
python3 -c "import src.api_server" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ API server module loads correctly"
else
    echo "❌ API server module has import errors"
fi

# Test scheduler import
python3 -c "import src.scheduler" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Scheduler module loads correctly"
else
    echo "❌ Scheduler module has import errors"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your actual configuration"
echo "2. Test locally: python3 src/api_server.py"
echo "3. Deploy to Railway using the deployment guide"
echo ""
echo "📚 Documentation:"
echo "- README.md - Project overview and features"
echo "- docs/RAILWAY_DEPLOYMENT.md - Detailed deployment guide"
echo "- .env.example - Environment variables reference"
echo ""
echo "🌐 Railway Deployment:"
echo "1. Push this code to GitHub"
echo "2. Connect GitHub repo to Railway"
echo "3. Configure environment variables"
echo "4. Deploy!"
echo ""
echo "✨ Your LCF Civic Summaries system is ready for Railway deployment!"

