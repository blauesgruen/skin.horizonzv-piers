"""Dashboard addon actions and the actual shutdown addon item; no power actions."""
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
        assert '!String.IsEmpty(Skin.String(addon_fav1))' in (repo / "xml/Includes_Dash_Addonpath_Fav.xml").read_text(encoding="utf-8"), "Baseline requires original dispatch predicates."
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    count = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert count.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-addon-dispatch-", dir=root))
    profile = root / "portable_data"
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    backups = {rel: (profile / rel).read_bytes() for rel in rels}
    for i, data in enumerate(backups.values()):
        (work / f"settings-{i}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    def db_files():
        return list(database.glob("Addons*.db*"))
    db_backup = {p.name: p.read_bytes() for p in db_files()}
    saved = work / "database"; saved.mkdir()
    for name, data in db_backup.items():
        (saved / name).write_bytes(data)
    addon_id = "script.horizonzv.dispatchprobe"
    fixture = profile / "addons" / addon_id
    assert not fixture.exists(), "Own fixture already exists"
    fixture.mkdir()
    (fixture / "addon.xml").write_text('<addon id="' + addon_id + '" name="HorizonzV Dispatch Fixture" version="0.0.1" provider-name="Authored local fixture"><requires><import addon="xbmc.python" version="3.0.0" /></requires><extension point="xbmc.python.script" library="default.py" /><extension point="xbmc.addon.metadata"><summary lang="en_GB">Authored local marker only</summary><description lang="en_GB">Writes a local invocation marker. No network, device or power action.</description><platform>all</platform><license>MIT</license></extension></addon>', encoding="utf-8")
    marker = work / "invocations.jsonl"
    (fixture / "default.py").write_text("import json,sys\nfrom pathlib import Path\nwith Path(" + repr(str(marker)) + ").open('a',encoding='utf-8') as f:f.write(json.dumps({'argv':sys.argv})+'\\n')\n", encoding="utf-8")
    xml = profile / "addons/skin.horizonzv/xml"
    for path in (repo / "xml").glob("*.xml"):
        shutil.copy2(path, xml / path.name)
    dashboard_file = xml / "Includes_Dash_Addonpath_Fav.xml"
    dashboard = ET.parse(dashboard_file)
    dashboard_items = dashboard.findall(".//include[@name='DashboardContent']/content/item")
    assert len(dashboard_items) == 10
    for item in dashboard_items:
        ET.SubElement(item, "property", {"name": "HorizonzV.DispatchProbeSlot"}).text = "slot-" + item.get("id")
    dashboard.write(dashboard_file, encoding="utf-8", xml_declaration=True)
    power_file = xml / "DialogButtonMenu.xml"
    tree = ET.parse(power_file)
    candidates = [e for e in tree.findall(".//item") if e.findtext("label") == "$VAR[shutdown_addon_var]"]
    assert len(candidates) == 1
    allowed = [e.text for e in candidates[0].findall("onclick")]
    assert allowed == ["Dialog.Close(all)", "RunAddon($INFO[Skin.String(shutdown_addon1)])", "Skin.SetAddon(shutdown_addon1,xbmc.addon.video,xbmc.addon.audio,xbmc.addon.executable,xbmc.addon.image,kodi.gameclient)"]
    ET.SubElement(candidates[0], "property", {"name": "HorizonzV.DispatchProbeTarget"}).text = "true"
    tree.write(power_file, encoding="utf-8", xml_declaration=True)
    layout = work / "resources/skins/Default/1080i"
    layout.mkdir(parents=True)
    window = ET.Element("window")
    ET.SubElement(window, "defaultcontrol", {"always": "true"}).text = "6001"
    controls = ET.SubElement(window, "controls")
    button = ET.SubElement(controls, "control", {"type": "button", "id": "9000"})
    for name, value in {"left": "50", "top": "25", "width": "1600", "height": "70", "label": "HorizonzV addon-dispatch contract probe", "font": "font16", "onclick": "noop"}.items():
        ET.SubElement(button, name).text = value
    for control_id, top in (("6001", "150"), ("8006", "750")):
        control = ET.SubElement(controls, "control", {"type": "list", "id": control_id})
        for name, value in {"left": "50", "top": top, "width": "1700", "height": "550" if control_id == "6001" else "200", "onup": control_id, "ondown": control_id}.items():
            ET.SubElement(control, name).text = value
        for tag in ("itemlayout", "focusedlayout"):
            item = ET.SubElement(control, tag, {"width": "1700", "height": "50"})
            label = ET.SubElement(item, "control", {"type": "label"})
            for name, value in {"width": "1600", "height": "50", "font": "font16", "label": "$INFO[ListItem.Label]", "textcolor": "orange" if tag == "focusedlayout" else "white"}.items():
                ET.SubElement(label, name).text = value
        ET.SubElement(control, "include").text = "DashboardContent"
    ET.ElementTree(window).write(layout / "dispatch_probe.xml", encoding="utf-8", xml_declaration=True)
    closed = work / "probe_closed"
    script = work / "probe.py"
    script.write_text("import xbmcgui\nfrom pathlib import Path\nclass Probe(xbmcgui.WindowXML):\n def onAction(self,a):\n  if a.getId() in (9,10,92,216):self.close()\nw=Probe('dispatch_probe.xml',str(Path(__file__).parent),'Default','1080i')\nw.doModal()\ndel w\nPath(" + repr(str(closed)) + ").write_text('closed')\n", encoding="utf-8")
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
    def invocations():
        return [json.loads(line) for line in marker.read_text(encoding="utf-8").splitlines()] if marker.exists() else []
    def set_string(name, value):
        client.send_action("Skin.SetString(" + name + "," + value + ")") if value else client.send_action("Skin.Reset(" + name + ")")
        wait(lambda: label("Skin.String(" + name + ")"), value)
    def observe_after(before, available):
        if available:
            wait(lambda: len(invocations()), before + 1)
        elif not baseline:
            wait(lambda: boolean("Window.IsVisible(selectdialog)"), True)
        time.sleep(.2)
        result = {"invocations_before": before, "invocations_after": len(invocations()), "selector_visible": boolean("Window.IsVisible(selectdialog)")}
        if not available:
            assert len(invocations()) == before, result
        if boolean("Window.IsVisible(selectdialog)"):
            rpc("Input.Back"); wait(lambda: boolean("Window.IsVisible(selectdialog)"), False)
        return result
    report = {"scope": "Actual production DashboardContent in a native WindowXML list and actual shutdownmenu addon item with one marker property. Only own local marker addon can run. No power/device action selected.", "baseline": baseline, "work": str(work), "rows": [], "production_sha256": {name: hashlib.sha256((repo / "xml" / name).read_bytes()).hexdigest() for name in ("Includes_Dash_Addonpath_Fav.xml", "DialogButtonMenu.xml")}}
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
            try:
                rpc("JSONRPC.Ping"); break
            except Exception:
                assert process.poll() is None; time.sleep(.2)
        client = XBMCClient(name="HorizonzV addon dispatch", uid=secrets.randbits(32)); client.connect(port=9777); time.sleep(.3)
        rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": False})
        for i in range(1, 11):
            set_string("addon_fav" + str(i), addon_id)
        client.send_action('RunScript("' + script.as_posix() + '")'); wait(lambda: boolean("Control.HasFocus(6001)"), True)
        for mode in (("disabled",) if baseline else ("disabled", "missing", "empty", "enabled")):
            available = mode == "enabled"
            if available:
                rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": True})
                wait(lambda: boolean("System.AddonIsEnabled(" + addon_id + ")"), True)
            selected = addon_id if mode in ("disabled", "enabled") else "script.horizonzv.missingdispatchfixture" if mode == "missing" else ""
            for i in range(1, 11):
                set_string("addon_fav" + str(i), selected)
            slots = (1, 10) if baseline or mode in ("missing", "empty") else range(1, 11)
            for slot in slots:
                client.send_action("Control.SetFocus(6001)"); wait(lambda: boolean("Control.HasFocus(6001)"), True)
                rpc("Input.ExecuteAction", {"action": "firstpage"})
                for _ in range(slot - 1):rpc("Input.Down")
                wait(lambda: label("Container(6001).ListItem.Label"), selected)
                wait(lambda: label("Container(6001).ListItem.Property(HorizonzV.DispatchProbeSlot)"), "slot-" + str(slot))
                before = len(invocations()); rpc("Input.Select"); time.sleep(.4)
                row = {"target": "dashboard", "mode": mode, "slot": slot, "observed_slot": str(slot), **observe_after(before, available)}; report["rows"].append(row)
        if not baseline:
            before = len(invocations()); client.send_action("Control.SetFocus(8006)"); wait(lambda: boolean("Control.HasFocus(8006)"), True)
            rpc("Input.Select"); wait(lambda: boolean("Control.HasFocus(9000)"), True)
            assert len(invocations()) == before and not boolean("Window.IsVisible(selectdialog)")
            report["preview_focus_preserved"] = True
        rpc("Input.Back"); wait(closed.exists, True)
        client.send_action("Skin.SetBool(shutdown_addon)"); wait(lambda: boolean("Skin.HasSetting(shutdown_addon)"), True)
        set_string("shutdown_addon1_label", "HorizonzV controlled addon target")
        for mode in (("disabled",) if baseline else ("disabled", "missing", "empty", "enabled")):
            available = mode == "enabled"
            rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": available})
            selected = addon_id if mode in ("disabled", "enabled") else "script.horizonzv.missingdispatchfixture" if mode == "missing" else ""
            set_string("shutdown_addon1", selected)
            rpc("GUI.ActivateWindow", {"window": "shutdownmenu"}); wait(lambda: boolean("Window.IsVisible(shutdownmenu)"), True)
            client.send_action("Control.SetFocus(9000)"); wait(lambda: boolean("Control.HasFocus(9000)"), True)
            for _ in range(100):
                if label("ListItem.Property(HorizonzV.DispatchProbeTarget)") == "true":break
                rpc("Input.Down"); time.sleep(.04)
            assert label("ListItem.Property(HorizonzV.DispatchProbeTarget)") == "true", "Never select an unidentified shutdown item"
            before = len(invocations()); rpc("Input.Select"); time.sleep(.5)
            report["rows"].append({"target": "shutdown_addon_item", "mode": mode, **observe_after(before, available)})
            client.send_action("Dialog.Close(shutdownmenu)"); wait(lambda: boolean("Window.IsVisible(shutdownmenu)"), False)
        report["invocations"] = invocations()
    except Exception as exc:
        failure = repr(exc); report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                for dialog in ("selectdialog", "shutdownmenu"):
                    if boolean("Window.IsVisible(" + dialog + ")"):
                        rpc("Input.Back"); wait(lambda: boolean("Window.IsVisible(" + dialog + ")"), False)
                if not closed.exists():
                    rpc("Input.Back"); wait(closed.exists, True)
                raw_rpc("Application.Quit"); process.wait(timeout=25)
            except Exception:
                pass
        if client:client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():(profile / rel).write_bytes(data)
            shutil.copy2(repo / "xml/DialogButtonMenu.xml", power_file)
            shutil.copy2(repo / "xml/Includes_Dash_Addonpath_Fav.xml", dashboard_file)
            extra = work / "new-database-files"; extra.mkdir()
            for p in db_files():
                if p.name not in db_backup:
                    assert root.resolve() in p.resolve().parents and root.resolve() in extra.resolve().parents
                    p.rename(extra / p.name)
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
        (repo / "results/kodi22_runtime" / ("addon_dispatch_before.json" if baseline else "addon_dispatch_checks.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "errors": report["errors"], "cleanup": cleanup}))
    return int(bool(failure) or not all(cleanup.values()) or (not baseline and bool(report["errors"])))


if __name__ == "__main__":main()
