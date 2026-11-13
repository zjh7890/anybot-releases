#!/usr/bin/env python3
"""在测试进程退出后清理其私有目录，避免与仍在卸载的模块争用。"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

app = Path(sys.argv[1]).resolve(strict=True)
with tempfile.TemporaryDirectory(prefix="AnyBot-native-tools-") as parent:
    env = dict(os.environ, QA_APP=str(app), QA_TEST_PARENT=parent, ELECTRON_RUN_AS_NODE="1")
    result = subprocess.run(
        [str(app / "Contents/MacOS/Electron"), "--test", str(Path(__file__).with_suffix(".test.mjs"))],
        env=env,
        timeout=60,
    )
    code = result.returncode
sys.exit(code)
