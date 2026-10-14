#!/usr/bin/env python3
"""Hook entry. Runs the hop script that sits next to this file."""
import os
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "mac-hop.py"
os.execv(sys.executable, [sys.executable, str(TARGET), *sys.argv[1:]])
