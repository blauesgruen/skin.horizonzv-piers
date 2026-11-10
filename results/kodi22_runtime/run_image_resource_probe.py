"""Visible native resource-selector contract check; provider copies stay unchanged."""
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
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-image-resource-", dir=root))
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    hashes = {}
    for addon in ("script.image.resource.select", "resource.images.weathericons.outline", "resource.images.weatherfanart.multi"):
        source, target = repo.parent / addon, root / "portable_data/addons" / addon
        for p in source.rglob("*"):
            if p.is_file() and not any(x in p.parts for x in (".git", "__pycache__", ".codex")):
                name = addon + "/" + p.relative_to(source).as_posix()
                hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
                dest = root / "portable_data/addons" / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    assert dest.read_bytes() == p.read_bytes(), "Existing provider copy differs"
                else:
                    shutil.copy2(p, dest)
    xml = root / "portable_data/addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    baseline = ET.fromstring(subprocess.check_output(["git", "-c", "safe.directory=" + repo.as_posix(), "show", "772c767:xml/SkinSettings.xml"]))
    current = ET.parse(repo / "xml/SkinSettings.xml").getroot()
    old = baseline.find(".//control[@id='438']").findall("onclick")
    new = current.find(".//control[@id='438']").findall("onclick")
    assert len(old) == 2 and len(new) == 1 and all(n.text == new[0].text for n in old)
    layout = work / "resources/skins/Default/1080i"
    layout.mkdir(parents=True)
    fixture = ET.Element("window")
    ET.SubElement(fixture, "defaultcontrol", {"always": "true"}).text = "100"
    controls = ET.SubElement(fixture, "controls")
    for cid, title, actions in [(100, "Baseline: duplicate selector call", old), (101, "HorizonzV: single selector call", new), (102, "HorizonzV: weather icons", [ET.fromstring('<onclick>RunScript(script.image.resource.select,property=weathericons&amp;type=resource.images.weathericons)</onclick>')])]:
        c = ET.SubElement(controls, "control", {"type": "button", "id": str(cid)})
        for tag, text in {"left":"70", "top":str(100+(cid-100)*90), "width":"1600", "height":"70", "font":"font16", "label":title, "texturefocus":"White.png", "texturenofocus":"Black.png"}.items():
            ET.SubElement(c, tag).text = text
        for action in actions:
            ET.SubElement(c, "onclick").text = action.text
    ET.ElementTree(fixture).write(layout / "selector_probe.xml", encoding="utf-8", xml_declaration=True)
    script = work / "selector_probe.py"
    script.write_text("import xbmcgui\nfrom pathlib import Path\nclass Probe(xbmcgui.WindowXML):\n def onInit(self): self.setFocusId(100)\n def onAction(self,a):\n  if a.getId() in (9,10,92,216): self.close()\nw=Probe('selector_probe.xml',str(Path(__file__).parent),'Default','1080i')\nw.doModal()\ndel w\n", encoding="utf-8")
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
        raise AssertionError({"expected":expected,"actual":actual})

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans":[expr]})[expr]

    def state(prop):
        labels = ["Skin.String(" + prop + "." + k + ")" for k in ("name", "path", "ext")]
        values = rpc("XBMC.GetInfoLabels", {"labels":labels})
        return {**{k:values[label] for k,label in zip(("name","path","ext"),labels)},"multi":boolean("Skin.HasSetting(" + prop + ".multi)")}

    def loglines():
        return (root / "portable_data/kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()

    report = {"scope":"Copied skin action chains in native WindowXML; unchanged Image Resource Select 3.0.2 and two real image resources; no weather backend or full settings layout test", "phases":[], "source_hashes":hashes}
    process = client = None
    failure = None
    try:
        gui = root / "portable_data/userdata/guisettings.xml"
        config = ET.parse(gui)
        debug = config.getroot().find("setting[@id='debug.showloginfo']")
        assert debug is not None
        debug.text = "true"
        debug.attrib.pop("default", None)
        config.write(gui, encoding="utf-8", xml_declaration=True)
        startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        report["pid"] = process.pid
        for _ in range(60):
            try:
                rpc("JSONRPC.Ping"); break
            except Exception:
                assert process.poll() is None
                time.sleep(.3)
        for addon in ("script.image.resource.select", "resource.images.weathericons.outline", "resource.images.weatherfanart.multi"):
            assert rpc("Addons.SetAddonEnabled", {"addonid":addon,"enabled":True}) == "OK"
        client = XBMCClient(name="HorizonzV resource selector", uid=secrets.randbits(32)); client.connect(port=9777)
        time.sleep(.2)
        client.send_action('RunScript("' + script.as_posix() + '")')
        wait(lambda:boolean("Control.IsVisible(100)"), True)
        for cid, phase, prop, select in [(100,"baseline_cancel","weatherfanart",False),(101,"single_cancel","weatherfanart",False),(101,"fanart_select","weatherfanart",True),(102,"icons_select","weathericons",True),(101,"fanart_none","weatherfanart",None),(102,"icons_none","weathericons",None)]:
            before = state(prop); offset = len(loglines())
            client.send_action("Control.SetFocus(" + str(cid) + ")"); time.sleep(.2)
            rpc("Input.Select")
            wait(lambda:boolean("Window.IsVisible(selectdialog)"), True)
            time.sleep(.4)
            if select is False:
                rpc("Input.Back")
            else:
                if select is True:
                    addon_id = "resource.images.weatherfanart.multi" if prop == "weatherfanart" else "resource.images.weathericons.outline"
                    addons = rpc("Addons.GetAddons", {"type":"kodi.resource.images","properties":["name"]})["addons"]
                    choices = [a for a in sorted(addons, key=lambda a:a["name"]) if a["addonid"].startswith("resource.images." + prop)]
                    position = next(i for i,a in enumerate(choices,1) if a["addonid"] == addon_id)
                    for _ in range(position):
                        rpc("Input.Down")
                        time.sleep(.05)
                rpc("Input.Select")
            wait(lambda:boolean("Window.IsVisible(selectdialog)"), False)
            time.sleep(.5)
            # Cancel a second dialog if the duplicate dispatch created one.
            second = boolean("Window.IsVisible(selectdialog)")
            if second:
                rpc("Input.Back")
                wait(lambda:boolean("Window.IsVisible(selectdialog)"), False)
            after = state(prop)
            lines = loglines()[offset:]
            starts = sum("script.image.resource.select: script started" in s for s in lines)
            row = {"phase":phase,"before":before,"after":after,"second_dialog":second,"provider_starts":starts,"provider_log":[s for s in lines if "script.image.resource.select" in s]}
            report["phases"].append(row)
            assert starts == (2 if phase == "baseline_cancel" else 1), row
            if select is False:
                assert before == after, row
            elif select is None:
                assert after == {"name":"","path":"","ext":"","multi":False}, row
            else:
                expected = "resource://resource.images.weatherfanart.multi/" if prop == "weatherfanart" else "resource://resource.images.weathericons.outline/"
                assert after["path"] == expected and after["multi"] == (prop == "weatherfanart") and after["ext"] == ("" if prop == "weatherfanart" else ".png"), row
            if phase == "fanart_select":
                screenshot = repo / "results/kodi22_runtime/image_resource_selector.png"
                screenshot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")'); wait(screenshot.exists, True)
        rpc("Input.Back")
    except Exception as exc:
        failure = repr(exc); report["failure"] = failure; report["failure_trace"] = traceback.format_exc()
    finally:
        if process:
            try:
                raw_rpc("Application.Quit"); process.wait(timeout=20)
            except Exception:
                pass
        if client:
            client.close()
        exited = process is None or process.poll() is not None
        cleanup = {"process_exited":exited}
        if exited:
            for rel in rels:
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
            cleanup["all_test_xml_match_production"] = {p.name:p.read_bytes() for p in xml.glob("*.xml")} == {p.name:p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        cleanup["standard_addons_unchanged"] = all(hashlib.sha256((repo.parent / name).read_bytes()).hexdigest() == digest for name,digest in hashes.items())
        cleanup["test_addon_copies_unchanged"] = all(hashlib.sha256((root / "portable_data/addons" / name).read_bytes()).hexdigest() == digest for name,digest in hashes.items())
        report["cleanup"] = cleanup
        report["error_lines"] = [s for s in loglines() if " error " in s.lower() or "fatal" in s.lower()]
        (repo / "results/kodi22_runtime/image_resource_checks.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"failure":failure,"phases":[{k:v for k,v in row.items() if k!='provider_log'} for row in report['phases']],"errors":len(report.get('error_lines',[])),"cleanup":cleanup},ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
