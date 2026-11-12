"""在当前 macOS 用户的空目录实跑已签 App 的自有 Backend 与 Codex。"""
import argparse
import ctypes
import errno
import json
import os
from pathlib import Path
import platform
import plistlib
import signal
import subprocess
import tempfile
import time
import urllib.error
import urllib.request


def process_table():
    rows = {}
    for line in subprocess.check_output(["/bin/ps", "-axo", "pid=,ppid=,comm="], text=True).splitlines():
        row = line.strip().split(None, 2)
        if len(row) == 3:
            rows[int(row[0])] = (int(row[1]), row[2])
    return rows


def descendants(pid):
    rows, owned = process_table(), {pid}
    for _ in range(10):
        owned |= {p for p, (parent, _) in rows.items() if parent in owned}
    return owned


def verify(app, architecture, build, output):
    assert platform.system() == "Darwin", "需要 macOS"
    assert platform.machine() == architecture, "必须在目标原生架构运行，不用 Rosetta 代验"
    translated, size = ctypes.c_int(), ctypes.c_size_t(ctypes.sizeof(ctypes.c_int))
    system = ctypes.CDLL(None, use_errno=True)
    if system.sysctlbyname(b"sysctl.proc_translated", ctypes.byref(translated), ctypes.byref(size), None, 0) != 0:
        assert ctypes.get_errno() == errno.ENOENT, "无法确认 Rosetta 状态"
    assert translated.value == 0, "Rosetta 不能作为原生 Intel 验收"
    assert build.isdecimal(), "版本号无效"
    app = app.resolve(strict=True)
    info = plistlib.loads((app / "Contents/Info.plist").read_bytes())
    assert info["CFBundleIdentifier"] == "com.zjh.anybot.mac" and info["CFBundleVersion"] == build
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)
    signed = subprocess.run(["/usr/bin/codesign", "-d", "-vv", str(app)], check=True, capture_output=True, text=True).stderr
    assert "TeamIdentifier=QR48N878TG\n" in signed and "Authority=Developer ID Application:" in signed and "runtime" in signed
    binary = app / "Contents/MacOS" / info["CFBundleExecutable"]
    assert set(subprocess.check_output(["/usr/bin/lipo", "-archs", str(binary)], text=True).split()) == {"arm64", "x86_64"}
    os.umask(0o077)
    root = Path(tempfile.mkdtemp(prefix="AnyBot-factory-")).resolve()
    home = root / "新 用户 Home"
    home.mkdir(mode=0o700)
    data = home / "Library/Application Support/AnyBot 验收"
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", "CODEX_HOME": str(home / ".codex"), "ELECTRON_RUN_AS_NODE": "1", "ANYBOT_DATA_HOME": str(data), "ANYBOT_BUILD": build}
    result = {"build": build, "architecture": architecture, "rosetta": False, "os": platform.mac_ver()[0], "uid": os.getuid(), "signature_verify_exit": 0, "universal": True, "empty_home": True, "external_cli_in_path": False, "oauth_or_business_writes": 0}
    process, owned, began = None, set(), time.monotonic()
    try:
        with (root / "backend.log").open("wb") as log:
            process = subprocess.Popen([str(binary), str(app / "Contents/Resources/app/backend/host.mjs")], env=env, cwd=home, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        owned.add(process.pid)
        ready = data / "backend/ready.json"
        while not ready.exists():
            owned |= descendants(process.pid)
            if process.poll() is not None:
                raise RuntimeError("BACKEND_EXITED_BEFORE_READY")
            if time.monotonic() - began > 40:
                raise RuntimeError("BACKEND_READY_TIMEOUT")
            time.sleep(0.1)
        assert json.loads(ready.read_text())["pid"] == process.pid
        result["ready_ms"] = round((time.monotonic() - began) * 1000)
        config = json.loads((data / "backend/host/config.json").read_text())

        def get(route, host=None):
            headers = {"Authorization": "Bearer " + config["token"]}
            if host:
                headers["X-AnyBot-Host-Id"] = host
            request = urllib.request.Request("http://127.0.0.1:" + str(config["port"]) + route, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    return response.status, json.load(response)
            except urllib.error.HTTPError as error:
                body = json.load(error)
                result["http_error"] = {"status": error.code, "code": body.get("code")}
                raise RuntimeError("PACKAGED_API_REJECTED") from None

        status, host = get("/v1/host")
        assert status == 200 and host["backend_pid"] == process.pid and str(host["backend_build"]) == build
        status, account = get("/v1/codex-account", host["host_id"])
        assert status == 200 and account["account"] is None
        result["account_http"] = status
        status, models = get("/v1/models", host["host_id"])
        assert status == 200 and models["models"] and models["authentication"] == {"required": True, "configured": False}
        result.update(models_http=status, model_count=len(models["models"]), no_anycli_home=not (home / ".anycli").exists(), status="passed")
        assert result["no_anycli_home"]
    except Exception as error:
        result.update(status="failed", error_type=type(error).__name__, error=str(error))
    finally:
        if process:
            owned |= descendants(process.pid)
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
            try:
                result["exit_code"] = process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                result["exit_code"] = None
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and owned.intersection(process_table()):
                time.sleep(0.05)
            result["still_alive"] = sorted(owned.intersection(process_table()))
            result["normal_exit_confirmed"] = result["exit_code"] == 0 and not result["still_alive"]
            if not result["normal_exit_confirmed"]:
                result["status"] = "failed"
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False))
    return result.get("status") == "passed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", type=Path)
    parser.add_argument("--architecture", required=True, choices=["x86_64", "arm64"])
    parser.add_argument("--build", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if verify(args.app, args.architecture, args.build, args.out) else 1)
