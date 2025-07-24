#!/usr/bin/env python3
"""
Simple trigger script for Up2Git
This can be bound to system keyboard shortcuts
"""
import os
import time
import sys

def main():
    """Create trigger file to signal the main app"""
    trigger_file = "/tmp/.upload_trigger"
    
    try:
        # Create trigger file
        with open(trigger_file, 'w') as f:
            f.write(str(time.time()))
        
        print("Upload triggered!")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
