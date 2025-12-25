from pathlib import Path
import os

print(Path(__file__).resolve().parent.parent.parent.parent)
print("\n\n", os.path.dirname(os.path.abspath(__file__)))