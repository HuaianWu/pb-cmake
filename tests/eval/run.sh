#!/bin/sh
# ProgramBench-style entry point (tests/eval/run.sh). Results go to <workspace>/eval/results.xml.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"
mkdir -p eval
python3 -m pytest -q -p no:cacheprovider --junitxml=eval/results.xml tests/
