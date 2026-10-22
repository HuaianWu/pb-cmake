"""Runs one test case against an executable and normalizes the result.

This file is copied verbatim into every generated task as tests/_pb.py, so
recording (authoring time) and checking (evaluation time) use exactly the
same code path.
"""

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

BASE_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C", "TZ": "UTC"}
MAX_FILE_BYTES = 1 << 20


@dataclass
class Result:
    returncode: int
    stdout: bytes
    stderr: bytes
    files: dict = field(default_factory=dict)  # files created or changed in the working dir
    timed_out: bool = False

    def key(self):
        return (self.returncode, self.stdout, self.stderr, tuple(sorted(self.files.items())), self.timed_out)


def _as_bytes(v):
    return v.encode() if isinstance(v, str) else v


def normalize(data: bytes, exe: str, prog: str, workdir: str, names=True) -> bytes:
    """Make output independent of where and under which name the program runs.

    - the temp working dir becomes <TMP>
    - in stderr only, the program (its full path, as glibc getopt prints argv[0], or
      its bare name) in "NAME: message" / "Usage: NAME" positions
      becomes <PROG>, whether the candidate prints its argv[0] ("executable") or the
      original name.
    """
    for wd in {workdir, os.path.realpath(workdir)}:
        data = data.replace(wd.encode() + b"/", b"").replace(wd.encode(), b"<TMP>")
    if not names:
        return data
    # glibc getopt prints argv[0] as given, i.e. the full path of the executable.
    for p in sorted({exe, os.path.realpath(exe)}, key=len, reverse=True):
        data = data.replace(p.encode() + b":", b"<PROG>:")
    names = {prog, os.path.basename(exe), "executable"}
    alt = b"|".join(re.escape(n.encode()) for n in sorted(names, key=len, reverse=True))
    data = re.sub(rb"(?m)(^|Usage: )(?:" + alt + rb")(?=[: ])", rb"\1<PROG>", data)
    return data


def _snapshot(root: Path):
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            out[str(p.relative_to(root))] = p.read_bytes()[:MAX_FILE_BYTES]
    return out


def run_case(exe, case, prog, timeout=10, extra_env=None, workdir_prefix="pb-"):
    """Run `case` (dict with args/stdin/files/env) in a fresh temp dir."""
    exe = os.path.abspath(exe)
    tmp = tempfile.mkdtemp(prefix=workdir_prefix)
    try:
        root = Path(tmp)
        inputs = {}
        for rel, content in (case.get("files") or {}).items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(_as_bytes(content))
            inputs[rel] = _as_bytes(content)
        env = dict(BASE_ENV, HOME=tmp, **(case.get("env") or {}), **(extra_env or {}))
        stdin = case.get("stdin")
        try:
            proc = subprocess.run(
                [exe, *case.get("args", [])],
                input=_as_bytes(stdin) if stdin is not None else b"",
                capture_output=True, cwd=tmp, env=env, timeout=timeout,
            )
            rc, out, err, to = proc.returncode, proc.stdout, proc.stderr, False
        except subprocess.TimeoutExpired as e:
            rc, out, err, to = -999, e.stdout or b"", e.stderr or b"", True
        after = _snapshot(root)
        changed = {k: normalize(v, exe, prog, tmp, names=False) for k, v in after.items() if inputs.get(k) != v}
        return Result(rc, normalize(out, exe, prog, tmp, names=False), normalize(err, exe, prog, tmp), changed, to)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
