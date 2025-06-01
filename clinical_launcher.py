#!/usr/bin/env python3
"""
Clinical Decision Support System Launcher
"""
import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.clinical_assistant import main

def cli_main():
    """Entry point for the clinical-assistant console command"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main() 