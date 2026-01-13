#!/usr/bin/env python3
"""
Wyoming Claim Research - Main Entry Point

A GUI application for researching and visualizing Wyoming state mineral leases
with commodity type categorization and color-coded legends.

Usage:
    python main.py
"""

import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import WyomingClaimApp


def main():
    """Run the Wyoming Claim Research application."""
    app = WyomingClaimApp()
    app.mainloop()


if __name__ == '__main__':
    main()
