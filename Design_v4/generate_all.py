import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent

for script in ['Breadboard_Optics_v4.py', 'Table_Optics_v4.py']:
    print(f"\n{'='*60}")
    print(f"  Generating {script}")
    print(f"{'='*60}")
    subprocess.run([sys.executable, script], cwd=here, check=True)

print("\nDone — both PDFs generated.")
