"""Observe native item context across the skin's existing Close action.

Only an isolated copy redirects ExtendedInfo dispatch to a property capture.
Authored music is scanned into a backed-up isolated database, restored on exit.
"""
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path


def run(context, context_path):
    repo, root, work = (Path(context[k]).resolve() for k in ("repo", "root", "work"))
    assert repo == Path(__file__).resolve().parents[2]
    assert root.name == "horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440"
    assert work.parent == root and context_path.resolve().parent == work
    existing = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command",
         "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert existing.stdout.strip() == "0", "Kodi already running; do not interfere"
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient

    def wait(probe, expected, attempts=100):
        for _ in range(attempts):
            value = probe()
            if value == expected:
                return value
            time.sleep(.1)
        raise AssertionError({"actual": value, "expected": expected})

    def labels(names):
        return rpc("XBMC.GetInfoLabels", {"labels": names})["result"]

    def label(name):
        return labels([name])[name]

    def boolean(name):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [name]})["result"][name]

    def window():
        return rpc("GUI.GetProperties", {"properties": ["currentwindow"]})["result"]["currentwindow"]["id"]

    xml = root / "portable_data/addons/skin.horizonzv/xml"
    database = root / "portable_data/userdata/Database"
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (repo / "xml").glob("*.xml")}
    report = {"scope": "Native movie/album/song item context after production Close; addon dispatch captured, addon not executed", "rows": []}
    cleanup = {}
    client = None
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 1
    process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
    report["process_id"] = process.pid
    error = None
    try:
        for _ in range(60):
            try:
                rpc("JSONRPC.Ping")
                break
            except Exception:
                assert process.poll() is None, "Kodi exited during startup"
                time.sleep(.5)
        client = XBMCClient(name="HorizonzV dialog context audit", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        rpc("AudioLibrary.Scan", {"directory": context["media"], "showdialogs": False})
        wait(lambda: bool(rpc("AudioLibrary.GetSongs", {"properties": ["title"]})["result"].get("songs")), True, 300)
        for kind, target, path, dialog in [
            ("movie", "videos", "videodb://movies/titles/", 12003),
            ("album", "music", "musicdb://albums/", 12001),
            ("song", "music", "musicdb://songs/", 10135),
        ]:
            rpc("GUI.ActivateWindow", {"window": target, "parameters": [path, "return"]})
            time.sleep(.6)
            client.send_action("Container.SetViewMode(50)")
            client.send_action("Control.SetFocus(50)")
            wait(lambda: boolean("Control.HasFocus(50)"), True)
            for _ in range(10):
                if label("ListItem.DBType") == kind:
                    break
                rpc("Input.Down")
                time.sleep(.15)
            assert label("ListItem.DBType") == kind, labels(["ListItem.DBType", "ListItem.Label"])
            rpc("Input.ExecuteAction", {"action": "info"})
            wait(window, dialog)
            time.sleep(.4)
            before = labels(["ListItem.DBType", "ListItem.Artist", "ListItem.Album", "ListItem.Title", "ListItem.Year"])
            assert before["ListItem.DBType"] == kind, before
            if kind == "movie" and boolean("Control.IsVisible(11)"):
                client.send_action("Control.SetFocus(5)")
                wait(lambda: boolean("Control.HasFocus(5)"), True)
                rpc("Input.Select")
                wait(lambda: boolean("Control.IsVisible(11)"), False)
            wait(lambda: boolean("Control.IsVisible(440)"), True)
            client.send_action("ClearProperty(HorizonAudit.ContextResult,home)")
            wait(lambda: label("Window(Home).Property(HorizonAudit.ContextResult)"), "")
            client.send_action("Control.SetFocus(440)")
            wait(lambda: boolean("Control.HasFocus(440)"), True)
            screenshot = repo / ("results/kodi22_runtime/dialog_context_" + kind + ".png")
            client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
            wait(screenshot.exists, True)
            expected = "id=" + (before["ListItem.Title"] + " " + before["ListItem.Year"] if kind == "movie" else before["ListItem.Artist"] + " " + before["ListItem.Album" if kind == "album" else "ListItem.Title"])
            rpc("Input.Select")
            wait(lambda: bool(label("Window(Home).Property(HorizonAudit.ContextResult)")), True)
            actual = label("Window(Home).Property(HorizonAudit.ContextResult)")
            row = {"kind": kind, "before": before, "expected": expected, "actual": actual, "matches": actual == expected}
            report["rows"].append(row)
            print(json.dumps(row, ensure_ascii=True), flush=True)
            assert row["matches"], row
            wait(lambda: window() != dialog, True)
    except Exception as exc:
        error = repr(exc)
        report["failure"] = error
    finally:
        if client:
            client.close()
        try:
            rpc("Application.Quit")
        except Exception:
            pass
        try:
            process.wait(timeout=20)
            cleanup["process_exited"] = True
        except subprocess.TimeoutExpired:
            cleanup["process_exited"] = False
        if cleanup["process_exited"]:
            for name in ("DialogMusicInfo.xml", "DialogVideoInfo.xml"):
                shutil.copy2(repo / "xml" / name, xml / name)
            for rel in ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml"):
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            for p in database.glob("MyMusic*.db*"):
                assert p.resolve().parent == database.resolve()
                p.unlink()
            for p in (work / "database").iterdir():
                assert p.name in context["music_db_files"]
                shutil.copy2(p, database / p.name)
            cleanup["music_database_restored"] = sorted(p.name for p in database.glob("MyMusic*.db*")) == sorted(context["music_db_files"]) and all(p.read_bytes() == (database / p.name).read_bytes() for p in (work / "database").iterdir())
            cleanup["profile_baseline_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml"))
            cleanup["all_test_xml_match_production"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        cleanup["production_xml_unchanged"] = hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/dialog_context_checks.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"failure": error, "passed": len(report["rows"]), "cleanup": cleanup}), flush=True)
    return int(bool(error) or not all(cleanup.values()))
