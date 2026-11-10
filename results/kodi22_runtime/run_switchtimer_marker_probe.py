"""Visible native check of removed legacy marker fallback; no timer service run."""
import copy
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
    running = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert running.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-switchtimer-marker-", dir=root))
    profile = root / "portable_data"
    backups = {rel: (profile / rel).read_bytes() for rel in ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")}
    for i, data in enumerate(backups.values()):
        (work / f"profile-{i}.xml").write_bytes(data)
    xml = profile / "addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    baseline = ET.fromstring(subprocess.check_output(["git", "-c", "safe.directory=" + repo.as_posix(), "show", "61de250:xml/Variables.xml"]))
    previous_marker = copy.deepcopy(baseline.find("variable[@name='VARSwitchtimer']"))
    previous_icon = copy.deepcopy(baseline.find("variable[@name='PVRTimerIcon']"))
    previous_marker.set("name", "ProbePreviousSwitchtimer")
    previous_icon.set("name", "ProbePreviousPVRTimerIcon")
    for value in previous_icon.findall("value"):
        if value.text == "$VAR[VARSwitchtimer]":
            value.text = "$VAR[ProbePreviousSwitchtimer]"
    current = ET.parse(repo / "xml/Variables.xml").getroot()
    current_icon = current.find("variable[@name='PVRTimerIcon']")
    assert [ET.tostring(n).strip() for n in current_icon] == [ET.tostring(n).strip() for n in baseline.find("variable[@name='PVRTimerIcon']") if n.get("condition")]
    current.extend([previous_marker, previous_icon])
    ET.ElementTree(current).write(xml / "Variables.xml", encoding="utf-8", xml_declaration=True)
    layout = work / "resources/skins/Default/1080i"
    layout.mkdir(parents=True)
    window = ET.Element("window")
    ET.SubElement(window, "views").text = "50"
    ET.SubElement(window, "defaultcontrol", {"always": "true"}).text = "50"
    controls = ET.SubElement(window, "controls")

    def control(parent, kind, cid, values):
        node = ET.SubElement(parent, "control", {"type": kind, "id": str(cid)})
        for tag, text in values.items():
            ET.SubElement(node, tag).text = str(text)
        return node

    items = control(controls, "list", 50, {"left": 60, "top": 80, "width": 1700, "height": 100})
    ET.SubElement(items, "viewtype", {"label": "535"}).text = "list"
    for name in ("itemlayout", "focusedlayout"):
        row = ET.SubElement(items, name, {"width": "1700", "height": "70"})
        control(row, "label", 60, {"width": 1700, "height": 70, "font": "font16", "label": "$INFO[ListItem.Label]"})
    for cid, text, top in [(1001, "$VAR[ProbePreviousPVRTimerIcon]", 240), (1002, "$VAR[PVRTimerIcon]", 330), (1003, "$INFO[Window(Home).Property(SwitchTimerActiveItems)]", 420)]:
        control(controls, "label", cid, {"left": 60, "top": top, "width": 1700, "height": 60, "font": "font16", "label": text})
    condition = ET.parse(repo / "xml/Includes_PVR.xml").find(".//control[texture='PVR-Switchtimer.png']/visible").text
    assert condition == "Integer.IsGreater(Window(Home).Property(SwitchTimerActiveItems),0)"
    control(controls, "image", 1004, {"left": 60, "top": 510, "width": 100, "height": 100, "texture": "PVR-Switchtimer.png", "visible": condition})
    ET.ElementTree(window).write(layout / "marker_probe.xml", encoding="utf-8", xml_declaration=True)
    script = work / "fixture.py"
    script.write_text("""import xbmcgui
from pathlib import Path
ROOT=Path(__file__).parent
class Probe(xbmcgui.WindowXML):
 def onInit(self):
  home=xbmcgui.Window(10000)
  for i in range(10):
   for suffix in ('channel','date'): home.clearProperty(f't{i}:{suffix}')
  self.addItems([xbmcgui.ListItem(label='HorizonzV: native marker contract probe',offscreen=True)])
  (ROOT/'bound').write_text('ready')
 def onAction(self,a):
  if a.getId() in (9,10,92,216): self.close()
w=Probe('marker_probe.xml',str(ROOT),'Default','1080i',True)
w.doModal()
del w
""", encoding="utf-8")
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        data = raw_rpc(method, params)
        assert "result" in data, data
        return data["result"]

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def label(expr):
        return rpc("XBMC.GetInfoLabels", {"labels": [expr]})[expr]

    def wait(probe, expected):
        for _ in range(120):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})

    report = {"scope": "Native old/new variable comparison with one generic item lacking PVR channel/date, and the retained global count condition. No actual backend, timer service, scheduling or channel switching.", "rows": []}
    process = client = None
    failure = None
    try:
        gui = ET.parse(profile / "userdata/guisettings.xml")
        for name, value in {"input.enablemouse": "false", "debug.showloginfo": "false", "window.width": "1280", "window.height": "720"}.items():
            node = gui.find(f"setting[@id='{name}']")
            assert node is not None
            node.text = value
            node.attrib.pop("default", None)
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
        client = XBMCClient(name="HorizonzV switchtimer markers", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action('RunScript("' + script.as_posix() + '")')
        wait((work / "bound").exists, True)
        client.send_action("Container.SetViewMode(50)")
        time.sleep(.3)
        wait(lambda: label("Container(50).NumItems"), "1")
        for count in (0, 1, 0):
            client.send_action(f"SetProperty(SwitchTimerActiveItems,{count},home)")
            wait(lambda: label("Control.GetLabel(1003)"), str(count))
            time.sleep(.2)
            expressions = ["ListItem.ChannelName", "ListItem.Date", "Control.GetLabel(1001)", "Control.GetLabel(1002)", "Skin.AspectRatio"]
            values = rpc("XBMC.GetInfoLabels", {"labels": expressions})
            row = {"count": count, "values": values, "global_marker_visible": boolean("Control.IsVisible(1004)")}
            report["rows"].append(row)
            assert not values["ListItem.ChannelName"] and not values["ListItem.Date"], row
            assert values["Control.GetLabel(1001)"] == "PVR-Switchtimer.png", row
            assert values["Control.GetLabel(1002)"] == "", row
            assert row["global_marker_visible"] == (count > 0), row
        rpc("Input.Back")
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
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
            shutil.copy2(repo / "xml/Variables.xml", xml / "Variables.xml")
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            cleanup["all_skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [s for s in lines if " error " in s.lower() or "fatal" in s.lower()]
        (repo / "results/kodi22_runtime/switchtimer_marker_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "errors": len(report["errors"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
