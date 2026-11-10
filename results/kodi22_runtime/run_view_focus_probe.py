"""Visible native view loading/focus, with restored local test media databases."""
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
    work = Path(tempfile.mkdtemp(prefix="review-view-focus-", dir=root))
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    backups = {rel:(root / "portable_data" / rel).read_bytes() for rel in rels}
    database = root / "portable_data/userdata/Database"
    saved = work / "database"; saved.mkdir()
    for pattern in ("MyVideos*.db*", "MyMusic*.db*"):
        for p in database.glob(pattern):
            shutil.copy2(p, saved / p.name)
    xml = root / "portable_data/addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    music = work / "music"; music.mkdir()
    sys.path.insert(0, str(root / "portable_data/addons/script.module.mutagen/lib"))
    from mutagen.wave import WAVE
    from mutagen.id3 import TIT2, TPE1, TALB
    song = music / "view-focus.wav"
    shutil.copy2(root / "portable_data/testmedia/skin-audit-silence.wav", song)
    tags = WAVE(song)
    if tags.tags is None:
        tags.add_tags()
    for item in (TIT2(encoding=3,text="View Focus Song"), TPE1(encoding=3,text="View Focus Artist"), TALB(encoding=3,text="View Focus Album")):
        tags.tags.add(item)
    tags.save()
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        data = raw_rpc(method, params)
        assert "result" in data, data
        return data["result"]

    def label(name):
        return rpc("XBMC.GetInfoLabels", {"labels":[name]})[name]

    def boolean(name):
        return rpc("XBMC.GetInfoBooleans", {"booleans":[name]})[name]

    def wait(probe, expected):
        for _ in range(200):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected":expected,"actual":actual})

    report = {"scope":"Actual skin movie/music views, enabled animation preference, native focus and selected-item verification. No playback or comprehensive animation-curve comparison.","rows":[]}
    process = client = None; failure = None
    try:
        gui = root / "portable_data/userdata/guisettings.xml"
        config = ET.parse(gui)
        for key, value in (("window.width","1280"),("window.height","720"),("input.enablemouse","false"),("debug.showloginfo","false")):
            node = config.getroot().find("setting[@id='"+key+"']")
            assert node is not None
            node.text = value; node.attrib.pop("default", None)
        config.write(gui,encoding="utf-8",xml_declaration=True)
        startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"),"-p","-w"],cwd=root,startupinfo=startup)
        report["pid"] = process.pid
        for _ in range(60):
            try:
                rpc("JSONRPC.Ping"); break
            except Exception:
                assert process.poll() is None; time.sleep(.3)
        client = XBMCClient(name="HorizonzV view focus",uid=secrets.randbits(32)); client.connect(port=9777); time.sleep(.2)
        client.send_action("Skin.SetBool(animation)")
        wait(lambda:boolean("Skin.HasSetting(animation)"), True)
        assert len(rpc("VideoLibrary.GetMovies").get("movies",[])) == 1
        assert not rpc("AudioLibrary.GetSongs").get("songs",[])
        rpc("AudioLibrary.Scan", {"directory":str(music),"showdialogs":False})
        wait(lambda:len(rpc("AudioLibrary.GetSongs").get("songs",[])), 1)
        wait(lambda:boolean("Library.IsScanningMusic"), False)
        for window, uri, title, views in (("videos","videodb://movies/titles/","Skin Audit Movie",(515,562,502,505)),("music","musicdb://songs/","View Focus Song",(515,562,505))):
            rpc("GUI.ActivateWindow", {"window":window,"parameters":[uri,"return"]})
            time.sleep(.4)
            for view in views:
                client.send_action("Container.SetViewMode("+str(view)+")")
                wait(lambda:boolean("Control.IsVisible("+str(view)+")"), True)
                client.send_action("Control.SetFocus("+str(view)+")")
                wait(lambda:boolean("Control.HasFocus("+str(view)+")"), True)
                for _ in range(6):
                    if label("Container("+str(view)+").ListItem.Title") == title:
                        break
                    rpc("Input.Down"); time.sleep(.2)
                wait(lambda:label("Container("+str(view)+").ListItem.Title"), title)
                time.sleep(.7)
                row = {"window":window,"viewid":view,"selected":label("Container("+str(view)+").ListItem.Title"),"display_label":label("Container("+str(view)+").ListItem.Label"),"has_focus":boolean("Control.HasFocus("+str(view)+")"),"music_context":boolean("Window.IsActive(music)"),"animation_enabled":boolean("Skin.HasSetting(animation)"),"aspect_ratio":label("Skin.AspectRatio")}
                assert row['music_context'] == (window == "music")
                report['rows'].append(row)
                shot = repo / "results/kodi22_runtime" / ("view_focus_"+window+"_"+str(view)+".png")
                shot.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("'+shot.as_posix()+'")'); wait(shot.exists, True)
    except Exception as exc:
        failure = repr(exc); report['failure'] = failure; report['failure_trace'] = traceback.format_exc()
        if process and process.poll() is None:
            report['failure_context'] = rpc("GUI.GetProperties", {"properties":["currentwindow","currentcontrol"]})
            report['failure_labels'] = rpc("XBMC.GetInfoLabels", {"labels":["Container(515).NumItems","Container(515).ListItemAbsolute(0).Label","Container(515).ListItemAbsolute(1).Label","Container(515).ListItemAbsolute(1).Title","Container.FolderPath"]})
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
            for rel,data in backups.items():
                (root / "portable_data" / rel).write_bytes(data)
            cleanup['profile_restored'] = all((root/"portable_data"/rel).read_bytes()==data for rel,data in backups.items())
            for pattern in ("MyVideos*.db*","MyMusic*.db*"):
                for p in database.glob(pattern):
                    assert p.resolve().parent == database.resolve(); p.unlink()
            for p in saved.iterdir():
                shutil.copy2(p,database/p.name)
            current_names = sorted(p.name for pattern in ("MyVideos*.db*","MyMusic*.db*") for p in database.glob(pattern))
            cleanup['media_databases_restored'] = sorted(p.name for p in saved.iterdir()) == current_names and all(p.read_bytes()==(database/p.name).read_bytes() for p in saved.iterdir())
            cleanup['skin_xml_match_production'] = {p.name:p.read_bytes() for p in xml.glob('*.xml')} == {p.name:p.read_bytes() for p in (repo/'xml').glob('*.xml')}
        report['cleanup'] = cleanup
        lines = (root / "portable_data/kodi.log").read_text(encoding='utf-8',errors='replace').splitlines()
        report['errors'] = [s for s in lines if ' error ' in s.lower() or 'fatal' in s.lower()]
        (repo / 'results/kodi22_runtime/view_focus_checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == '__main__':
    sys.exit(main())
