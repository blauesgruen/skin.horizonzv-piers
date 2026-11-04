"""Run existing positive CU probes and restore own music/addon DB snapshots."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    database = root / "portable_data/userdata/Database"
    def no_kodi():
        count = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return count.stdout.strip() == "0"
    assert no_kodi(), "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-lyrics-availability-regression-", dir=root))
    saved = work / "database"
    saved.mkdir()
    def files():
        return [p for p in database.iterdir() if p.is_file() and (p.name.startswith("Addons") or p.name.startswith("MyMusic")) and ".db" in p.name]
    backup = {p.name: p.read_bytes() for p in files()}
    for name, data in backup.items():
        (saved / name).write_bytes(data)
    report = {"scope": "Existing positive manual/background CU native probes against guarded skin XML; wrapper restores own music/addon DB snapshots.", "runs": [], "work": str(work)}
    try:
        for background in (False, True):
            prefix = "lyrics_availability_background" if background else "lyrics_availability_enabled"
            command = [sys.executable, str(repo / "results/kodi22_runtime/run_lyrics_visualisation_probe.py"), "--report-prefix", prefix]
            if background:
                command.append("--background-service")
            result = subprocess.run(command, capture_output=True, text=True)
            native = json.loads((repo / "results/kodi22_runtime" / (prefix + "_checks.json")).read_text(encoding="utf-8"))
            row = {"report": prefix + "_checks.json", "returncode": result.returncode, "failure": native.get("failure"), "shutdown_wait_failure": native.get("shutdown_wait_failure"), "errors": native.get("errors"), "cleanup": native.get("cleanup")}
            report["runs"].append(row)
            print(json.dumps({"run": prefix, "returncode": result.returncode, "failure": row["failure"], "errors": len(row["errors"])}), flush=True)
            assert result.returncode == 0, row
    finally:
        report["all_kodi_processes_exited"] = no_kodi()
        if report["all_kodi_processes_exited"]:
            extra = work / "new-database-files"
            extra.mkdir()
            for path in files():
                if path.name not in backup:
                    assert root.resolve() in path.resolve().parents and root.resolve() in extra.resolve().parents
                    path.rename(extra / path.name)
            for name, data in backup.items():
                (database / name).write_bytes(data)
            report["database_file_sets_and_bytes_restored"] = {p.name: p.read_bytes() for p in files()} == backup
        (repo / "results/kodi22_runtime/lyrics_availability_regression_restore.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    assert report.get("database_file_sets_and_bytes_restored")
    print("Both positive regressions passed; own DB snapshots restored.", flush=True)


if __name__ == "__main__":
    main()
