import os

import pytest

from ._pb import run_case

EXECUTABLE = os.environ.get("EXECUTABLE", "/workspace/executable")
PROG = "cmark"


@pytest.fixture
def run():
    def _run(args, stdin=None, files=None, env=None):
        return run_case(EXECUTABLE, {"args": args, "stdin": stdin, "files": files, "env": env}, PROG)
    return _run
