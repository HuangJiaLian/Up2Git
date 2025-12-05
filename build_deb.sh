#!/bin/bash

# Up2Git .deb Package Builder
# Creates a Debian package from PyInstaller executable

set -e  # Exit on error

VERSION="1.0.0"
PACKAGE_NAME="up2git"
MAINTAINER="Jie Huang <jiehuang.fi@gmail.com>"
DESCRIPTION="Upload clipboard content to GitHub with a keyboard shortcut"

echo "🚀 Building Up2Git .deb package..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Step 1: Build the executable first (if not exists)
if [ ! -f "dist/Up2Git" ]; then
    echo "📦 Executable not found. Building with PyInstaller first..."
    ./build_executable.sh
fi

if [ ! -f "dist/Up2Git" ]; then
    echo "❌ Failed to build executable!"
    exit 1
fi

echo "✅ Executable found: dist/Up2Git"

# Step 2: Create package directory structure
echo "📁 Creating package structure..."
PKG_DIR="dist/${PACKAGE_NAME}_${VERSION}_amd64"
rm -rf "$PKG_DIR"

mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$PKG_DIR/usr/share/doc/${PACKAGE_NAME}"

# Step 3: Copy files
echo "📋 Copying files..."

# Main executable
cp dist/Up2Git "$PKG_DIR/usr/bin/up2git"
chmod 755 "$PKG_DIR/usr/bin/up2git"

# Icons
if [ -f "icons/icon.svg" ]; then
    cp icons/icon.svg "$PKG_DIR/usr/share/icons/hicolor/scalable/apps/up2git.svg"
fi
if [ -f "icons/icon.png" ]; then
    cp icons/icon.png "$PKG_DIR/usr/share/icons/hicolor/128x128/apps/up2git.png"
fi

# Documentation
cp README.md "$PKG_DIR/usr/share/doc/${PACKAGE_NAME}/"
cp LICENSE "$PKG_DIR/usr/share/doc/${PACKAGE_NAME}/"

# Step 4: Create desktop file
cat > "$PKG_DIR/usr/share/applications/up2git.desktop" << EOF
[Desktop Entry]
Name=Up2Git
Comment=Upload clipboard content to GitHub
Exec=/usr/bin/up2git
Icon=up2git
Terminal=false
Type=Application
Categories=Utility;Development;
StartupNotify=false
Keywords=github;upload;clipboard;screenshot;
EOF

# Step 5: Create DEBIAN control file
cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: ${MAINTAINER}
Description: ${DESCRIPTION}
 Up2Git is a system tray application that allows you to quickly
 upload clipboard content (images, files) to a GitHub repository.
 .
 Features:
  - System tray integration
  - Keyboard shortcut support (up2git --trigger)
  - Automatic URL copying to clipboard
  - Support for images and files
EOF

# Step 6: Create postinst script (runs after installation)
cat > "$PKG_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

echo ""
echo "✅ Up2Git installed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Run 'up2git' to start the application"
echo "   2. Right-click the tray icon → Settings to configure GitHub credentials"
echo "   3. Set up a keyboard shortcut (e.g., Alt+Shift+U) to run: up2git --trigger"
echo ""
echo "💡 Tip: Add Up2Git to your startup applications for automatic launch."
echo ""

exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/postinst"

# Step 7: Create prerm script (runs before removal)
cat > "$PKG_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Kill running instances
pkill -f "/usr/bin/up2git" 2>/dev/null || true

exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/prerm"

# Step 8: Build the .deb package
echo "📦 Building .deb package..."
dpkg-deb --build "$PKG_DIR"

# Move to dist folder with clean name
DEB_FILE="dist/${PACKAGE_NAME}_${VERSION}_amd64.deb"
echo ""
echo "✅ Package built successfully!"
echo ""
echo "📁 Package location: $PROJECT_ROOT/$DEB_FILE"
echo "📊 Package size: $(du -h "$DEB_FILE" | cut -f1)"
echo ""
echo "🎯 Installation:"
echo "   sudo dpkg -i $DEB_FILE"
echo ""
echo "🗑️  Uninstallation:"
echo "   sudo dpkg -r up2git"
echo ""
