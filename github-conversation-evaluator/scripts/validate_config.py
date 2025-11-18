import json
import sys
from pathlib import Path

paths = [
    Path(r"c:\Users\Melania Balestri\Desktop\valutazione\config\config_judge.json"),
    Path(r"c:\Users\Melania Balestri\Desktop\valutazione\config\config_metrics.json"),
]

any_error = False
for p in paths:
    try:
        with p.open("r", encoding="utf-8") as f:
            json.load(f)
        print(f"OK: {p}")
    except Exception as e:
        print(f"ERROR loading {p}: {e}")
        any_error = True

if any_error:
    sys.exit(1)

print("All JSON files loaded successfully.")
