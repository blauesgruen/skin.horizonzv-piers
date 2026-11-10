"""Native ListItem parent paths and production fanart variable, without playback."""
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
from urllib.parse import quote


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-native-fanart-paths-", dir=root))
    layout = work / "resources/skins/Default/1080i"
    layout.mkdir(parents=True)
    fixture = ET.Element("window")
    ET.SubElement(fixture, "views").text = "50"
    ET.SubElement(fixture, "defaultcontrol", {"always": "true"}).text = "50"
    controls = ET.SubElement(fixture, "controls")

    def control(parent, kind, values, cid=None):
        attrs = {"type": kind}
        if cid is not None:
            attrs["id"] = str(cid)
        result = ET.SubElement(parent, "control", attrs)
        for tag, value in values.items():
            ET.SubElement(result, tag).text = str(value)
        return result

    control(controls, "label", dict(left=30, top=20, width=1800, height=60, font="font24", label="HorizonzV: native parent paths"))
    items = control(controls, "list", dict(left=30, top=100, width=1800, height=360), 50)
    ET.SubElement(items, "viewtype", {"label": "535"}).text = "list"
    for tag, color in [("itemlayout", "white"), ("focusedlayout", "orange")]:
        group = ET.SubElement(items, tag, {"width": "1800", "height": "45"})
        control(group, "label", dict(width=1800, height=45, font="font16", textcolor=color, label="$INFO[ListItem.Label]"))
    for cid, top, label in [(1001, 500, "$INFO[ListItem.Path]"), (1002, 580, "$INFO[ListItem.FolderPath]"), (1003, 660, "$VAR[ListItemExtraFanartPath]")]:
        control(controls, "label", dict(left=30, top=top, width=1800, height=60, font="font16", label=label), cid)
    ET.ElementTree(fixture).write(layout / "path_labels.xml", encoding="utf-8", xml_declaration=True)
    ET.parse(layout / "path_labels.xml")
    base = "plugin://script.extendedinfo/fanart-audit/"
    plugin_parent = "plugin://script.extendedinfo/"
    stack = "stack://" + base + "one.mkv , " + base + "two.mkv"
    local = (root / "portable_data/testmedia").as_posix() + "/"
    local_stack = "stack://" + local + "one.mkv , " + local + "two.mkv"
    cases = [
        ("direct_plugin", base + "one.mkv", plugin_parent, ""),
        ("stack_plugin", stack, plugin_parent, ""),
        ("multipath_plugin", "multipath://" + quote(base + "one.mkv", safe="") + "/", plugin_parent, ""),
        ("nested_multipath_stack_plugin", "multipath://" + quote(stack, safe="") + "/", plugin_parent, ""),
        ("local_file", local + "one.mkv", local, local + "extrafanart"),
        ("local_stack", local_stack, local, local + "extrafanart"),
        ("local_multipath", "multipath://" + quote(local + "one.mkv", safe="") + "/", local, local + "extrafanart"),
    ]
    (work / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
    script = work / "path_fixture.py"
    script.write_text('''import xbmcgui,json
from pathlib import Path
ROOT=Path(__file__).parent
class Audit(xbmcgui.WindowXML):
 def onInit(self):
  (ROOT/'fixture_stage.json').write_text(json.dumps('on_init'))
  items=[xbmcgui.ListItem(label=c[0],path=c[1],offscreen=True) for c in json.loads((ROOT/'cases.json').read_text())]
  self.addItems(items)
  self.setCurrentListPosition(0)
  self.setFocusId(50)
  (ROOT/'fixture_stage.json').write_text(json.dumps('items_bound'))
 def onAction(self,action):
  if action.getId() in [9,10,92,216]:
   self.close()
ui=Audit('path_labels.xml',str(ROOT),'Default','1080i',True)
(ROOT/'fixture_stage.json').write_text(json.dumps('constructed'))
ui.doModal()
del ui
''', encoding="utf-8")
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient

    def labels():
        values = rpc("XBMC.GetInfoLabels", {"labels": ["Control.GetLabel(1001)", "Control.GetLabel(1002)", "Control.GetLabel(1003)", "Container(50).ListItem.Label"]})["result"]
        return {"1001": values["Control.GetLabel(1001)"], "1002": values["Control.GetLabel(1002)"], "1003": values["Control.GetLabel(1003)"], "case": values["Container(50).ListItem.Label"]}

    report = {"scope": "Native generic ListItem parent-path semantics and unmodified production ListItemExtraFanartPath; authored list paths only, no playback or plugin/SMB directory request", "rows": []}
    client = process = None
    failure = None
    try:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        for _ in range(60):
            try:
                rpc("JSONRPC.Ping")
                break
            except Exception:
                assert process.poll() is None
                time.sleep(.3)
        client = XBMCClient(name="HorizonzV native fanart paths", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action('RunScript("' + script.as_posix() + '")')
        for _ in range(80):
            stage = work / "fixture_stage.json"
            if stage.exists() and json.loads(stage.read_text()) == "items_bound":
                break
            time.sleep(.1)
        client.send_action("Container.SetViewMode(50)")
        client.send_action("Control.SetFocus(50)")
        for name, path, parent, fanart in cases:
            for _ in range(80):
                values = labels()
                if values.get("case") == name:
                    break
                time.sleep(.1)
            assert values.get("case") == name, values
            row = {"case": name, "input_path": path, "observed_parent": values["1001"], "observed_folderpath": values["1002"], "observed_fanart": values["1003"], "expected_parent": parent, "expected_fanart": fanart}
            report["rows"].append(row)
            assert row["observed_parent"].replace("\\", "/") == parent and row["observed_fanart"].replace("\\", "/") == fanart, row
            rpc("Input.Down")
            time.sleep(.15)
        shot = repo / "results/kodi22_runtime/fanart_wrapper_paths.png"
        shot.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + shot.as_posix() + '")')
        for _ in range(30):
            if shot.exists():
                break
            time.sleep(.1)
        rpc("Input.Back")
    except Exception as exc:
        failure = repr(exc)
        report["failure"] = failure
        report["failure_trace"] = traceback.format_exc()
        report["fixture_stage"] = (work / "fixture_stage.json").read_text() if (work / "fixture_stage.json").exists() else "no-stage"
        report["native_gui_state"] = rpc("GUI.GetProperties", {"properties": ["currentwindow", "currentcontrol"]})
        if client:
            shot = repo / "results/kodi22_runtime/fanart_wrapper_fixture_failure.png"
            shot.unlink(missing_ok=True)
            client.send_action('TakeScreenshot("' + shot.as_posix() + '")')
            for _ in range(20):
                if shot.exists():
                    break
                time.sleep(.1)
    finally:
        if client:
            client.close()
        if process:
            try:
                rpc("Application.Quit")
                process.wait(timeout=20)
            except Exception:
                pass
        exited = process is None or process.poll() is not None
        cleanup = {"process_exited": exited}
        if exited:
            for rel in rels:
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/fanart_wrapper_path_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
