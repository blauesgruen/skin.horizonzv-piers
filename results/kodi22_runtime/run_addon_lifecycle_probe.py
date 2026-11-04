"""Actual Kodi addon-info lifecycle states and textbox paging; own metadata only."""
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
    work = Path(tempfile.mkdtemp(prefix="review-addon-lifecycle-", dir=root))
    profile = root / "portable_data"
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    backups = {rel: (profile / rel).read_bytes() for rel in rels}
    for index, data in enumerate(backups.values()):
        (work / f"settings-{index}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    def db_files():
        return list(database.glob("Addons*.db*"))
    db_backup = {p.name: p.read_bytes() for p in db_files()}
    saved = work / "database"
    saved.mkdir()
    for name, data in db_backup.items():
        (saved / name).write_bytes(data)
    fixture_dirs = []
    for state in ("normal", "deprecated", "broken"):
        addon_id = "script.horizonzv.lifecycleprobe." + state
        path = profile / "addons" / addon_id
        assert not path.exists(), "Own fixture already exists"
        path.mkdir()
        fixture_dirs.append(path)
        manifest = ET.Element("addon", {"id": addon_id, "name": "HorizonzV Lifecycle Fixture " + state, "version": "0.0.1", "provider-name": "Authored local metadata fixture"})
        requires = ET.SubElement(manifest, "requires")
        ET.SubElement(requires, "import", {"addon": "xbmc.python", "version": "3.0.0"})
        ET.SubElement(manifest, "extension", {"point": "xbmc.python.script", "library": "default.py"})
        metadata = ET.SubElement(manifest, "extension", {"point": "xbmc.addon.metadata"})
        ET.SubElement(metadata, "summary", {"lang": "en_GB"}).text = "Authored lifecycle metadata fixture"
        ET.SubElement(metadata, "description", {"lang": "en_GB"}).text = "Short authored description." if state == "normal" else "\n".join("Authored description line %03d: Controlled multiline text for native paging verification." % i for i in range(1, 181))
        ET.SubElement(metadata, "lifecyclestate", {"type": state, "lang": "en_GB"}).text = "Authored lifecycle reason: " + state
        ET.SubElement(metadata, "platform").text = "all"
        ET.SubElement(metadata, "license").text = "MIT"
        ET.ElementTree(manifest).write(path / "addon.xml", encoding="utf-8", xml_declaration=True)
        (path / "default.py").write_text("# Metadata fixture. Never invoked by this test.\n", encoding="utf-8")
    xml = profile / "addons/skin.horizonzv/xml"
    for path in (repo / "xml").glob("*.xml"):
        shutil.copy2(path, xml / path.name)
    target = xml / "DialogAddonInfo.xml"
    tree = ET.parse(target)
    hooks = {}
    for control in tree.findall(".//control"):
        visible = control.findtext("visible", "")
        if control.get("type") == "group" and visible == "Container(400).HasNext|Container(400).HasPrevious":
            control.set("id", "15001"); hooks["pages"] = "15001"
        if control.get("type") == "group" and "24170" in visible and "24171" in visible and any(x.text == "$INFO[ListItem.AddonLifecycleType]" for x in control.findall(".//label")):
            control.set("id", "15002"); hooks["banner"] = "15002"
        if control.get("type") == "textbox" and control.findtext("label") == "$INFO[ListItem.AddonLifecycleDesc]":
            control.set("id", "15005"); hooks["reason"] = "15005"
        if control.findtext("description") == "Description Page Count":
            control.set("id", "15006"); hooks["page_label"] = "15006"
    assert hooks == {"pages": "15001", "page_label": "15006", "banner": "15002", "reason": "15005"}, hooks
    tree.write(target, encoding="utf-8", xml_declaration=True)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient
    def rpc(method, params=None):
        result = raw_rpc(method, params)
        assert "result" in result, result
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
    def labels(*names):
        return rpc("XBMC.GetInfoLabels", {"labels": list(names)})
    def label(name):
        return labels(name)[name]
    def state():
        return {"labels": labels("ListItem.Property(Addon.ID)", "ListItem.AddonLifecycleType", "ListItem.AddonLifecycleDesc", "Container(400).CurrentPage", "Container(400).NumPages", "Control.GetLabel(15006)", "Skin.AspectRatio"), "page_indicator_visible": boolean("Control.IsVisible(15001)"), "banner_visible": boolean("Control.IsVisible(15002)"), "has_next": boolean("Container(400).HasNext"), "has_previous": boolean("Container(400).HasPrevious")}
    report = {"scope": "Real installed metadata fixtures, native addonbrowser Info, actual DialogAddonInfo.xml with ID-only observation hooks. No existing addon code changed or fixture script executed. Four visits including return to normal, long-text paging.", "work": str(work), "rows": [], "observation_hooks": hooks, "production_xml_sha256": hashlib.sha256((repo / "xml/DialogAddonInfo.xml").read_bytes()).hexdigest()}
    process = client = None
    failure = None
    try:
        gui = ET.parse(profile / rels[0])
        for name, text in {"lookandfeel.skin": "skin.horizonzv", "window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            item = gui.getroot().find(f"setting[@id='{name}']")
            assert item is not None, name
            item.text = text; item.attrib.pop("default", None)
        gui.write(profile / rels[0], encoding="utf-8", xml_declaration=True)
        startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        report["pid"] = process.pid
        for _ in range(90):
            try:
                rpc("JSONRPC.Ping"); break
            except Exception:
                assert process.poll() is None; time.sleep(.2)
        client = XBMCClient(name="HorizonzV lifecycle metadata", uid=secrets.randbits(32)); client.connect(port=9777); time.sleep(.3)
        localized = work / "localized.json"
        script = work / "localize.py"
        script.write_text("import xbmc,json\nfrom pathlib import Path\nPath(" + repr(str(localized)) + ").write_text(json.dumps({k:xbmc.getLocalizedString(v) for k,v in {'normal':24169,'deprecated':24170,'broken':24171}.items()}),encoding='utf-8')\n", encoding="utf-8")
        client.send_action('RunScript("' + script.as_posix() + '")'); wait(localized.exists, True)
        expected_types = json.loads(localized.read_text(encoding="utf-8"))
        for case in ("normal", "deprecated", "broken", "normal"):
            addon_id = "script.horizonzv.lifecycleprobe." + case
            rpc("GUI.ActivateWindow", {"window": "addonbrowser", "parameters": ["addons://user/xbmc.python.script/", "return"]})
            time.sleep(.5)
            client.send_action("Container.SetViewMode(50)"); client.send_action("Control.SetFocus(50)")
            wait(lambda: boolean("Control.HasFocus(50)"), True)
            rpc("Input.ExecuteAction", {"action": "firstpage"})
            for _ in range(250):
                if label("ListItem.Property(Addon.ID)") == addon_id:
                    break
                rpc("Input.Down"); time.sleep(.03)
            assert label("ListItem.Property(Addon.ID)") == addon_id, addon_id
            rpc("Input.ExecuteAction", {"action": "info"})
            wait(lambda: boolean("Window.IsVisible(addoninformation)"), True)
            time.sleep(.6)
            row = {"case": case, "before_page": state()}; report["rows"].append(row)
            values = row["before_page"]["labels"]
            assert values["ListItem.AddonLifecycleType"] == expected_types[case], row
            assert values["ListItem.AddonLifecycleDesc"] == "Authored lifecycle reason: " + case, row
            assert row["before_page"]["banner_visible"] == (case != "normal"), row
            pages = int(values["Container(400).NumPages"])
            assert row["before_page"]["page_indicator_visible"] == (pages > 1), row
            if case == "normal":
                assert pages == 1, row
            else:
                assert pages > 1, row
                client.send_action("Control.SetFocus(60)"); wait(lambda: boolean("Control.HasFocus(60)"), True)
                # Kodi forces page-spin reverse=false: PageUp action advances by ten pages.
                row["paging_action"] = "pageup"
                rpc("Input.ExecuteAction", {"action": "pageup"})
                wait(lambda: int(label("Container(400).CurrentPage")) > int(values["Container(400).CurrentPage"]), True)
                row["after_page"] = state()
                assert row["after_page"]["has_previous"], row
            capture = repo / "results/kodi22_runtime" / ("addon_lifecycle_" + case + ".png")
            capture.unlink(missing_ok=True); client.send_action('TakeScreenshot("' + capture.as_posix() + '")'); wait(capture.exists, True)
            rpc("Input.Back"); wait(lambda: boolean("Window.IsVisible(addoninformation)"), False)
    except Exception as exc:
        failure = repr(exc); report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                rpc("Input.Back"); raw_rpc("Application.Quit"); process.wait(timeout=25)
            except Exception:
                pass
        if client:
            client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():
                (profile / rel).write_bytes(data)
            shutil.copy2(repo / "xml/DialogAddonInfo.xml", target)
            extra = work / "new-addon-database-files"; extra.mkdir()
            for p in db_files():
                if p.name not in db_backup:
                    assert root.resolve() in p.resolve().parents and root.resolve() in extra.resolve().parents
                    p.rename(extra / p.name)
            for name, data in db_backup.items():
                (database / name).write_bytes(data)
            for path in fixture_dirs:
                assert root.resolve() in path.resolve().parents and root.resolve() in work.resolve().parents
                path.rename(work / path.name)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            cleanup["addon_databases_restored"] = {p.name: p.read_bytes() for p in db_files()} == db_backup
            cleanup["fixtures_removed_from_addon_directory"] = all(not p.exists() for p in fixture_dirs)
            cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [line for line in lines if " error " in line.lower() or "fatal" in line.lower()]
        (repo / "results/kodi22_runtime/addon_lifecycle_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "errors": report["errors"], "cleanup": cleanup}))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
