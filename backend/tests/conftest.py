import sys
from pathlib import Path

# Ensure the backend package root is importable when running `pytest` from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
