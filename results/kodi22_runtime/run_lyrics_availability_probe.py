"""Visible selected-provider availability checks; existing addon code unchanged."""
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
        assert '<usealttexture>String.IsEmpty(Skin.String(LyricScript_Path))</usealttexture>' in (repo / "xml/PlayerControls.xml").read_text(encoding="utf-8"), "Baseline requires the original unguarded XML; preserve the recorded result."
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    count = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert count.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-lyrics-availability-", dir=root))
    profile = root / "portable_data"
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml", "userdata/addon_data/script.cu.lrclyrics/settings.xml")
    backups = {rel: (profile / rel).read_bytes() if (profile / rel).exists() else None for rel in rels}
    for i, data in enumerate(backups.values()):
        if data is not None:
            (work / f"settings-{i}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    def db_files():
        return [p for p in database.iterdir() if p.is_file() and (p.name.startswith("Addons") or p.name.startswith("MyMusic")) and ".db" in p.name]
    db_backup = {p.name: p.read_bytes() for p in db_files()}
    saved = work / "database"; saved.mkdir()
    for name, data in db_backup.items():
        (saved / name).write_bytes(data)
    xml = profile / "addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient
    def rpc(method, params=None):
        result = raw_rpc(method, params); assert "result" in result, result
        return result["result"]
    def wait(probe, expected, attempts=150):
        for _ in range(attempts):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})
    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]
    def label(expr):
        return rpc("XBMC.GetInfoLabels", {"labels": [expr]})[expr]
    def state():
        return {"lyrics": boolean("Skin.HasSetting(Lyrics)"), "selected": label("Skin.String(LyricScript_Path)"), "dynamic_version": label("System.AddonVersion(Skin.String(LyricScript_Path))"), "selector_visible": boolean("Window.IsVisible(selectdialog)"), "provider_running": label("Window(home).Property(culrc.running)")}
    report = {"scope": "Disabled selected CU LRC, missing ID and no selection at native lyrics UI. Own profile only; no addon code change.", "baseline": baseline, "rows": [], "work": str(work)}
    process = client = None
    failure = None
    try:
        gui = ET.parse(profile / rels[0])
        for name, value in {"lookandfeel.skin": "skin.horizonzv", "window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            item = gui.getroot().find(f"setting[@id='{name}']"); assert item is not None
            item.text = value; item.attrib.pop("default", None)
        gui.write(profile / rels[0], encoding="utf-8", xml_declaration=True)
        cu = ET.parse(profile / rels[2]) if backups[rels[2]] else ET.ElementTree(ET.Element("settings", {"version": "2"}))
        service = cu.getroot().find("setting[@id='service']")
        if service is None:
            service = ET.SubElement(cu.getroot(), "setting", {"id": "service"})
        service.text = "false"; service.attrib.pop("default", None)
        cu.write(profile / rels[2], encoding="utf-8", xml_declaration=True)
        startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup); report["pid"] = process.pid
        for _ in range(90):
            try:
                rpc("JSONRPC.Ping"); break
            except Exception:
                assert process.poll() is None; time.sleep(.2)
        client = XBMCClient(name="HorizonzV lyrics availability", uid=secrets.randbits(32)); client.connect(port=9777); time.sleep(.3)
        client.send_action("Skin.SetString(LyricScript_Path,script.cu.lrclyrics)"); time.sleep(.2)
        rpc("Addons.SetAddonEnabled", {"addonid": "script.cu.lrclyrics", "enabled": True})
        wait(lambda: boolean("System.AddonIsEnabled(script.cu.lrclyrics)"), True)
        report["enabled_version"] = label("System.AddonVersion(Skin.String(LyricScript_Path))")
        assert report["enabled_version"] == "6.7.6"
        rpc("Addons.SetAddonEnabled", {"addonid": "script.cu.lrclyrics", "enabled": False})
        wait(lambda: boolean("System.AddonIsEnabled(script.cu.lrclyrics)"), False)
        report["disabled_version"] = label("System.AddonVersion(Skin.String(LyricScript_Path))")
        assert report["disabled_version"] == ""
        audio = profile / "testmedia/skin-audit-silence.wav"
        client.send_action('PlayMedia("' + audio.as_posix() + '")'); wait(lambda: boolean("Player.HasAudio"), True)
        for selected in (("script.cu.lrclyrics",) if baseline else ("script.cu.lrclyrics", "script.horizonzv.missinglyricsfixture", "")):
            client.send_action("Skin.SetString(LyricScript_Path," + selected + ")") if selected else client.send_action("Skin.Reset(LyricScript_Path)")
            wait(lambda: label("Skin.String(LyricScript_Path)"), selected)
            for target in ("osd", "playercontrols"):
                client.send_action("Skin.Reset(Lyrics)"); wait(lambda: boolean("Skin.HasSetting(Lyrics)"), False)
                if target == "osd":
                    client.send_action("ActivateWindow(visualisation)"); wait(lambda: boolean("Window.IsVisible(visualisation)"), True)
                    client.send_action("ActivateWindow(musicosd)"); wait(lambda: boolean("Window.IsVisible(musicosd)"), True)
                    client.send_action("Control.SetFocus(701)"); wait(lambda: boolean("Control.HasFocus(701)"), True)
                else:
                    rpc("GUI.ActivateWindow", {"window": "home"}); wait(lambda: boolean("Window.IsActive(home)"), True)
                    client.send_action("ActivateWindow(playercontrols)"); wait(lambda: boolean("Window.IsVisible(playercontrols)"), True)
                    client.send_action("Control.SetFocus(609)"); wait(lambda: boolean("Control.HasFocus(609)"), True)
                if not baseline and target == "osd":
                    rpc("Input.Down"); wait(lambda: boolean("Control.IsVisible(2401)"), True)
                    assert not boolean("Control.IsEnabled(2401)")
                    if selected == "script.cu.lrclyrics":
                        client.send_action("Skin.SetBool(Lyrics)"); wait(lambda: boolean("Skin.HasSetting(Lyrics)"), True)
                        wait(lambda: boolean("Control.IsEnabled(2401)"), True)
                        client.send_action("Control.SetFocus(2401)"); wait(lambda: boolean("Control.HasFocus(2401)"), True)
                        rpc("Input.Select"); wait(lambda: boolean("Skin.HasSetting(Lyrics)"), False)
                        report["stale_lyrics_toggle_off"] = state()
                    client.send_action("Control.SetFocus(701)"); wait(lambda: boolean("Control.HasFocus(701)"), True)
                before = state(); rpc("Input.Select"); time.sleep(.8)
                if not baseline:
                    wait(lambda: boolean("Window.IsVisible(selectdialog)"), True)
                row = {"target": target, "before": before, "after": state()}; report["rows"].append(row)
                if not baseline:
                    assert not row["after"]["lyrics"] and not row["after"]["provider_running"], row
                    if target == "osd" and selected == "script.cu.lrclyrics":
                        capture = repo / "results/kodi22_runtime/lyrics_availability_selector.png"
                        capture.unlink(missing_ok=True)
                        client.send_action('TakeScreenshot("' + capture.as_posix() + '")'); wait(capture.exists, True)
                if boolean("Window.IsVisible(selectdialog)"):
                    rpc("Input.Back"); wait(lambda: boolean("Window.IsVisible(selectdialog)"), False)
                for dialog in ("musicosd", "playercontrols"):
                    client.send_action("Dialog.Close(" + dialog + ")")
                    wait(lambda: boolean("Window.IsVisible(" + dialog + ")"), False)
        rpc("Player.Stop", {"playerid": 0}); wait(lambda: boolean("Player.HasAudio"), False)
    except Exception as exc:
        failure = repr(exc); report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                if boolean("Player.HasAudio"):
                    rpc("Player.Stop", {"playerid": 0})
                rpc("Input.Back"); raw_rpc("Application.Quit"); process.wait(timeout=25)
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
            extra = work / "new-database-files"; extra.mkdir()
            for p in db_files():
                if p.name not in db_backup:
                    assert root.resolve() in p.resolve().parents and root.resolve() in extra.resolve().parents
                    p.rename(extra / p.name)
            for name, data in db_backup.items():
                (database / name).write_bytes(data)
            cleanup["settings_restored"] = all((profile / rel).read_bytes() == data if data is not None else not (profile / rel).exists() for rel, data in backups.items())
            cleanup["music_and_addon_databases_restored"] = {p.name: p.read_bytes() for p in db_files()} == db_backup
            cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [line for line in lines if " error " in line.lower() or "fatal" in line.lower()]
        (repo / "results/kodi22_runtime" / ("lyrics_availability_before.json" if baseline else "lyrics_availability_checks.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "errors": report["errors"], "cleanup": cleanup}))
    return int(bool(failure) or not all(cleanup.values()) or (not baseline and bool(report["errors"])))


if __name__ == "__main__":
    sys.exit(main())
