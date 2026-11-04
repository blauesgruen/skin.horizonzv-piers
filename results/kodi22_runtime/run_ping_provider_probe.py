"""Visible WOL status integration with unchanged provider and localhost fixtures.

Never selects a device or calls WakeOnLan. Test MACs are all empty; provider
background service remains disabled. Only the isolated profile is configured.
"""
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    source = repo.parent / "script.skinhelper.ping"
    target = root / "portable_data/addons/script.skinhelper.ping"
    assert not target.exists(), "First-run preparation requires absent isolated provider"
    files = [p for p in source.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git", "__pycache__", ".codex"))]
    hashes = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        dest = target / p.relative_to(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    work = Path(tempfile.mkdtemp(prefix="review-real-ping-", dir=root))
    settings = root / "portable_data/userdata/addon_data/script.skinhelper.ping/settings.xml"
    assert not settings.exists()
    settings.parent.mkdir(parents=True, exist_ok=True)
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    xml = root / "portable_data/addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient

    def label(name):
        return rpc("XBMC.GetInfoLabels", {"labels": [name]})["result"][name]

    def prop(name):
        return label("Window(Home).Property(SkinHelperPING." + name + ")")

    def wait(probe, expected, attempts=120):
        for _ in range(attempts):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})

    def items():
        n = int(label("Container(36110).NumItems"))
        result = []
        for i in range(n):
            names = [f"Container(36110).ListItemAbsolute({i})." + key for key in ("Label", "Label2", "Property(number)", "Property(mac)")]
            result.append(rpc("XBMC.GetInfoLabels", {"labels": names})["result"])
        return result

    report = {"scope": "Unchanged Ping 4.1.2, real loopback status through production WOL onload; no WOL action", "phases": [], "source_hashes": hashes}
    failure = None
    all_exited = True
    try:
        for phase, slots in [("two", [1, 10]), ("one", [1])]:
            config = ET.Element("settings", {"version": "2"})
            for slot in range(1, 11):
                for key in ("name", "ip", "mac"):
                    e = ET.SubElement(config, "setting", {"id": key + str(slot)})
                    e.text = ("Audit Loopback " + str(slot) if key == "name" else "127.0.0.1" if key == "ip" else "") if slot in slots else ""
            ET.SubElement(config, "setting", {"id": "service"}).text = "false"
            ET.ElementTree(config).write(settings, encoding="utf-8", xml_declaration=True)
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = 1
            process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
            client = None
            try:
                for _ in range(60):
                    try:
                        rpc("JSONRPC.Ping")
                        break
                    except Exception:
                        assert process.poll() is None
                        time.sleep(.3)
                assert rpc("Addons.SetAddonEnabled", {"addonid": "script.skinhelper.ping", "enabled": True}).get("result") == "OK"
                client = XBMCClient(name="HorizonzV real Ping status", uid=secrets.randbits(32))
                client.connect(port=9777)
                time.sleep(.2)
                # An authored stale slot must not survive a real dialog load.
                for key in ("servername5", "ip5"):
                    client.send_action("SetProperty(SkinHelperPING." + key + ",Audit stale slot,home)")
                client.send_action("ActivateWindow(1151)")
                wait(lambda: prop("servercount"), str(len(slots)))
                wait(lambda: prop("serveron"), str(len(slots)))
                wait(lambda: label("Container(36110).NumItems"), str(len(slots) + 2))
                assert prop("servername5") == "" and prop("ip5") == ""
                for slot in slots:
                    assert prop("server" + str(slot)) == "on"
                    assert prop("ip" + str(slot)) == "127.0.0.1"
                    assert prop("mac" + str(slot)) == ""
                if phase == "one":
                    assert prop("server10") == "" and prop("servername10") == ""
                rows = items()
                report["phases"].append({"phase": phase, "slots": slots, "servercount": prop("servercount"), "serveron": prop("serveron"), "items": rows, "stale_slot5_cleared": True})
                screenshot = repo / "results/kodi22_runtime" / ("ping_provider_" + phase + ".png")
                client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
                wait(screenshot.exists, True)
                if phase == "one":
                    client.send_action("Dialog.Close(1151)")
                    wait(lambda: rpc("GUI.GetProperties", {"properties": ["currentwindow"]})["result"]["currentwindow"]["id"] != 11151, True)
                    wait(lambda: rpc("Addons.SetAddonEnabled", {"addonid": "script.skinhelper.ping", "enabled": False}).get("result"), "OK")
                    client.send_action("SetProperty(SkinHelperPING.servername10,Audit stale ten,home)")
                    client.send_action("ActivateWindow(1151)")
                    wait(lambda: label("Container(36110).NumItems"), "1")
                    wait(lambda: prop("servercount"), "")
                    assert prop("servername10") == ""
                    report["phases"].append({"phase": "disabled", "items": items(), "servercount": prop("servercount"), "stale_slot10_cleared": True})
                    rpc("Addons.SetAddonEnabled", {"addonid": "script.skinhelper.ping", "enabled": True})
            finally:
                if client:
                    client.close()
                try:
                    rpc("Application.Quit")
                    process.wait(timeout=20)
                except Exception:
                    pass
                exited = process.poll() is not None
                all_exited = all_exited and exited
                assert exited, "Owned Kodi still running; no offline writes allowed"
    except Exception as exc:
        failure = repr(exc)
        report["failure"] = failure
        report["failure_trace"] = traceback.format_exc()
    finally:
        cleanup = {"all_processes_exited": all_exited}
        if all_exited:
            for rel in rels:
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            assert settings.resolve().parent == (root / "portable_data/userdata/addon_data/script.skinhelper.ping").resolve()
            settings.unlink(missing_ok=True)
            cleanup["test_provider_settings_removed"] = not settings.exists()
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
            cleanup["all_test_xml_match_production"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        cleanup["standard_provider_sources_unchanged"] = all(hashlib.sha256((source / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        cleanup["test_provider_sources_match_original"] = all(hashlib.sha256((target / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/ping_provider_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
