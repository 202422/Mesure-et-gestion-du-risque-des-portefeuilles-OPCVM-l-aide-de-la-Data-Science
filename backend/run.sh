#!/usr/bin/env bash
python3 startup_sequence.py
rc=$?
if [ $rc -ne 0 ]; then
  echo "Startup sequence failed with exit code $rc"
  exit $rc
fi
python3 main.py
