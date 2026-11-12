"""只下载具名 QA 草稿原包，先核摘要再解压。"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

tag, asset, expected = (os.environ[key] for key in ("QA_TAG", "QA_ASSET", "QA_SHA256"))
assert re.fullmatch(r"qa-[A-Za-z0-9._-]+", tag), "需要具名 QA 标签"
assert re.fullmatch(r"AnyBot-[A-Za-z0-9._-]+\.zip", asset), "候选文件名无效"
assert re.fullmatch(r"[a-f0-9]{64}", expected), "SHA256 无效"
release = json.loads(subprocess.check_output(["gh", "release", "view", tag, "--json", "isDraft,assets"]))
assert release["isDraft"], "此入口只验 QA 草稿，不改变正式 Release"
assert sum(row["name"] == asset for row in release["assets"]) == 1, "需要唯一原件"
destination = Path("candidate")
destination.mkdir(mode=0o700)
subprocess.run(["gh", "release", "download", tag, "--pattern", asset, "--dir", str(destination)], check=True)
archive = destination / asset
digest = hashlib.file_digest(archive.open("rb"), "sha256").hexdigest()
assert digest == expected, "下载摘要与本地已签候选不符"
subprocess.run(["/usr/bin/ditto", "-x", "-k", str(archive), str(destination)], check=True)
assert (destination / "AnyBot.app").is_dir(), "候选缺 App"
archive.unlink()
print(json.dumps({"asset": asset, "sha256": digest, "draft": True}))
