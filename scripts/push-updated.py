"""Refresh, commit the evidence snapshot, then push the current branch."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def run(*args):return subprocess.run(args,cwd=ROOT,check=True)
run(sys.executable,'scripts/refresh-data.py')
run('git','add','--','data/latest.json','data/manifest.json')
if subprocess.run(['git','diff','--cached','--quiet','--','data/latest.json','data/manifest.json'],cwd=ROOT).returncode:
    run('git','commit','--only','-m','Refresh experiment evidence snapshot','--','data/latest.json','data/manifest.json')
run('git','push',*sys.argv[1:])
