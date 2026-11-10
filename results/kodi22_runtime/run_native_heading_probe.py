"""Visible native numeric/settings heading contracts in the actual skin XML."""
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
    if baseline:
        for name in ("DialogNumeric.xml", "DialogSettings.xml"):
            params = ET.parse(repo / "xml" / name).findall(".//include[@content='DialogBackgroundCommons']/param[@name='header_id']")
            assert len(params) == 1 and params[0].get("value") == "0", "Baseline requires the original uncorrected XML; preserve recorded baseline."
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-native-headings-", dir=root))
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
        result = raw_rpc(method, params)
        assert "result" in result, result
        return result["result"]

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

    def screenshot(kind):
        path = repo / "results/kodi22_runtime" / ("native_heading_" + kind + ("_before" if baseline else "_fixed") + ".png")
        path.unlink(missing_ok=True)
        time.sleep(.3)
        client.send_action('TakeScreenshot("' + path.as_posix() + '")')
        wait(path.exists, True)

    report = {"scope": "Actual numeric dialog (four modes) and three shared native settings dialogs; titles, focus, number entry/backspace/confirmation and cancellation only. No player, persistent device settings or addon code changed.", "baseline": baseline, "work": str(work), "xml_sha256": {name: hashlib.sha256((repo / "xml" / name).read_bytes()).hexdigest() for name in ("DialogNumeric.xml", "DialogSettings.xml")}, "numeric": [], "settings": []}
    process = client = None
    active_numeric_output = None
    failure = None
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
        client = XBMCClient(name="HorizonzV native headings", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.5)
        wait(lambda: boolean("Window.IsActive(home)"), True)
        localized = work / "localized.json"
        localization_script = work / "localize.py"
        localization_script.write_text("import xbmc,json\nfrom pathlib import Path\nPath(" + repr(str(localized)) + ").write_text(json.dumps({str(i):xbmc.getLocalizedString(i) for i in (13396,13395,24133)}),encoding='utf-8')\n", encoding="utf-8")
        client.send_action('RunScript("' + localization_script.as_posix() + '")')
        wait(localized.exists, True)
        localization = json.loads(localized.read_text(encoding="utf-8"))
        for mode, default in ((0, "12"), (1, "04/11/2026"), (2, "12:34"), (3, "127.0.0.1")):
            heading = "HorizonzV native input " + str(mode)
            output = work / ("numeric-" + str(mode) + ".json")
            active_numeric_output = output
            script = work / "numeric.py"
            script.write_text("import xbmcgui,json\nfrom pathlib import Path\nr=xbmcgui.Dialog().numeric(" + repr(mode) + "," + repr(heading) + "," + repr(default) + ")\nPath(" + repr(str(output)) + ").write_text(json.dumps({'result':r}),encoding='utf-8')\n", encoding="utf-8")
            client.send_action('RunScript("' + script.as_posix() + '")')
            wait(lambda: boolean("Window.IsVisible(numericinput)"), True)
            time.sleep(.4)
            observed = labels("Control.GetLabel(1)", "Control.GetLabel(4)", "System.CurrentControlID", "Skin.AspectRatio")
            row = {"mode": mode, "expected_heading": heading, "observed": observed}
            report["numeric"].append(row)
            if mode == 0:
                screenshot("numeric")
            if not baseline:
                assert observed["Control.GetLabel(1)"] == heading, row
                assert observed["System.CurrentControlID"] == "21", row
            if mode == 0 and not baseline:
                client.send_action("Control.SetFocus(13)")
                time.sleep(.1)
                rpc("Input.Select")
                client.send_action("Control.SetFocus(14)")
                time.sleep(.1)
                rpc("Input.Select")
                client.send_action("Control.SetFocus(23)")
                time.sleep(.1)
                rpc("Input.Select")
                time.sleep(.2)
                row["after_digit_and_backspace"] = labels("Control.GetLabel(4)")["Control.GetLabel(4)"]
                assert row["after_digit_and_backspace"] == "123", row
                client.send_action("Control.SetFocus(21)")
                time.sleep(.1)
                rpc("Input.Select")
            else:
                rpc("Input.Back")
            wait(lambda: boolean("Window.IsVisible(numericinput)"), False)
            wait(output.exists, True)
            active_numeric_output = None
            row["returned"] = json.loads(output.read_text(encoding="utf-8"))["result"]
            assert row["returned"] == ("123" if mode == 0 and not baseline else ""), row
        for target, string_id in (("osdaudiosettings", 13396), ("osdvideosettings", 13395), ("osdsubtitlesettings", 24133)):
            client.send_action("ActivateWindow(" + target + ")")
            wait(lambda: boolean("Window.IsVisible(" + target + ")"), True)
            time.sleep(.5)
            observed = labels("Control.GetLabel(2)", "System.CurrentControlID", "Skin.AspectRatio")
            row = {"target": target, "observed": observed, "expected_heading": localization[str(string_id)], "heading_string_id": string_id}
            report["settings"].append(row)
            if target == "osdaudiosettings":
                screenshot("settings")
            if not baseline:
                assert observed["Control.GetLabel(2)"] == row["expected_heading"] and row["expected_heading"], row
            rpc("Input.Back")
            wait(lambda: boolean("Window.IsVisible(" + target + ")"), False)
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                rpc("Input.Back")
                if active_numeric_output is not None:
                    wait(active_numeric_output.exists, True)
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
        name = "native_heading_before.json" if baseline else "native_heading_checks.json"
        (repo / "results/kodi22_runtime" / name).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "numeric": report["numeric"], "settings": report["settings"], "errors": report["errors"], "cleanup": cleanup}))
    return int(bool(failure) or not all(cleanup.values()) or bool(report["errors"]))


if __name__ == "__main__":
    sys.exit(main())
