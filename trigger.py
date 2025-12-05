#!/usr/bin/env python3
"""
Simple trigger script for Up2Git
This can be bound to system keyboard shortcuts

DEPRECATED: Use 'up2git --trigger' or 'python up2git_unified.py --trigger' instead
This file is kept for backward compatibility.
"""
import os
import sys
import time
from pathlib import Path

def main():
    """Create trigger file to signal the main app"""
    trigger_file = "/tmp/.upload_trigger"
    
    try:
        Path(trigger_file).write_text(str(time.time()))
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
