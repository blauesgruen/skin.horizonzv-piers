"""Own temporary plugin playback; production player fanart and request log."""
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
    work = Path(tempfile.mkdtemp(prefix="review-plugin-player-fanart-", dir=root))
    media = work / "media"
    art = media / "extrafanart"
    art.mkdir(parents=True)
    for name in ("first.avi", "second.avi"):
        shutil.copy2(root / "portable_data/testmedia/skin-audit-video.avi", media / name)
    shutil.copy2(repo / "backgrounds/gambit/background.jpg", art / "stack-fanart.jpg")
    profile = root / "portable_data"
    backups = {rel: (profile / rel).read_bytes() for rel in ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")}
    for i, data in enumerate(backups.values()):
        (work / f"profile-{i}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    def db_files():
        return [p for p in database.iterdir() if p.is_file() and (p.name.startswith("MyVideos") or p.name.startswith("Addons")) and ".db" in p.name]

    db_backup = {p.name: p.read_bytes() for p in db_files()}
    saved_db = work / "database"
    saved_db.mkdir()
    for name, data in db_backup.items():
        (saved_db / name).write_bytes(data)
    addon_id = "plugin.video.horizonzv.fanartprobe"
    fixture = profile / "addons" / addon_id
    assert not fixture.exists(), "Own fixture ID already exists"
    fixture.mkdir()
    (fixture / "addon.xml").write_text('<addon id="' + addon_id + '" name="HorizonzV Fanart Test Fixture" version="0.0.1" provider-name="Local test fixture"><requires><import addon="xbmc.python" version="3.0.0" /></requires><extension point="xbmc.python.pluginsource" library="default.py"><provides>video</provides></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Authored local test fixture only</summary><description lang="en_GB">Records routes and resolves own local AVI media.</description><platform>all</platform><license>MIT</license></extension></addon>', encoding="utf-8")
    requests = work / "requests.jsonl"
    plugin_source = '''import json,sys
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import xbmcgui,xbmcplugin
work=Path(WORK)
uri=sys.argv[0]+sys.argv[2]
with (work/'requests.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'uri':uri,'argv':sys.argv})+'\\n')
handle=int(sys.argv[1])
if urlsplit(sys.argv[0]).path!='/play':
 xbmcplugin.endOfDirectory(handle,False)
else:
 mode=parse_qs(sys.argv[2].lstrip('?')).get('mode',['local'])[0]
 first=(work/'media/first.avi').as_posix()
 path=first if mode=='local' else 'stack://'+first+' , '+(work/'media/second.avi').as_posix()
 item=xbmcgui.ListItem(label='Authored plugin video '+mode,path=path)
 item.setProperty('IsPlayable','true')
 item.getVideoInfoTag().setTitle('Authored plugin video '+mode)
 xbmcplugin.setResolvedUrl(handle,True,item)
'''.replace("WORK", repr(str(work)))
    (fixture / "default.py").write_text(plugin_source, encoding="utf-8")
    xml = profile / "addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        data = raw_rpc(method, params)
        assert "result" in data, data
        return data["result"]

    def labels(exprs):
        return rpc("XBMC.GetInfoLabels", {"labels": exprs})

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def wait(probe, expected):
        for _ in range(150):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})

    report = {"scope": "Real playback via a temporary authored plugin resolving local AVI and local stack; production Home multiimage 2016 and fixture route requests. No existing addon code changed. Not Disney DRM, SMB, plugin-containing stack URI or all-wrapper acceptance.", "work": str(work), "fixture_id": addon_id, "rows": []}
    process = client = None
    failure = None
    try:
        config = ET.parse(profile / "userdata/guisettings.xml")
        for name, value in {"input.enablemouse": "false", "debug.showloginfo": "false", "window.width": "1280", "window.height": "720"}.items():
            node = config.find(f"setting[@id='{name}']")
            assert node is not None
            node.text = value
            node.attrib.pop("default", None)
        config.write(profile / "userdata/guisettings.xml", encoding="utf-8", xml_declaration=True)
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
        details = rpc("Addons.GetAddonDetails", {"addonid": addon_id, "properties": ["enabled", "version"]})["addon"]
        report["fixture_registered"] = details
        if not details["enabled"]:
            rpc("Addons.SetAddonEnabled", {"addonid": addon_id, "enabled": True})
        client = XBMCClient(name="HorizonzV plugin player fanart", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action("Skin.Reset(BackgroundVideo)")
        wait(lambda: boolean("Skin.HasSetting(BackgroundVideo)"), False)
        client.send_action("Skin.Reset(WeatherFanartHome)")
        wait(lambda: boolean("Skin.HasSetting(WeatherFanartHome)"), False)
        cases = [("plugin_resolves_local", "plugin://" + addon_id + "/play?mode=local"), ("plugin_resolves_stack", "plugin://" + addon_id + "/play?mode=stack")]
        for name, path in cases:
            rpc("Player.Open", {"item": {"file": path}})
            wait(lambda: boolean("Player.HasVideo"), True)
            wait(lambda: rpc("Player.GetProperties", {"playerid": 1, "properties": ["time"]})["time"]["seconds"] >= 1, True)
            rpc("GUI.ActivateWindow", {"window": "home"})
            wait(lambda: boolean("Window.IsActive(home)"), True)
            time.sleep(.6)
            folder = labels(["Player.FolderPath"])["Player.FolderPath"]
            assert folder.startswith("plugin://"), folder
            wait(lambda: labels(["Control.GetLabel(2016)"])["Control.GetLabel(2016)"], "")
            exprs = ["Player.FolderPath", "Player.FilenameAndPath", "Control.GetLabel(2016)", "Skin.AspectRatio"]
            row = {"case": name, "requested_file": path, "labels": labels(exprs), "fanart_control_visible": boolean("Control.IsVisible(2016)"), "player_item": rpc("Player.GetItem", {"playerid": 1, "properties": ["file"]})}
            report["rows"].append(row)
            assert not row["fanart_control_visible"], row
            assert row["labels"]["Player.FilenameAndPath"] == path, row
            row["folder_is_plugin"] = folder.startswith("plugin://")
            row["requests"] = [json.loads(line) for line in requests.read_text(encoding="utf-8").splitlines()]
            assert all("extrafanart" not in call["uri"].lower() for call in row["requests"]), row
            if name == "plugin_resolves_stack":
                image = repo / "results/kodi22_runtime/plugin_player_fanart.png"
                image.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("' + image.as_posix() + '")')
                wait(image.exists, True)
            rpc("Player.Stop", {"playerid": 1})
            wait(lambda: boolean("Player.HasVideo"), False)
            wait(lambda: labels(["Player.FolderPath"])["Player.FolderPath"], "")
        report["after_stop"] = labels(["Player.FolderPath", "Control.GetLabel(2016)"])
        assert len([json.loads(line) for line in requests.read_text(encoding="utf-8").splitlines()]) == len(cases)
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
        try:
            report["failure_context"] = {"gui": rpc("GUI.GetProperties", {"properties": ["currentwindow"]}), "labels": labels(["Player.FolderPath", "Control.GetLabel(2016)", "Container(9000).ListItem.Property(homemenu_id)"]), "control_visible": boolean("Control.IsVisible(2016)"), "video_background_visible": boolean("Control.IsVisible(2015)")}
        except Exception:
            pass
    finally:
        if process and process.poll() is None:
            try:
                if boolean("Player.HasVideo"):
                    rpc("Player.Stop", {"playerid": 1})
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
            extra = work / "new-video-database-files"
            extra.mkdir(exist_ok=True)
            for p in db_files():
                if p.name not in db_backup:
                    assert root.resolve() in p.resolve().parents and root.resolve() in extra.resolve().parents
                    p.rename(extra / p.name)
            for name, data in db_backup.items():
                (database / name).write_bytes(data)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            cleanup["video_and_addon_databases_restored"] = {p.name: p.read_bytes() for p in db_files()} == db_backup
            assert root.resolve() in fixture.resolve().parents and root.resolve() in work.resolve().parents
            fixture.rename(work / "fixture-addon")
            cleanup["fixture_removed_from_addon_directory"] = not fixture.exists()
            cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [s for s in lines if " error " in s.lower() or "fatal" in s.lower()]
        report["requests"] = [json.loads(line) for line in requests.read_text(encoding="utf-8").splitlines()] if requests.exists() else []
        (repo / "results/kodi22_runtime/plugin_player_fanart_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "after_stop": report.get("after_stop"), "errors": len(report["errors"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
