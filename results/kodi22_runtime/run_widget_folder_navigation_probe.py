"""Baseline for source checkpoint 017200c, before explicit widget source targets."""
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET


def main():
    repo = Path(__file__).resolve().parents[2]
    assert ET.parse(repo / "xml/Variables_Widgets.xml").getroot().find("variable[@name='WidgetTarget']") is not None, "Baseline requires the pre-fix WidgetTarget variable (checkpoint 017200c)"
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    count = subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], text=True)
    assert count.strip() == "0", "Another Kodi is running"
    profile = root / "portable_data"
    xml = profile / "addons/skin.horizonzv/xml"
    work = Path(tempfile.mkdtemp(prefix="review-widget-navigation-", dir=root))
    folder = work / "untyped-folder"
    folder.mkdir()
    (folder / "README.txt").write_text("Authored navigation fixture; no media playback.\n", encoding="utf-8")
    settings = {p: p.read_bytes() for p in [profile / "userdata/guisettings.xml", profile / "userdata/addon_data/skin.horizonzv/settings.xml"]}
    database = profile / "userdata/Database"
    db = {p.name: p.read_bytes() for p in database.iterdir() if p.is_file()}
    saved = work / "database"
    saved.mkdir()
    for name, data in db.items():
        (saved / name).write_bytes(data)
    addon = profile / "addons/plugin.program.horizonzv.navigationprobe"
    window = xml / "Custom_1197_WidgetNavigationAudit.xml"
    assert not addon.exists() and not window.exists()
    addon.mkdir()
    (addon / "addon.xml").write_text('<addon id="plugin.program.horizonzv.navigationprobe" name="HorizonzV local navigation probe" version="0.0.1" provider-name="Local fixture"><requires><import addon="xbmc.python" version="3.0.0" /></requires><extension point="xbmc.python.pluginsource" library="default.py"><provides>video executable</provides></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Local folder navigation probe</summary><description lang="en_GB">No network or playback.</description><platform>all</platform><license>MIT</license></extension></addon>', encoding="utf-8")
    (addon / "default.py").write_text('import sys,xbmcgui,xbmcplugin\nitem=xbmcgui.ListItem(label="Local test folder",path='+repr(folder.as_posix()+"/")+')\nxbmcplugin.addDirectoryItem(int(sys.argv[1]),item.getPath(),item,True)\nxbmcplugin.endOfDirectory(int(sys.argv[1]),True,cacheToDisc=False)\n', encoding="utf-8")
    ui = ET.Element("window", {"id": "1197"})
    ET.SubElement(ui, "defaultcontrol", {"always": "true"}).text = "50"
    controls = ET.SubElement(ui, "controls")
    def control(parent, kind, fields, cid=None):
        attrs = {"type": kind}
        if cid is not None:
            attrs["id"] = str(cid)
        result = ET.SubElement(parent, "control", attrs)
        for key, value in fields.items():
            ET.SubElement(result, key).text = str(value)
        return result
    control(controls, "image", {"width": "100%", "height": "100%", "texture": "BlackBack.png"})
    control(controls, "label", {"left": 40, "top": 40, "width": 1800, "height": 70, "font": "font24", "label": "HorizonzV: widget folder navigation"})
    for cid, top, target in [(50, 160, "$VAR[WidgetTarget]"), (51, 420, "videos")]:
        control(controls, "label", {"left": 40, "top": top, "width": 1800, "height": 55, "font": "font16", "label": "Production target" if cid == 50 else "Explicit videos target (reference)"})
        listing = control(controls, "list", {"left": 40, "top": top+70, "width": 1200, "height": 100, "ondown": 51, "onup": 50}, cid)
        for tag in ["itemlayout", "focusedlayout"]:
            layout = ET.SubElement(listing, tag, {"width": "1200", "height": "70"})
            control(layout, "label", {"width": 1200, "height": 70, "font": "font16", "textcolor": "orange" if tag == "focusedlayout" else "white", "label": "$INFO[ListItem.Label]"})
        ET.SubElement(listing, "content", {"target": target}).text = "plugin://plugin.program.horizonzv.navigationprobe/"
    control(controls, "label", {"left": 40, "top": 730, "width": 1800, "height": 65, "font": "font16", "label": "Resolved target: $VAR[WidgetTarget]"}, 1001)
    ET.ElementTree(ui).write(window, encoding="utf-8", xml_declaration=True)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient
    def result(method, params=None):
        value = rpc(method, params)
        assert "result" in value, value
        return value["result"]
    def wait(fn, expected, seconds=15):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            value = fn()
            if value == expected:
                return value
            time.sleep(.2)
        raise AssertionError((value, expected))
    def window_id():
        return result("GUI.GetProperties", {"properties": ["currentwindow"]})["currentwindow"]["id"]
    report = {"scope": "Native production WidgetTarget with an untyped authored folder, compared with explicit videos target. No media playback or network directory.", "rows": []}
    process = client = None
    failure = None
    try:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        for _ in range(80):
            try:
                result("JSONRPC.Ping")
                break
            except Exception:
                assert process.poll() is None
                time.sleep(.25)
        result("Addons.SetAddonEnabled", {"addonid": addon.name, "enabled": True})
        client = XBMCClient(name="HorizonzV local folder navigation", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action("ActivateWindow(11197)")
        wait(window_id, 11197)
        wait(lambda: result("XBMC.GetInfoLabels", {"labels": ["Container(50).NumItems"]})["Container(50).NumItems"], "1")
        for cid in [50, 51]:
            client.send_action("Control.SetFocus("+str(cid)+")")
            wait(lambda: result("XBMC.GetInfoBooleans", {"booleans": ["Control.HasFocus("+str(cid)+")"]})["Control.HasFocus("+str(cid)+")"], True)
            before = result("XBMC.GetInfoLabels", {"labels": ["Container.ListItem.Label", "Container.ListItem.DBTYPE", "Container.ListItem.FolderPath", "Control.GetLabel(1001)"]})
            time.sleep(.8)
            if cid == 50:
                shot = repo / "results/kodi22_runtime/widget_folder_navigation_before.png"
                shot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("'+shot.as_posix()+'")')
                wait(shot.exists, True)
            result("Input.Select")
            time.sleep(1.2)
            report["rows"].append({"control": cid, "before": before, "window_after_select": window_id(), "directory_after_select": result("XBMC.GetInfoLabels", {"labels": ["Container.FolderPath"]})["Container.FolderPath"]})
        assert report["rows"][0]["window_after_select"] == 11197, report
        assert report["rows"][1]["window_after_select"] == 10025, report
        assert report["rows"][1]["directory_after_select"].rstrip('/\\').replace('\\','/') == folder.as_posix(), report
    except Exception as exc:
        failure = repr(exc)
        report.update(failure=failure, trace=traceback.format_exc())
    finally:
        if process and process.poll() is None:
            try:
                result("Application.Quit")
                process.wait(timeout=30)
            except Exception as exc:
                report["shutdown_error"] = repr(exc)
        if client:
            client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for path, data in settings.items():
                path.write_bytes(data)
            extra = work / "new-database-files"
            extra.mkdir()
            for path in database.iterdir():
                if path.is_file() and path.name not in db:
                    path.rename(extra / path.name)
            for name, data in db.items():
                (database / name).write_bytes(data)
            assert root.resolve() in addon.resolve().parents and root.resolve() in work.resolve().parents
            addon.rename(work / "fixture-addon")
            window.rename(work / window.name)
            cleanup.update(settings_restored=all(p.read_bytes()==data for p,data in settings.items()), databases_restored={p.name:p.read_bytes() for p in database.iterdir() if p.is_file()}==db, skin_xml_match={p.name:p.read_bytes() for p in xml.glob('*.xml')}=={p.name:p.read_bytes() for p in (repo/'xml').glob('*.xml')})
        report["cleanup"] = cleanup
        report["errors"] = [line for line in (profile/"kodi.log").read_text(encoding="utf-8", errors="replace").splitlines() if " error " in line.lower() or "fatal" in line.lower()]
        (repo/"results/kodi22_runtime/widget_folder_navigation_before.json").write_text(json.dumps(report,indent=2)+'\n',encoding="utf-8")
    print(json.dumps({"failure":failure,"rows":report['rows'],"cleanup":cleanup,"errors":report['errors']}))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
