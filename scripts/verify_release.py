"""Build and verify local release images without changing active demo volumes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/release")
    parser.add_argument("--model-cache-volume", help="Reuse a populated model cache read-only; otherwise init downloads weights")
    parser.add_argument("--port", type=int, default=8502)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if (output / "verification.json").exists():
        parser.error("Choose a new output directory to preserve the earlier verification.")
    project = "unihybrid-release-" + uuid4().hex[:8]
    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "status": "in_progress",
              "compose_project": project, "checks": [],
              "model_cache": "existing read-only cache" if args.model_cache_volume else "new volume; network required",
              "human_review": "separate mandatory gate; this script does not complete it"}

    def run(label, command):
        with (output / f"{label}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, text=True)
        report["checks"].append({"check": label, "exit_code": result.returncode})
        print(f"{label}: exit {result.returncode}", flush=True)
        if result.returncode:
            raise RuntimeError(f"{label} failed; see {output / (label + '.log')}")

    def inspect(image):
        data = json.loads(subprocess.check_output(["docker", "image", "inspect", image], text=True))[0]
        return {"tag": image, "id": data["Id"], "os": data["Os"], "architecture": data["Architecture"],
                "user": data["Config"]["User"], "size_bytes": data["Size"]}

    compose = None
    try:
        run("docker-version", ["docker", "version"])
        run("runtime-build", ["docker", "build", "--target", "runtime", "-t", "unihybrid-ai:1.0.0", "-t", "unihybrid-ai:phase-08", "."])
        run("test-build", ["docker", "build", "--target", "test", "-t", "unihybrid-ai-test:1.0.0", "-t", "unihybrid-ai-test:phase-08", "."])
        report["runtime_image"] = inspect("unihybrid-ai:1.0.0")
        report["test_image"] = inspect("unihybrid-ai-test:1.0.0")
        run("runtime-permissions", ["docker", "run", "--rm", "unihybrid-ai:1.0.0", "python", "-m", "scripts.check_container"])
        report["base_image"] = next(line.split("=", 1)[1] for line in (ROOT / "Dockerfile").read_text().splitlines() if line.startswith("ARG PYTHON_IMAGE="))
        model_mount = {"type": "volume", "source": "models", "target": "/app/model-cache",
                       "read_only": bool(args.model_cache_volume)}
        runtime = {"image": "unihybrid-ai:1.0.0", "environment": {
            "GEMINI_API_KEY": "", "DATA_DIR": "/app/state/release-check-state", "LOGS_DIR": "/app/logs",
            "MODEL_CACHE": "/app/model-cache", "CURRENT_TERM": "2026-FALL",
            "HF_HUB_OFFLINE": "1" if args.model_cache_volume else "0"},
            "volumes": ["data:/app/state", "logs:/app/logs", model_mount]}
        configuration = {"services": {
            "init": {**runtime, "command": ["python", "-m", "scripts.ingest_docs"]},
            "app": {**runtime, "ports": [f"127.0.0.1:{args.port}:8501"]},
            "test": {"image": "unihybrid-ai-test:1.0.0", "environment": {"GEMINI_API_KEY": "", "HF_HUB_OFFLINE": "1"},
                     "volumes": [{**model_mount, "read_only": True}]}},
            "volumes": {"data": {}, "logs": {}, "models": {"external": True, "name": args.model_cache_volume} if args.model_cache_volume else {}}}
        config_file = output / "compose.json"
        config_file.write_text(json.dumps(configuration, indent=2), encoding="utf-8")
        compose = ["docker", "compose", "-p", project, "-f", str(config_file)]
        run("compose-config", [*compose, "config", "--quiet"])
        run("fresh-init", [*compose, "run", "--rm", "init"])
        run("container-tests", [*compose, "run", "--rm", "test"])
        run("runtime-probe", [*compose, "run", "--rm", "app", "python", "-m", "scripts.release_probe", "initial"])
        run("fresh-ui-start", [*compose, "up", "-d", "app"])

        def health(label):
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                try:
                    with urlopen(f"http://127.0.0.1:{args.port}/_stcore/health", timeout=2) as response:
                        if response.status == 200 and response.read() == b"ok":
                            report["checks"].append({"check": label, "http_status": 200})
                            return
                except OSError:
                    pass
                time.sleep(1)
            raise RuntimeError(f"{label}: health timeout")

        health("fresh-ui-health")
        run("restart-init", [*compose, "run", "--rm", "init"])
        run("ui-restart", [*compose, "restart", "app"])
        health("restarted-ui-health")
        run("persistence-probe", [*compose, "exec", "-T", "app", "python", "-m", "scripts.release_probe", "restart"])
        run("dependencies", [*compose, "exec", "-T", "app", "python", "-m", "pip", "freeze"])
        run("source-identity", [*compose, "exec", "-T", "app", "python", "-c",
            "from pathlib import Path; from src.evaluation.reporting import run_metadata; import json; print(json.dumps(run_metadata(Path('evaluation/eval_set.json'), 'offline', None)))"])
        archive = output / "unihybrid-ai-1.0.0.tar"
        run("archive-export", ["docker", "save", "-o", str(archive), "unihybrid-ai:1.0.0"])
        checksum = digest(archive)
        checksum_file = archive.with_suffix(".tar.sha256")
        checksum_file.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
        assert digest(archive) == checksum_file.read_text().split()[0], "Archive checksum mismatch"
        run("archive-load", ["docker", "load", "-i", str(archive)])
        loaded = inspect("unihybrid-ai:1.0.0")
        assert loaded["id"] == report["runtime_image"]["id"], "Loaded image identity mismatch"
        run("loaded-image-smoke", [*compose, "run", "--rm", "app", "python", "-m", "scripts.release_probe", "restart"])
        report["archive"] = {"path": str(archive), "sha256": checksum, "size_bytes": archive.stat().st_size,
                             "loaded_image_id": loaded["id"]}
        report["status"] = "automated_release_checks_passed"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        print(str(exc), flush=True)
    finally:
        if compose:
            try:
                run("scratch-stop", [*compose, "down"])
            except RuntimeError as exc:
                report["status"] = "failed"
                report["cleanup_error"] = str(exc)
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (output / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["status"] == "automated_release_checks_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
