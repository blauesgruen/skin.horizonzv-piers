"""Visible native Kodi argument probe using a prepared isolated skin fixture.

Requires --context pointing to the private preparation JSON. Never runs an addon;
SetProperty captures the argument after Kodi's native label expansion/parser.
"""

import argparse
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    args = parser.parse_args()
    context = json.loads(args.context.read_text(encoding="utf-8"))
    if context.get("probe") == "dialog_context":
        from dialog_context_probe import run
        return run(context, args.context)
    repo, root, work = (Path(context[k]).resolve() for k in ("repo", "root", "work"))
    assert repo == Path(__file__).resolve().parents[2]
    assert root.name == "horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440"
    assert work.parent == root and args.context.resolve().parent == work
    xml = root / "portable_data/addons/skin.horizonzv/xml"
    fixture = Path(context["fixture"]).resolve()
    assert fixture == xml / "Custom_1197_ArgumentAudit.xml"
    existing = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command",
         "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert existing.stdout.strip() == "0", "Kodi already running; do not interfere."
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient

    def wait_value(probe, expected, attempts=40):
        for _ in range(attempts):
            value = probe()
            if value == expected:
                return value
            time.sleep(0.1)
        raise AssertionError((value, expected))

    def label(name):
        return rpc("XBMC.GetInfoLabels", {"labels": [name]})["result"][name]

    def quote(value):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (repo / "xml").glob("*.xml")}
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 1
    process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"],
                               cwd=root, startupinfo=startup)
    client = None
    report = {"scope": "Native argument round-trip, not an ExtendedInfo execution test.",
              "process_id": process.pid, "rows": []}
    cleanup = {}
    error = None
    try:
        for _ in range(30):
            try:
                rpc("JSONRPC.Ping")
                break
            except Exception:
                if process.poll() is not None:
                    raise RuntimeError("Kodi exited before RPC became ready")
                time.sleep(0.5)
        client = XBMCClient(name="HorizonzV argument audit", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(0.1)
        client.send_action("ActivateWindow(1197)")
        wait_value(lambda: rpc("GUI.GetProperties", {"properties": ["currentwindow"]})
                   ["result"]["currentwindow"]["id"], 11197)
        cases = [
            ("comma", "Alpha, Beta", "Album, Part II", "Movie, Part Two", "2024"),
            ("quotes_slashes", '"A" \\ Band', 'Album "B"', '"C" \\ Cut', "2024"),
            ("unicode_equals", "Björk 東京", "Álbum = Δ", "人間の条件", "2024"),
            ("empty", "", "", "", ""),
        ]
        for case, artist, album, title, year in cases:
            values = dict(Artist=artist, Album=album, Title=title, Year=year)
            for name, value in values.items():
                client.send_action("SetProperty(HorizonAudit." + name + "," + quote(value) + ",home)")
                wait_value(lambda n=name: label("Window(Home).Property(HorizonAudit." + n + ")"), value)
            for index, expected in enumerate([artist + " " + album, artist + " " + title, title + " " + year]):
                wait_value(lambda i=index: label("Control.GetLabel(" + str(2001 + i) + ")"), expected)
                for revised in (False, True):
                    cid = 1001 + index * 2 + int(revised)
                    client.send_action("ClearProperty(HorizonAudit.Result)")
                    wait_value(lambda: label("Window.Property(HorizonAudit.Result)"), "")
                    client.send_action("Control.SetFocus(" + str(cid) + ")")
                    wait_value(lambda: rpc("XBMC.GetInfoBooleans", {
                        "booleans": ["Control.HasFocus(" + str(cid) + ")"]})
                        ["result"]["Control.HasFocus(" + str(cid) + ")"], True)
                    rpc("Input.Select")
                    time.sleep(0.25)
                    actual = label("Window.Property(HorizonAudit.Result)")
                    row = dict(case=case, family=index, revised=revised,
                               expected="id=" + expected, actual=actual)
                    row["matches"] = actual == row["expected"]
                    report["rows"].append(row)
                    if revised:
                        assert row["matches"], row
            client.send_action("Control.SetFocus(1007)")
            time.sleep(0.15)
            rpc("Input.Select")
            time.sleep(0.25)
            actual = label("Window.Property(HorizonAudit.Result)")
            row = dict(case=case, family="single", revised=True,
                       expected="name=" + title, actual=actual, matches=actual == "name=" + title)
            report["rows"].append(row)
            assert row["matches"], row
        report["revised_cases_passed"] = sum(r["revised"] and r["matches"] for r in report["rows"])
        report["comma_baseline_failures"] = sum(r["case"] == "comma" and not r["revised"]
                                               and not r["matches"] for r in report["rows"])
        assert report["comma_baseline_failures"] == 3
        screenshot = repo / "results/kodi22_runtime/argument_escape_native.png"
        client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
        wait_value(screenshot.exists, True)
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
            fixture.unlink(missing_ok=True)
            shutil.copy2(repo / "xml/Variables.xml", xml / "Variables.xml")
            for rel in ["userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml"]:
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            source = {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
            copied = {p.name: p.read_bytes() for p in xml.glob("*.xml")}
            cleanup["all_test_xml_match_production"] = source == copied
            cleanup["xml_count"] = len(source)
            cleanup["fixture_removed"] = not fixture.exists()
            cleanup["profile_baseline_restored"] = all(
                (work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes()
                for rel in ["userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml"])
        cleanup["production_xml_hashes_unchanged"] = hashes == {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/argument_escape_native_checks.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"failure": error, "revised_cases_passed": report.get("revised_cases_passed"),
                      "comma_baseline_failures": report.get("comma_baseline_failures"), "cleanup": cleanup}))
    return 1 if error or not all(cleanup.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
