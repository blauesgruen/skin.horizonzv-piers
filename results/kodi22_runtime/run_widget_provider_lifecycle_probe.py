"""Real directory jobs through production widget structures; no device actions."""
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
    count = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert count.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-widget-provider-lifecycle-", dir=root))
    events = work / "events"; events.mkdir()
    profile = root / "portable_data"
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    backups = {rel: (profile / rel).read_bytes() for rel in rels}
    for i, data in enumerate(backups.values()):(work / f"settings-{i}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    def db_files():return list(database.glob("Addons*.db*"))
    db_backup = {p.name: p.read_bytes() for p in db_files()}
    saved = work / "database"; saved.mkdir()
    for name, data in db_backup.items():(saved / name).write_bytes(data)
    addon_id = "plugin.video.horizonzv.widgetprobe"
    fixture = profile / "addons" / addon_id
    assert not fixture.exists()
    fixture.mkdir()
    (fixture / "addon.xml").write_text('<addon id="' + addon_id + '" name="HorizonzV Widget Fixture" version="0.0.1" provider-name="Authored local fixture"><requires><import addon="xbmc.python" version="3.0.0" /></requires><extension point="xbmc.python.pluginsource" library="default.py"><provides>video executable</provides></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Local directory fixture</summary><description lang="en_GB">Returns authored rows only. No device, network or power actions.</description><platform>all</platform><license>MIT</license></extension></addon>', encoding="utf-8")
    provider = '''import json,sys,uuid
from pathlib import Path
from urllib.parse import parse_qs
import xbmc,xbmcgui,xbmcplugin
params=parse_qs(sys.argv[2].lstrip('?'))
kind='gto' if params.get('action')==['getcontent'] else 'fritz'
stamp=params.get('ts',[''])[0]
enabled_at_entry=xbmc.getCondVisibility('System.AddonIsEnabled(FIXTURE)')
for case in range(8 if kind=='gto' else 1):
 item=xbmcgui.ListItem(label='Authored '+kind+' '+stamp+' case'+str(case),path='plugin://FIXTURE/unused')
 item.setProperty('type','fixture-not-an-action')
 if kind=='gto':
  item.setProperty('GTO_Dash_FirstplaceLabel','First' if case & 4 else '')
  item.setProperty('channel','Channel' if case & 2 else '')
  item.setLabel2('Secondary' if case & 1 else '')
 item.setArt({'icon':'DefaultAddon.png'})
 xbmcplugin.addDirectoryItem(int(sys.argv[1]),'plugin://FIXTURE/unused',item,True)
xbmcplugin.endOfDirectory(int(sys.argv[1]),True,cacheToDisc=False)
folder=Path(EVENTS)
key=uuid.uuid4().hex
temporary=folder/(key+'.tmp')
temporary.write_text(json.dumps({'kind':kind,'timestamp':stamp,'addon_enabled_at_entry':enabled_at_entry,'argv':sys.argv}),encoding='utf-8')
temporary.rename(folder/(key+'.json'))
'''.replace("FIXTURE", addon_id).replace("EVENTS", repr(str(events)))
    (fixture / "default.py").write_text(provider, encoding="utf-8")
    xml = profile / "addons/skin.horizonzv/xml"
    for path in (repo / "xml").glob("*.xml"):shutil.copy2(path, xml / path.name)
    mapped = {"Includes_Dash_FritzDect.xml": "script.program.fritzact", "Includes_Dash_GTO.xml": "script.service.gto"}
    for name, original_id in mapped.items():
        path = xml / name
        path.write_text(path.read_text(encoding="utf-8").replace(original_id, addon_id), encoding="utf-8")
    layout = work / "resources/skins/Default/1080i"; layout.mkdir(parents=True)
    window = ET.Element("window"); ET.SubElement(window, "defaultcontrol", {"always": "true"}).text = "9000"
    controls = ET.SubElement(window, "controls")
    background = ET.SubElement(controls, "control", {"type": "image"})
    for name, value in {"width": "1920", "height": "1080", "texture": "Black.png"}.items():ET.SubElement(background, name).text = value
    button = ET.SubElement(controls, "control", {"type": "button", "id": "9000"})
    for name, value in {"left": "50", "top": "30", "width": "1800", "height": "70", "font": "font16", "label": "HorizonzV widget-provider lifecycle: no device actions", "onclick": "noop"}.items():ET.SubElement(button, name).text = value
    for include_name, control_id, top in (("FritzDect", "6100", "200"), ("GTO", "6200", "500")):
        group = ET.SubElement(controls, "control", {"type": "group"})
        for name, value in {"left": "50", "top": top, "width": "1800", "height": "200"}.items():ET.SubElement(group, name).text = value
        include = ET.SubElement(group, "include", {"content": include_name, "condition": "System.AddonIsEnabled(" + addon_id + ")"})
        ET.SubElement(include, "param", {"name": "id", "value": control_id})
        ET.SubElement(include, "param", {"name": "visible", "value": "System.AddonIsEnabled(" + addon_id + ")"})
    ET.ElementTree(window).write(layout / "widget_lifecycle_probe.xml", encoding="utf-8", xml_declaration=True)
    closed = work / "probe_closed"
    script = work / "probe.py"
    script.write_text("import xbmcgui\nfrom pathlib import Path\nclass Probe(xbmcgui.WindowXML):\n def onAction(self,a):\n  if a.getId() in (9,10,92,216):self.close()\nw=Probe('widget_lifecycle_probe.xml',str(Path(__file__).parent),'Default','1080i')\nw.doModal()\ndel w\nPath(" + repr(str(closed)) + ").write_text('closed')\n", encoding="utf-8")
    sys.path.insert(0, str(root)); sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient
    def rpc(method, params=None):
        result = raw_rpc(method, params); assert "result" in result, result
        return result["result"]
    def wait(probe, expected, attempts=180):
        for _ in range(attempts):
            actual = probe()
            if actual == expected:return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})
    def boolean(expr):return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]
    def labels(*exprs):return rpc("XBMC.GetInfoLabels", {"labels": list(exprs)})
    def event_rows():return [json.loads(p.read_text(encoding="utf-8")) for p in events.glob("*.json")]
    def snapshot():
        return {"enabled": boolean("System.AddonIsEnabled(" + addon_id + ")"), "visible": {str(i): boolean("Control.IsVisible(" + str(i) + ")") for i in (6100, 6200)}, "labels": labels("Container(6100).NumItems", "Container(6100).ListItem.Label", "Container(6200).NumItems", "Container(6200).ListItem(1).Label", "Skin.AspectRatio"), "requests": event_rows()}
    def stamp(value):
        for name in ("fritzact.timestamp", "GTO.timestamp"):client.send_action("SetProperty(" + name + "," + value + ",home)")
    def wait_data(value):
        wait(lambda: all(any(x["kind"] == k and x["timestamp"] == value for x in event_rows()) for k in ("fritz", "gto")), True)
        wait(lambda: value in labels("Container(6100).ListItem.Label")["Container(6100).ListItem.Label"], True)
        wait(lambda: value in labels("Container(6200).ListItem(1).Label")["Container(6200).ListItem(1).Label"], True)
    report = {"scope": "Production Fritz/GTO structures with addon IDs remapped only in isolated XML to a local fixture. No real backend data or widget Select actions. Actual directory jobs, enable/disable transition and eight focused-label input combinations.", "work": str(work), "mapped_addon_ids": mapped, "rows": [], "focused_labels": [], "production_sha256": {name: hashlib.sha256((repo / "xml" / name).read_bytes()).hexdigest() for name in (*mapped, "Includes_Dash_Layout.xml")}}
    process = client = None
    failure = None
    try:
        gui = ET.parse(profile / rels[0])
        for name, text in {"lookandfeel.skin": "skin.horizonzv", "window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            item = gui.getroot().find(f"setting[@id='{name}']"); assert item is not None
            item.text = text; item.attrib.pop("default", None)
        gui.write(profile / rels[0], encoding="utf-8", xml_declaration=True)
        startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup); report["pid"] = process.pid
        for _ in range(90):
            try:rpc("JSONRPC.Ping"); break
            except Exception:assert process.poll() is None; time.sleep(.2)
        client = XBMCClient(name="HorizonzV widget provider lifecycle", uid=secrets.randbits(32)); client.connect(port=9777); time.sleep(.3)
        rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": True}); wait(lambda: boolean("System.AddonIsEnabled(" + addon_id + ")"), True)
        stamp("initial")
        client.send_action('RunScript("' + script.as_posix() + '")'); wait(lambda: boolean("Control.HasFocus(9000)"), True)
        wait_data("initial"); report["rows"].append({"phase": "initial", **snapshot()})
        stamp("enabled-refresh"); wait_data("enabled-refresh"); report["rows"].append({"phase": "enabled-refresh", **snapshot()})
        predicate = ET.parse(repo / "xml/Includes_Dash_GTO.xml").find(".//include[@content='DashFocusedlayout']/param[@name='Dash_Label2_IsEmpty']").get("value")
        client.send_action("Control.SetFocus(6200)"); wait(lambda: boolean("Control.HasFocus(6200)"), True)
        rpc("Input.ExecuteAction", {"action": "firstpage"})
        for case in range(8):
            rpc("Input.Right")
            wait(lambda: labels("Container(6200).ListItem.Label")["Container(6200).ListItem.Label"].endswith("case" + str(case)), True)
            row = {"case": case, "labels": labels("ListItem.Label", "ListItem.Property(GTO_Dash_FirstplaceLabel)", "ListItem.Property(channel)", "ListItem.Label2"), "empty_predicate": predicate, "is_empty": boolean(predicate)}
            assert row["is_empty"] == (case == 0), row
            report["focused_labels"].append(row)
            if case in (0, 7):
                time.sleep(.9)  # Let the existing 800 ms horizontal scroll settle.
                capture = repo / "results/kodi22_runtime" / ("widget_label_" + ("empty" if case == 0 else "full") + ".png")
                capture.unlink(missing_ok=True); client.send_action('TakeScreenshot("' + capture.as_posix() + '")'); wait(capture.exists, True)
        client.send_action("Control.SetFocus(9000)"); wait(lambda: boolean("Control.HasFocus(9000)"), True)
        time.sleep(.3)
        rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": False}); wait(lambda: boolean("System.AddonIsEnabled(" + addon_id + ")"), False)
        for i in (6100, 6200):wait(lambda: boolean("Control.IsVisible(" + str(i) + ")"), False)
        baseline_count = len(event_rows())
        for i in range(3):stamp("disabled-" + str(i)); time.sleep(.7)
        row = {"phase": "disabled", "requests_before_changes": baseline_count, **snapshot()}; report["rows"].append(row)
        assert len(row["requests"]) == baseline_count, row
        rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": True}); wait(lambda: boolean("System.AddonIsEnabled(" + addon_id + ")"), True)
        stamp("reenabled"); wait_data("reenabled"); report["rows"].append({"phase": "reenabled", **snapshot()})
        assert all(event["addon_enabled_at_entry"] for event in event_rows())
        capture = repo / "results/kodi22_runtime/widget_provider_lifecycle.png"; capture.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + capture.as_posix() + '")'); wait(capture.exists, True)
        rpc("Input.Back"); wait(closed.exists, True)
    except Exception as exc:
        failure = repr(exc); report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                if not closed.exists():rpc("Input.Back"); wait(closed.exists, True)
                raw_rpc("Application.Quit"); process.wait(timeout=25)
            except Exception:pass
        if client:client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():(profile / rel).write_bytes(data)
            for name in mapped:shutil.copy2(repo / "xml" / name, xml / name)
            extra = work / "new-database-files"; extra.mkdir()
            for path in db_files():
                if path.name not in db_backup:
                    assert root.resolve() in path.resolve().parents and root.resolve() in extra.resolve().parents
                    path.rename(extra / path.name)
            for name, data in db_backup.items():(database / name).write_bytes(data)
            assert root.resolve() in fixture.resolve().parents and root.resolve() in work.resolve().parents
            fixture.rename(work / "fixture-addon")
            cleanup["settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            cleanup["addon_databases_restored"] = {p.name: p.read_bytes() for p in db_files()} == db_backup
            cleanup["fixture_removed"] = not fixture.exists()
            cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [line for line in lines if " error " in line.lower() or "fatal" in line.lower()]
        (repo / "results/kodi22_runtime/widget_provider_lifecycle_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "errors": report["errors"], "cleanup": cleanup}))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":sys.exit(main())
