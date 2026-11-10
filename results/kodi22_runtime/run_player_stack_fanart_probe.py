"""Actual local stack playback and the production player-fanart control."""
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
    work = Path(tempfile.mkdtemp(prefix="review-player-stack-fanart-", dir=root))
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
    db_backup = {p.name: p.read_bytes() for p in database.glob("MyVideos*.db*")}
    saved_db = work / "database"
    saved_db.mkdir()
    for name, data in db_backup.items():
        (saved_db / name).write_bytes(data)
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

    def normalize(value):
        return value.replace("\\", "/").rstrip("/")

    report = {"scope": "Actual Player.Open stack of two authored local AVI files, production Home multiimage 2016. No plugin, SMB, second-part transition or malformed/mixed-wrapper test.", "rows": []}
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
        client = XBMCClient(name="HorizonzV player stack fanart", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action("Skin.Reset(BackgroundVideo)")
        wait(lambda: boolean("Skin.HasSetting(BackgroundVideo)"), False)
        client.send_action("Skin.Reset(WeatherFanartHome)")
        wait(lambda: boolean("Skin.HasSetting(WeatherFanartHome)"), False)
        # The same media folder is used for the ordinary and stack playback cases.
        cases = [("ordinary_local_file", (media / "first.avi").as_posix()), ("local_stack", "stack://" + (media / "first.avi").as_posix() + " , " + (media / "second.avi").as_posix())]
        for name, path in cases:
            rpc("Player.Open", {"item": {"file": path}})
            wait(lambda: boolean("Player.HasVideo"), True)
            wait(lambda: rpc("Player.GetProperties", {"playerid": 1, "properties": ["time"]})["time"]["seconds"] >= 1, True)
            rpc("GUI.ActivateWindow", {"window": "home"})
            wait(lambda: boolean("Window.IsActive(home)"), True)
            wait(lambda: normalize(labels(["Player.FolderPath"])["Player.FolderPath"]), normalize(media.as_posix()))
            wait(lambda: normalize(labels(["Control.GetLabel(2016)"])["Control.GetLabel(2016)"]), normalize((art / "stack-fanart.jpg").as_posix()))
            exprs = ["Player.FolderPath", "Player.FilenameAndPath", "Control.GetLabel(2016)", "Skin.AspectRatio"]
            row = {"case": name, "requested_file": path, "labels": labels(exprs), "fanart_control_visible": boolean("Control.IsVisible(2016)"), "player_item": rpc("Player.GetItem", {"playerid": 1, "properties": ["file"]})}
            report["rows"].append(row)
            assert row["fanart_control_visible"], row
            if name == "local_stack":
                assert row["labels"]["Player.FilenameAndPath"].startswith("stack://"), row
                assert row["player_item"]["item"]["file"].startswith("stack://"), row
            if name == "local_stack":
                image = repo / "results/kodi22_runtime/player_stack_fanart.png"
                image.unlink(missing_ok=True)
                client.send_action('TakeScreenshot("' + image.as_posix() + '")')
                wait(image.exists, True)
            rpc("Player.Stop", {"playerid": 1})
            wait(lambda: boolean("Player.HasVideo"), False)
            wait(lambda: labels(["Player.FolderPath"])["Player.FolderPath"], "")
        report["after_stop"] = labels(["Player.FolderPath", "Control.GetLabel(2016)"])
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
            for p in database.glob("MyVideos*.db*"):
                if p.name not in db_backup:
                    assert root.resolve() in p.resolve().parents and root.resolve() in extra.resolve().parents
                    p.rename(extra / p.name)
            for name, data in db_backup.items():
                (database / name).write_bytes(data)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            cleanup["video_databases_restored"] = {p.name: p.read_bytes() for p in database.glob("MyVideos*.db*")} == db_backup
            cleanup["skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [s for s in lines if " error " in s.lower() or "fatal" in s.lower()]
        (repo / "results/kodi22_runtime/player_stack_fanart_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "rows": report["rows"], "after_stop": report.get("after_stop"), "errors": len(report["errors"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
