# Copyright Spack Project Developers. See COPYRIGHT file for details.
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import json
import os
import pathlib
import subprocess
import sys

import pytest

import spack.paths


@pytest.mark.parametrize("owned_count", [0, 1, 205])
def test_refresh_only_owned_specs(tmp_path, owned_count):
    """Shared dependencies are excluded, including an entirely inherited environment."""
    fake_spack = tmp_path / "spack"
    log = tmp_path / "commands.jsonl"
    shared = "a" * 32
    owned = [f"{i:032d}" for i in range(owned_count)]
    fake_spack.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"with open({str(log)!r}, 'a') as f: f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[3] == 'find':\n"
        f"    print('\\n'.join({[shared] + owned!r} if sys.argv[2] == 'child' "
        f"else {[shared]!r}))\n"
    )
    fake_spack.chmod(0o755)
    script = pathlib.Path(spack.paths.share_path) / "arc/refresh-owned-modules.py"
    subprocess.run(
        [sys.executable, str(script), "--apply", "child", "parent"],
        env=dict(os.environ, SPACK_COMMAND=str(fake_spack)),
        check=True,
        capture_output=True,
        text=True,
    )
    commands = [json.loads(line) for line in log.read_text().splitlines()]
    refreshes = [cmd for cmd in commands if cmd[2] == "module"]
    selected = [arg for cmd in refreshes for arg in cmd[6:]]
    assert selected == ["/" + h for h in sorted(owned)]
    assert all(cmd[:6] == ["-e", "child", "module", "lmod", "refresh", "-y"] for cmd in refreshes)
    assert all(0 < len(cmd[6:]) <= 100 for cmd in refreshes)
