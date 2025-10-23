"""
PyBootManager - Main Application Entry Point
A Python-Based Boot Manager for Windows
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui import main

if __name__ == "__main__":
    main()
