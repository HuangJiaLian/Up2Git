#!/bin/bash

# Up2Git Executable Builder
# This script creates a standalone executable using PyInstaller

echo "🚀 Building Up2Git standalone executable..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project root: $PROJECT_ROOT"

# Activate conda environment
echo "📦 Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate up2git

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/

# Build the executable
echo "⚙️ Building executable with PyInstaller..."
pyinstaller --clean Up2Git.spec

# Check if build was successful
if [ -f "dist/Up2Git" ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📁 Executable location: $PROJECT_ROOT/dist/Up2Git"
    echo "📊 Executable size: $(du -h dist/Up2Git | cut -f1)"
    echo ""
    echo "🎯 Usage:"
    echo "   ./dist/Up2Git                    # Run from project directory"
    echo "   cp dist/Up2Git ~/bin/up2git      # Install to user bin (add ~/bin to PATH)"
    echo "   sudo cp dist/Up2Git /usr/local/bin/up2git  # Install system-wide"
    echo ""
    echo "⚠️  Note: You still need to configure .env file in the same directory as the executable"
    echo "    Or set environment variables: GITHUB_TOKEN, GITHUB_REPO, etc."
    
    # Create a portable package
    echo "📦 Creating portable package..."
    mkdir -p dist/Up2Git-Portable
    cp dist/Up2Git dist/Up2Git-Portable/
    cp .env.example dist/Up2Git-Portable/
    cp README.md dist/Up2Git-Portable/
    cp LICENSE dist/Up2Git-Portable/
    
    # Create a simple launcher script for the portable version
    cat > dist/Up2Git-Portable/run.sh << 'EOF'
#!/bin/bash
# Up2Git Portable Launcher

# Get the directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if .env exists, if not copy from example
if [ ! -f "$DIR/.env" ]; then
    if [ -f "$DIR/.env.example" ]; then
        echo "Creating .env file from template..."
        cp "$DIR/.env.example" "$DIR/.env"
        echo "Please edit .env file with your GitHub credentials:"
        echo "  nano $DIR/.env"
        echo ""
        echo "Then run this script again."
        exit 1
    else
        echo "Error: No .env.example found!"
        exit 1
    fi
fi

# Set environment variables from .env file
export $(grep -v '^#' "$DIR/.env" | xargs)

# Run the executable
"$DIR/Up2Git"
EOF
    
    chmod +x dist/Up2Git-Portable/run.sh
    
    echo "📦 Portable package created: dist/Up2Git-Portable/"
    echo "   - Contains executable, config template, and launcher"
    echo "   - Can be copied anywhere and run independently"
    
else
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    exit 1
fi
