"""
Run a sequence of preprocessing scripts before starting the backend.

Order executed:
- ../weekly-opcvm-scraper/scraper.py
- ../weekly-masi-scraper/scraper.py
- ../dataset_building/new_pdfs_extraction.py
- ../dataset_building/dataset_processing.py

This script returns non-zero exit code on the first failure.
"""
import os
import subprocess
import sys


SCRIPTS = [
    os.path.join('..', 'weekly-opcvm-scraper', 'scraper.py'),
    os.path.join('..', 'weekly-masi-scraper', 'scraper.py'),
    os.path.join('..', 'dataset_building', 'new_pdfs_extraction.py'),
    os.path.join('..', 'dataset_building', 'dataset_processing.py'),
]


def run_script(path):
    print(f"Running: {path}")
    # run with the same python executable
    cmd = [sys.executable, path]
    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def main():
    # Ensure working directory is the backend folder
    repo_backend = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_backend)

    for script in SCRIPTS:
        if not os.path.exists(script):
            print(f"Error: script not found: {script}")
            return 2
        rc = run_script(script)
        if rc != 0:
            print(f"Script failed: {script} (exit {rc})")
            return rc

    print("All startup scripts completed successfully.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
