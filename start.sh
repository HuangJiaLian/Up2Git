#!/bin/bash
# Start Up2Git application

echo "🚀 Starting Up2Git..."
cd "$(dirname "$0")"
/home/jie/.jieprograms/miniconda3/bin/conda run -n up2git python up2git_unified.py &
echo "✅ Up2Git started in background"
echo "📋 Right-click the system tray icon to access settings"
echo ""
echo "To set up keyboard shortcut, run: ./setup_shortcut.sh"
