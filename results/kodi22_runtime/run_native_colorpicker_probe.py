"""Visible native Kodi color-dialog contract check; no external picker invocation."""
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
    baseline = "--baseline" in sys.argv
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    count = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert count.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-native-colorpicker-", dir=root))
    profile = root / "portable_data"
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml", "userdata/addon_data/script.cu.lrclyrics/settings.xml")
    backups = {rel: (profile / rel).read_bytes() if (profile / rel).exists() else None for rel in rels}
    for index, data in enumerate(backups.values()):
        if data is not None:
            (work / f"settings-{index}.xml").write_bytes(data)
    skin_xml = profile / "addons/skin.horizonzv/xml"
    for path in (repo / "xml").glob("*.xml"):
        shutil.copy2(path, skin_xml / path.name)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        data = raw_rpc(method, params)
        assert "result" in data, data
        return data["result"]

    def wait(probe, expected, attempts=120):
        for _ in range(attempts):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def labels(*names):
        return rpc("XBMC.GetInfoLabels", {"labels": list(names)})

    def value():
        return labels("Skin.String(HorizonzVNativeColorProbe)")["Skin.String(HorizonzVNativeColorProbe)"]

    def snapshot():
        return labels("Container(6).NumItems", "Container(6).ListItem.Label", "Container(6).ListItem.Label2", "System.CurrentControlID", "Control.GetLabel(1)", "Control.GetLabel(20)", "Skin.AspectRatio")

    def screenshot(suffix):
        path = repo / "results/kodi22_runtime" / ("native_colorpicker_" + suffix + ".png")
        path.unlink(missing_ok=True)
        time.sleep(.4)
        client.send_action('TakeScreenshot("' + path.as_posix() + '")')
        wait(path.exists, True)

    report = {"scope": "Native Skin.SetColor through the actual skin DialogColorPicker.xml. Isolated setting, default Kodi palette, selection/preselection/cancel/reopening. External skin helper action is unchanged.", "baseline": baseline, "xml_sha256": hashlib.sha256((repo / "xml/DialogColorPicker.xml").read_bytes()).hexdigest(), "phases": [], "work": str(work)}
    process = client = None
    failure = None
    dialog = "Window.IsVisible(dialogcolorpicker)"
    try:
        gui = ET.parse(profile / rels[0])
        for name, text in {"lookandfeel.skin": "skin.horizonzv", "window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            item = gui.getroot().find(f"setting[@id='{name}']")
            assert item is not None, name
            item.text = text
            item.attrib.pop("default", None)
        gui.write(profile / rels[0], encoding="utf-8", xml_declaration=True)
        cu = ET.parse(profile / rels[2]) if backups[rels[2]] else ET.ElementTree(ET.Element("settings", {"version": "2"}))
        service = cu.getroot().find("setting[@id='service']")
        if service is None:
            service = ET.SubElement(cu.getroot(), "setting", {"id": "service"})
        service.text = "false"
        service.attrib.pop("default", None)
        cu.write(profile / rels[2], encoding="utf-8", xml_declaration=True)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        report["pid"] = process.pid
        for _ in range(90):
            try:
                rpc("JSONRPC.Ping")
                break
            except Exception:
                assert process.poll() is None
                time.sleep(.2)
        client = XBMCClient(name="HorizonzV native colorpicker", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.5)
        wait(lambda: boolean("Window.IsActive(home)"), True)
        client.send_action("Skin.SetString(HorizonzVNativeColorProbe,FF123456)")
        wait(value, "FF123456")
        for phase in (("baseline",) if baseline else ("cancel", "select", "preselect_cancel", "cancel_button")):
            before = value()
            client.send_action("Skin.SetColor(HorizonzVNativeColorProbe,737)")
            wait(lambda: boolean(dialog), True)
            time.sleep(.6)
            entry = snapshot()
            row = {"phase": phase, "before": before, "dialog": entry}
            report["phases"].append(row)
            if baseline:
                screenshot("before")
                rpc("Input.Back")
            else:
                screenshot("observed")
                assert int(entry["Container(6).NumItems"]) == len(ET.parse(root / "system/dialogcolors.xml").findall("color")), entry
                assert entry["System.CurrentControlID"] == "6", entry
                assert entry["Control.GetLabel(1)"], entry
                assert entry["Control.GetLabel(20)"], entry
                if phase == "select":
                    rpc("Input.Right")
                    time.sleep(.2)
                    chosen = snapshot()
                    row["chosen"] = chosen
                    screenshot("fixed")
                    rpc("Input.Select")
                    wait(value, chosen["Container(6).ListItem.Label2"])
                elif phase == "cancel_button":
                    client.send_action("Control.SetFocus(7)")
                    time.sleep(.2)
                    rpc("Input.Select")
                else:
                    if phase == "preselect_cancel":
                        assert entry["Container(6).ListItem.Label2"] == before, entry
                    rpc("Input.Back")
            wait(lambda: boolean(dialog), False)
            row["after"] = value()
            if phase != "select":
                assert row["after"] == before, row
        report["saved_color"] = value()
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                if boolean(dialog):
                    rpc("Input.Back")
                raw_rpc("Application.Quit")
                process.wait(timeout=25)
            except Exception:
                pass
        if client:
            client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():
                target = profile / rel
                if data is not None:
                    target.write_bytes(data)
                else:
                    target.unlink(missing_ok=True)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data if data is not None else not (profile / rel).exists() for rel, data in backups.items())
        cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in skin_xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        log = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [line for line in log if " error " in line.lower() or "fatal" in line.lower()]
        name = "native_colorpicker_before.json" if baseline else "native_colorpicker_checks.json"
        (repo / "results/kodi22_runtime" / name).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "phases": report["phases"], "errors": report["errors"], "cleanup": cleanup}))
    return int(bool(failure) or not all(cleanup.values()) or (not baseline and bool(report["errors"])))


if __name__ == "__main__":
    sys.exit(main())
