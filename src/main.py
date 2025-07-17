#!/usr/bin/env python3
"""
Main entry point for the aitop application.
This script can be run directly with Python.
"""

import sys
import os

# Add the src directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aitop import main as aitop_main


def main():
    """Main entry point for the application."""
    try:
        aitop_main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
