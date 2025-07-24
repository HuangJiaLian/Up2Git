#!/bin/bash
# Auto-start script for Up2Git
# This script will be used by the system startup applications

# Wait a bit for the desktop environment to fully load
sleep 5

# Change to the Up2Git directory
cd "/home/jie/Github/Up2Git"

# Start Up2Git in background
/home/jie/.jieprograms/miniconda3/bin/conda run -n up2git python up2git_unified.py &

# Log startup
echo "$(date): Up2Git auto-started" >> /tmp/up2git-startup.log
