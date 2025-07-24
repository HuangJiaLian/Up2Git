#!/bin/bash
# Setup auto-start for Up2Git

echo "🚀 Setting up Up2Git auto-start..."

# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart

# Copy the desktop entry to autostart directory
cp up2git-autostart.desktop ~/.config/autostart/

echo "✅ Up2Git will now start automatically when you boot up!"
echo ""
echo "📋 You can also manage this through:"
echo "   Menu → Preferences → Startup Applications"
echo ""
echo "🔧 To disable auto-start later:"
echo "   rm ~/.config/autostart/up2git-autostart.desktop"
echo ""
echo "📝 Startup logs will be saved to: /tmp/up2git-startup.log"
