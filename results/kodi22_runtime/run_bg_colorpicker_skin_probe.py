"""Native BG addon invocation with the skin-owned compatible dialog."""
import hashlib
import json
import re
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
    reference = False
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    running = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert running.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-bg-skin-dialog-", dir=root))
    profile = root / "portable_data"
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    backups = {rel: (profile / rel).read_bytes() for rel in rels}
    for i, data in enumerate(backups.values()):
        (work / f"profile-{i}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    database_backup = {p.name:p.read_bytes() for p in database.iterdir() if p.is_file()}
    database_saved = work / "database"
    database_saved.mkdir()
    for name,data in database_backup.items(): (database_saved/name).write_bytes(data)
    addon = "script.skin.helper.colorpicker.bg"
    hashes = {}
    for p in (repo.parent / addon).rglob("*"):
        if not p.is_file() or any(x in p.parts for x in (".git", "__pycache__", ".codex")):
            continue
        rel = p.relative_to(repo.parent / addon)
        data = p.read_bytes()
        hashes[rel.as_posix()] = hashlib.sha256(data).hexdigest()
        target = profile / "addons" / addon / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == data, f"Existing provider copy differs: {rel}"
        else:
            target.write_bytes(data)
    xml = profile / "addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    source = ET.parse(repo / "xml/SkinSettings.xml").getroot().find(".//control[@id='824']")
    action = source.find("onclick").text
    assert action == "RunScript(script.skin.helper.colorpicker.bg,skinstring=MySkinColor)"
    layout = work / "resources/skins/Default/1080i"
    layout.mkdir(parents=True)
    win = ET.Element("window")
    ET.SubElement(win, "defaultcontrol", {"always": "true"}).text = "100"
    controls = ET.SubElement(win, "controls")
    button = ET.SubElement(controls, "control", {"type": "button", "id": "100"})
    for tag, text in {"left": "100", "top": "150", "width": "1500", "height": "90", "font": "font16", "label": "HorizonzV: Farbauswahl testen", "texturefocus": "White.png", "texturenofocus": "Black.png", "onclick": action}.items():
        ET.SubElement(button, tag).text = text
    ET.ElementTree(win).write(layout / "colorpicker_probe.xml", encoding="utf-8", xml_declaration=True)
    script = work / "colorpicker_probe.py"
    script.write_text("import xbmcgui\nfrom pathlib import Path\nclass Probe(xbmcgui.WindowXML):\n def onInit(self): self.setFocusId(100)\n def onAction(self,a):\n  if a.getId() in (9,10,92,216): self.close()\nw=Probe('colorpicker_probe.xml',str(Path(__file__).parent),'Default','1080i')\nw.doModal()\ndel w\n", encoding="utf-8")
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

    def labels(names):
        return rpc("XBMC.GetInfoLabels", {"labels": names})

    def state():
        names = [f"Skin.String(MySkinColor{k})" for k in ("", ".name", ".base")]
        values = labels(names)
        return {k: values[n] for k, n in zip(("value", "name", "base"), names)}

    dialog = "Window.IsVisible(script-skin_helper_service-ColorPicker.xml)"
    process = client = None
    failure = None
    report = {"scope": "Estuary direct addon-call reference; cancel only." if reference else "Copied SkinSettings control 824 action in a native WindowXML probe; actual unchanged BG colorpicker 1.0.1. Skin-owned override, including manual ARGB input, opacity and material palette; other palettes, unset initial state and mouse remain untested.", "action": action, "provider_hashes": hashes, "phases": []}
    try:
        gui = ET.parse(profile / "userdata/guisettings.xml")
        if reference:
            skin = gui.getroot().find("setting[@id='lookandfeel.skin']")
            assert skin is not None
            skin.text = "skin.estuary"
            skin.attrib.pop("default", None)
        for name, value in {"window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            setting = gui.getroot().find(f"setting[@id='{name}']")
            assert setting is not None, name
            setting.text = value
            setting.attrib.pop("default", None)
        gui.write(profile / "userdata/guisettings.xml", encoding="utf-8", xml_declaration=True)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        report["pid"] = process.pid
        for _ in range(60):
            try:
                rpc("JSONRPC.Ping")
                break
            except Exception:
                assert process.poll() is None
                time.sleep(.3)
        details = rpc("Addons.GetAddonDetails", {"addonid": addon, "properties": ["enabled", "version"]})["addon"]
        report["provider_version"] = details["version"]
        report["provider_previously_enabled"] = details["enabled"]
        assert details["version"] == "1.0.1"
        rpc("Addons.SetAddonEnabled", {"addonid": addon, "enabled": True})
        client = XBMCClient(name="HorizonzV colorpicker", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        if not reference:
            client.send_action('RunScript("' + script.as_posix() + '")')
            wait(lambda: boolean("Control.IsVisible(100)"), True)
        for key, value in (("MySkinColor", "ff123456"), ("MySkinColor.name", "Probe"), ("MySkinColor.base", "ff123456")):
            client.send_action(f"Skin.SetString({key},{value})")
            time.sleep(.15)
        baseline = {"value": "ff123456", "name": "Probe", "base": "ff123456"}
        wait(state, baseline)
        report["active_skin"] = labels(["Skin.CurrentTheme", "Skin.AspectRatio"])
        for phase in (("cancel",) if reference else ("cancel", "select_cancel", "select_save", "none")):
            before = state()
            if reference:
                client.send_action(action)
            else:
                client.send_action("Control.SetFocus(100)")
                time.sleep(.2)
                rpc("Input.Select")
            wait(lambda: boolean(dialog), True)
            wait(lambda: boolean("Control.IsVisible(3110)"), True)
            time.sleep(.4)
            if reference:
                screenshot = repo / "results/kodi22_runtime/bg_colorpicker_reference.png"
                screenshot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
                wait(screenshot.exists, True)
            if phase == "cancel":
                shot = repo / "results/kodi22_runtime/bg_colorpicker_dialog.png"
                shot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("' + shot.as_posix() + '")')
                wait(shot.exists, True)
                heading = labels(["Control.GetLabel(5000)"])["Control.GetLabel(5000)"]
                assert heading, "Missing provider/default heading"
                report["heading"] = heading
            chosen = None
            if phase.startswith("select_"):
                client.send_action("Control.SetFocus(3110)")
                time.sleep(.2)
                names = ["Container(3110).ListItem.Property(colorstring)", "Container(3110).ListItem.Label"]
                selected = labels(names)
                chosen = {"value": selected[names[0]], "name": selected[names[1]]}
                assert len(chosen["value"]) == 8, chosen
                rpc("Input.Select")
                wait(lambda: state()["value"], chosen["value"])
            if phase in ("cancel", "select_cancel"):
                rpc("Input.Back")
            else:
                client.send_action("Control.SetFocus(" + ("3011" if phase == "none" else "3012") + ")")
                time.sleep(.2)
                rpc("Input.Select")
            wait(lambda: boolean(dialog), False)
            time.sleep(.3)
            after = state()
            row = {"phase": phase, "before": before, "selected": chosen, "after": after}
            report["phases"].append(row)
            if phase in ("cancel", "select_cancel"):
                assert after == before, row
            elif phase == "select_save":
                assert after == {**chosen, "base": "ff" + chosen["value"][2:]}, row
                screenshot = repo / "results/kodi22_runtime/bg_colorpicker_saved.png"
                screenshot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
                wait(screenshot.exists, True)
            else:
                assert after["value"] == "None" and not after["base"], row
        def open_picker():
            client.send_action("Control.SetFocus(100)")
            wait(lambda: boolean("Control.HasFocus(100)"), True)
            rpc("Input.Select")
            wait(lambda: boolean(dialog), True)
            wait(lambda: boolean("Control.IsVisible(3110)"), True)
            time.sleep(.3)

        open_picker()
        client.send_action("Control.SetFocus(3010)")
        wait(lambda: boolean("Control.HasFocus(3010)"), True)
        rpc("Input.Select")
        wait(lambda: boolean("Window.IsVisible(virtualkeyboard)"), True)
        rpc("Input.SendText", {"text": "80446688", "done": True})
        wait(lambda: boolean("Window.IsVisible(virtualkeyboard)"), False)
        wait(lambda: state()["value"], "80446688")
        client.send_action("Control.SetFocus(3012)")
        wait(lambda: boolean("Control.HasFocus(3012)"), True)
        rpc("Input.Select")
        wait(lambda: boolean(dialog), False)
        manual = state()
        assert manual["value"] == "80446688" and manual["base"] == "ff446688" and manual["name"], manual
        report["phases"].append({"phase": "manual_input_save", "after": manual})

        open_picker()
        before_opacity = state()
        client.send_action("Control.SetFocus(3015)")
        wait(lambda: boolean("Control.HasFocus(3015)"), True)
        rpc("Input.Right")
        wait(lambda: state()["value"] != before_opacity["value"], True)
        changed_opacity = state()
        assert changed_opacity["value"][2:] == before_opacity["value"][2:] and len(changed_opacity["value"]) == 8, changed_opacity
        rpc("Input.Back")
        wait(lambda: boolean(dialog), False)
        wait(state, before_opacity)
        report["phases"].append({"phase": "opacity_change_cancel", "before": before_opacity, "changed": changed_opacity, "after": state()})

        open_picker()
        before_palette = state()
        wait(lambda: labels(["Container(3110).NumItems"])["Container(3110).NumItems"], "126")
        client.send_action("Control.SetFocus(3030)")
        wait(lambda: boolean("Control.HasFocus(3030)"), True)
        rpc("Input.Select")
        wait(lambda: boolean("Window.IsVisible(12000)"), True)
        rpc("Input.Down")
        wait(lambda: labels(["Container(3).ListItem.Label"])["Container(3).ListItem.Label"], "material-design")
        rpc("Input.Select")
        wait(lambda: boolean("Window.IsVisible(12000)"), False)
        wait(lambda: labels(["Container(3110).NumItems"])["Container(3110).NumItems"], "266")
        time.sleep(.4)
        shot = repo / "results/kodi22_runtime/bg_colorpicker_material.png"
        shot.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + shot.as_posix() + '")')
        wait(shot.exists, True)
        rpc("Input.Back")
        wait(lambda: boolean(dialog), False)
        wait(state, before_palette)
        report["phases"].append({"phase": "material_palette_cancel", "source_colors": 126, "target_colors": 266, "after": state()})
        report["aspect"] = labels(["Skin.AspectRatio"])
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                if "provider_previously_enabled" in report:
                    rpc("Addons.SetAddonEnabled", {"addonid": addon, "enabled": report["provider_previously_enabled"]})
                raw_rpc("Application.Quit")
                process.wait(timeout=25)
            except Exception:
                pass
        if client:
            client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():
                (profile / rel).write_bytes(data)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            extra = work / "new-database-files"
            extra.mkdir()
            for path in database.iterdir():
                if path.is_file() and path.name not in database_backup: path.rename(extra/path.name)
            for name,data in database_backup.items(): (database/name).write_bytes(data)
            cleanup["all_database_files_restored"] = {p.name:p.read_bytes() for p in database.iterdir() if p.is_file()} == database_backup
        cleanup["standard_provider_unchanged"] = all(hashlib.sha256((repo.parent / addon / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        cleanup["test_provider_unchanged"] = all(hashlib.sha256((profile / "addons" / addon / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        log = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["error_lines"] = [s for s in log if " error " in s.lower() or "fatal" in s.lower()]
        report["skin_load_log"] = [s for s in log if "  load skin from:" in s]
        report["focus_error_count"] = sum(bool(re.search(r"Control 3110 in window \d+ has been asked to focus, but it can't$", s)) for s in report["error_lines"])
        report["only_expected_focus_errors"] = report["focus_error_count"] == len(report["error_lines"]) == 0
        name = "bg_colorpicker_skin_checks.json"
        (repo / "results/kodi22_runtime" / name).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "phases": report["phases"], "errors": len(report["error_lines"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()) or not report["only_expected_focus_errors"])


if __name__ == "__main__":
    sys.exit(main())
