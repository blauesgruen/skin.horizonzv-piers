"""Visible actual Global Search entry, results, view switch, info and empty search."""
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
import zipfile
from pathlib import Path


def main():
    stage = sys.argv[1]
    assert stage in ("baseline", "current")
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    archive_dir = Path((Path(tempfile.gettempdir()) / "horizonzv-current-globalsearch-download.txt").read_text(encoding="utf-8-sig").strip())
    archive = archive_dir / "script.globalsearch-9.2.1.zip"
    addons = root / "portable_data/addons"
    hashes = {}
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith("/"):
                continue
            target = addons / name
            assert name.startswith("script.globalsearch/") and target.resolve().is_relative_to((addons / "script.globalsearch").resolve())
            content = z.read(name)
            hashes[name] = hashlib.sha256(content).hexdigest()
            if target.exists():
                assert target.read_bytes() == content, "Existing addon copy differs"
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
    work = Path(tempfile.mkdtemp(prefix="review-globalsearch-" + stage + "-", dir=root))
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml", "userdata/addon_data/script.globalsearch/settings.xml")
    backups = {}
    for index, rel in enumerate(rels):
        path = root / "portable_data" / rel
        backups[rel] = path.read_bytes() if path.exists() else None
        if path.exists():
            shutil.copy2(path, work / (str(index) + "-settings.xml"))
    xml = addons / "skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    if stage == "baseline":
        (xml / "script-globalsearch.xml").unlink(missing_ok=True)
        (xml / "script-globalsearch-main.xml").write_bytes(subprocess.check_output(["git", "-c", "safe.directory=" + repo.as_posix(), "show", "ca3e276:xml/script-globalsearch-main.xml"]))
    else:
        (xml / "script-globalsearch-main.xml").unlink(missing_ok=True)
    database = root / "portable_data/userdata/Database"
    db_backup = work / "database"; db_backup.mkdir()
    for pattern in ("MyVideos*.db*", "MyMusic*.db*"):
        for p in database.glob(pattern):
            shutil.copy2(p, db_backup / p.name)
    sys.path.insert(0, str(root)); sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        data = raw_rpc(method, params)
        assert "result" in data, data
        return data["result"]

    def wait(probe, expected, attempts=200):
        for _ in range(attempts):
            value = probe()
            if value == expected:
                return value
            time.sleep(.1)
        raise AssertionError({"expected":expected,"actual":value})

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans":[expr]})[expr]

    def label(expr):
        return rpc("XBMC.GetInfoLabels", {"labels":[expr]})[expr]

    def snapshot(name):
        props = rpc("GUI.GetProperties", {"properties":["currentwindow","currentcontrol"]})
        return {"phase":name,"gui":props,"menu_items":label("Container(9000).NumItems"),"view50_items":label("Container(50).NumItems"),"view51_items":label("Container(51).NumItems"),"label50":label("Container(50).ListItem.Label"),"label51":label("Container(51).ListItem.Label"),"no_results_visible":boolean("Control.IsVisible(999)"),"new_search_visible":boolean("Control.IsVisible(990)"),"query":label("Window.Property(GlobalSearch.SearchString)")}

    def search(query):
        client.send_action("RunScript(script.globalsearch)")
        wait(lambda:boolean("Window.IsVisible(virtualkeyboard)"), True)
        rpc("Input.SendText", {"text":query,"done":True})
        wait(lambda:boolean("Window.IsVisible(script-globalsearch.xml)"), True)
        wait(lambda:boolean("Control.IsVisible(990)"), True)
        wait(lambda:label("Container(50).ListItem.Label"), "Skin Audit Movie")

    def screenshot(name):
        p = repo / "results/kodi22_runtime" / ("globalsearch_" + stage + "_" + name + ".png")
        p.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + p.as_posix() + '")')
        wait(p.exists, True)

    report = {"stage":stage,"scope":"Actual unchanged official Global Search 9.2.1; exact no-argument skin entry and native keyboard. Own existing movie; no provider code modification.","archive_sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"source_hashes":hashes,"phases":[]}
    process = client = None; failure = None
    try:
        gui_path = root / "portable_data/userdata/guisettings.xml"
        config = ET.parse(gui_path)
        debug = config.getroot().find("setting[@id='debug.showloginfo']")
        assert debug is not None; debug.text = "false"; debug.attrib.pop("default", None)
        mouse = config.getroot().find("setting[@id='input.enablemouse']")
        assert mouse is not None; mouse.text = "false"; mouse.attrib.pop("default", None)
        config.write(gui_path,encoding="utf-8",xml_declaration=True)
        provider_settings = root / "portable_data/userdata/addon_data/script.globalsearch/settings.xml"
        provider_settings.parent.mkdir(parents=True,exist_ok=True)
        provider_settings.write_text('<settings version="2"><setting id="movies">true</setting><setting id="tvshows">false</setting><setting id="episodes">false</setting><setting id="musicvideos">false</setting><setting id="artists">false</setting><setting id="albums">false</setting><setting id="songs">false</setting><setting id="livetv">false</setting><setting id="actors">false</setting><setting id="tvactors">false</setting><setting id="directors">false</setting><setting id="view">50</setting></settings>',encoding="utf-8")
        startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"),"-p","-w"],cwd=root,startupinfo=startup); report["pid"] = process.pid
        for _ in range(60):
            try:
                rpc("JSONRPC.Ping"); break
            except Exception:
                assert process.poll() is None; time.sleep(.3)
        assert rpc("Addons.SetAddonEnabled", {"addonid":"script.globalsearch","enabled":True}) == "OK"
        assert len(rpc("VideoLibrary.GetMovies").get("movies",[])) == 1
        client = XBMCClient(name="HorizonzV Global Search " + stage,uid=secrets.randbits(32)); client.connect(port=9777); time.sleep(.2)
        client.send_action("RunScript(script.globalsearch)")
        wait(lambda:boolean("Window.IsVisible(virtualkeyboard)"), True)
        rpc("Input.Back")
        wait(lambda:boolean("Window.IsVisible(virtualkeyboard)"), False)
        assert not boolean("Window.IsVisible(script-globalsearch.xml)")
        report["phases"].append({"phase":"initial_cancel","search_window_not_opened":True})
        search("Skin Audit")
        client.send_action("Control.SetFocus(50)"); time.sleep(.2)
        assert label("Container(50).ListItem.Label") == "Skin Audit Movie"
        report["phases"].append(snapshot("movie_view50")); screenshot("movie50")
        if stage == "current":
            client.send_action("Control.SetFocus(2)"); time.sleep(.2); rpc("Input.Select")
        else:
            client.send_action("Container.SetViewMode(51)")
        time.sleep(.2); client.send_action("Control.SetFocus(51)")
        wait(lambda:boolean("Control.IsVisible(51)"), True)
        assert label("Container(51).ListItem.Label") == "Skin Audit Movie"
        report["phases"].append(snapshot("movie_view51")); screenshot("movie51")
        if stage == "current":
            rpc("Input.Left"); wait(lambda:boolean("Control.HasFocus(9000)"), True)
            rpc("Input.Right"); wait(lambda:boolean("Control.HasFocus(51)"), True)
            report["phases"].append({"phase":"category_result_navigation","left_to_menu_and_right_to_active_view":True})
        rpc("Input.Info")
        wait(lambda:boolean("Window.IsVisible(movieinformation)"), True)
        report["phases"].append({"phase":"movie_information","title":label("ListItem.Title")})
        rpc("Input.Back"); wait(lambda:boolean("Window.IsVisible(movieinformation)"), False)
        client.send_action("Control.SetFocus(990)"); time.sleep(.2); rpc("Input.Select")
        wait(lambda:boolean("Window.IsVisible(virtualkeyboard)"), True)
        rpc("Input.SendText", {"text":"HorizonzV_No_Result_2026","done":True})
        # The unchanged provider opens a yes/no prompt over the empty-results
        # label. Current-window control queries therefore refer to the prompt.
        wait(lambda:boolean("Window.IsVisible(DialogConfirm.xml)"), True)
        report["phases"].append({"phase":"empty_results_prompt","search_window_visible":boolean("Window.IsVisible(script-globalsearch.xml)")})
        screenshot("empty")
        rpc("Input.Back"); wait(lambda:boolean("Window.IsVisible(script-globalsearch.xml)"), False)
    except Exception as exc:
        failure = repr(exc); report["failure"] = failure; report["failure_trace"] = traceback.format_exc()
    finally:
        if process:
            try:
                for _ in range(3):
                    raw_rpc("Input.Back")
                    time.sleep(.2)
                raw_rpc("Application.Quit"); process.wait(timeout=20)
            except Exception:
                pass
        if client: client.close()
        exited = process is None or process.poll() is not None
        cleanup = {"process_exited":exited}
        if exited:
            for rel, content in backups.items():
                p = root / "portable_data" / rel
                if content is None: p.unlink(missing_ok=True)
                else: p.write_bytes(content)
            cleanup["profile_restored"] = all((root/"portable_data"/rel).read_bytes()==data if data is not None else not (root/"portable_data"/rel).exists() for rel,data in backups.items())
            for pattern in ("MyVideos*.db*", "MyMusic*.db*"):
                for p in database.glob(pattern):
                    assert p.resolve().parent == database.resolve(); p.unlink()
            for p in db_backup.iterdir(): shutil.copy2(p,database/p.name)
            cleanup["media_databases_restored"] = all(p.read_bytes()==(database/p.name).read_bytes() for p in db_backup.iterdir())
            for p in (repo / "xml").glob("*.xml"):
                shutil.copy2(p, xml / p.name)
            if not (repo / "xml/script-globalsearch-main.xml").exists():
                (xml / "script-globalsearch-main.xml").unlink(missing_ok=True)
            cleanup["skin_xml_match_production"] = {p.name:p.read_bytes() for p in xml.glob('*.xml')} == {p.name:p.read_bytes() for p in (repo/'xml').glob('*.xml')}
        cleanup["provider_copy_matches_archive"] = all(hashlib.sha256((addons/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items())
        report["cleanup"] = cleanup
        log = (root / "portable_data/kodi.log").read_text(encoding="utf-8",errors="replace").splitlines()
        report["layout_log"] = [s for s in log if "globalsearch" in s.lower() and any(t in s for t in ("Loading", "Window Init", "Running", "DEBUG", "debug", "error"))]
        report["error_lines"] = [s for s in log if " error " in s.lower() or "fatal" in s.lower()]
        (repo / "results/kodi22_runtime" / ("globalsearch_"+stage+"_checks.json")).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"failure":failure,"phases":report['phases'],"errors":report.get('error_lines',[]),"cleanup":cleanup},ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
