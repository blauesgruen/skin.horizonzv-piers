"""Visible native lyrics entry using unchanged CU LRC and authored local LRC.

Only an isolated profile is configured. No online scraper is enabled.
"""
import argparse
import hashlib
import json
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import wave
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--background-service", action="store_true")
    parser.add_argument("--report-prefix")
    args = parser.parse_args()
    artifact = args.report_prefix or ("lyrics_background" if args.background_service else "lyrics_visualisation")
    assert artifact and all(c.isalnum() or c == "_" for c in artifact)
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-local-lyrics-", dir=root))
    addons = root / "portable_data/addons"
    copied = {}
    seen = set()

    def install_copy(name):
        if name.startswith("xbmc.") or name in seen:
            return
        seen.add(name)
        dest = addons / name
        if not dest.exists():
            source = repo.parent / name
            assert (source / "addon.xml").is_file(), name
            paths = [p for p in source.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git", "__pycache__", ".codex"))]
            hashes = {}
            for p in paths:
                rel = p.relative_to(source)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                hashes[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
            copied[name] = hashes
        for dep in ET.parse(dest / "addon.xml").getroot().findall("requires/import"):
            if dep.get("optional") != "true":
                install_copy(dep.get("addon"))

    install_copy("script.cu.lrclyrics")
    for name in ("script.cu.lrclyrics", "script.module.beautifulsoup4", "script.module.soupsieve", "script.module.mutagen"):
        if name not in copied:
            source = repo.parent / name
            copied[name] = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in source.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git", "__pycache__", ".codex"))}
            assert all(hashlib.sha256((addons / name / rel).read_bytes()).hexdigest() == digest for rel, digest in copied[name].items())
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    xml = addons / "skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    provider_settings = root / "portable_data/userdata/addon_data/script.cu.lrclyrics/settings.xml"
    previous = provider_settings.read_bytes() if provider_settings.exists() else None
    config = ET.Element("settings", {"version": "2"})
    defaults = {}
    for setting in ET.parse(addons / "script.cu.lrclyrics/resources/settings.xml").getroot().iter("setting"):
        if setting.find("default") is not None:
            defaults[setting.get("id")] = setting.findtext("default") or ""
    for scraper in (addons / "script.cu.lrclyrics/lib/culrcscrapers").iterdir():
        if scraper.is_dir() and scraper.name != "__pycache__":
            defaults[scraper.name] = "false"
    defaults.update(service="true" if args.background_service else "false", hide_dialog="false", search_lrc_file="true", search_txt_file="false", search_embedded="false", log_enabled="true", save_lyrics_path=str(work / "lyrics-cache"))
    for name in list(defaults):
        if name.startswith("save_lyrics") and name != "save_lyrics_path":
            defaults[name] = "false"
    # This provider uses the save-location choice for local lookup as well.
    # Enable the song-directory location; only authored files exist there.
    defaults["save_lyrics2_lrc"] = "true"
    for name, value in defaults.items():
        ET.SubElement(config, "setting", {"id": name}).text = value
    provider_settings.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(config).write(provider_settings, encoding="utf-8", xml_declaration=True)
    audio = work / "lyrics-audit.wav"
    with wave.open(str(root / "portable_data/testmedia/skin-audit-silence.wav"), "rb") as source:
        params, data = source.getparams(), source.readframes(source.getnframes())
    with wave.open(str(audio), "wb") as dest:
        dest.setparams(params)
        dest.writeframes(data * 3)
    sys.path.insert(0, str(addons / "script.module.mutagen/lib"))
    from mutagen.wave import WAVE
    from mutagen.id3 import TIT2, TPE1, TALB
    tags = WAVE(audio)
    tags.add_tags()
    tags.tags.add(TIT2(encoding=3, text="HorizonzV Lyrics Audit"))
    tags.tags.add(TPE1(encoding=3, text="HorizonzV Audit Artist"))
    tags.tags.add(TALB(encoding=3, text="Local Skin Test"))
    tags.save()
    audio.with_suffix(".lrc").write_text("[00:00.00]HorizonzV audit line one\n[00:03.00]Native lyrics entry works\n[00:06.00]Authored local fixture\n", encoding="utf-8")
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient

    def label(name):
        return rpc("XBMC.GetInfoLabels", {"labels": [name]})["result"][name]

    def boolean(name):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [name]})["result"][name]

    def wait(probe, expected, attempts=150):
        for _ in range(attempts):
            value = probe()
            if value == expected:
                return value
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": value})

    def snapshot():
        keys = ["Window(Home).Property(culrc.running)", "Window(Home).Property(culrc.guirunning)", "Window(Home).Property(culrc.lyrics)", "Window(Home).Property(culrc.source)", "MusicPlayer.Title", "MusicPlayer.Artist", "System.CurrentWindow", "System.CurrentControlID"]
        return rpc("XBMC.GetInfoLabels", {"labels": keys})["result"]

    def provider_invokers():
        log = (root / "portable_data/kodi.log").read_text(encoding="utf-8", errors="replace")
        return sorted({int(x) for x in re.findall(r"CPythonInvoker\((\d+), [^\r\n]*[\\/]script\.cu\.lrclyrics[\\/]default\.py\)", log)})

    def osd_lyrics_start():
        rpc("GUI.ActivateWindow", {"window": "musicosd"})
        wait(lambda: boolean("Window.IsVisible(musicosd)"), True)
        time.sleep(.3)
        client.send_action("Control.SetFocus(701)")
        wait(lambda: boolean("Control.HasFocus(701)"), True)
        rpc("Input.Select")
        wait(lambda: boolean("Skin.HasSetting(Lyrics)"), True)
        # An already-visible provider needs no startup delay. Wait for the OSD's
        # actual close instead of racing a second OSD activation with its fade.
        wait(lambda: boolean("Window.IsVisible(musicosd)"), False)
        wait(lambda: label("Window(Home).Property(culrc.running)"), "true")
        wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), True)
        wait(lambda: "HorizonzV audit line one" in label("Window(Home).Property(culrc.lyrics)"), True)

    report = {"scope": "Native MusicOSD lyrics entry over real Visualisation with unchanged CU LRC 6.7.6 and authored local LRC", "background_service_configured": args.background_service, "verified_addon_files": {name: len(hashes) for name, hashes in copied.items()}, "observations": []}
    process = client = None
    failure = None
    try:
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
        for name in reversed(list(seen)):
            rpc("Addons.SetAddonEnabled", {"addonid": name, "enabled": True})
        client = XBMCClient(name="HorizonzV local lyrics test", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action("Skin.SetString(LyricScript_Path,script.cu.lrclyrics)")
        client.send_action("Skin.Reset(Lyrics)")
        wait(lambda: boolean("Skin.HasSetting(Lyrics)"), False)
        if args.background_service:
            # No provider RunScript has been issued by the fixture at this point.
            wait(lambda: label("Window(Home).Property(culrc.running)"), "true")
            report["background_running_before_playback_or_skin_entry"] = snapshot()
            for setting in ("fanart", "artistslideshow_artistinfos_bio", "artistslideshow_artistinfos_albums", "artistslideshow_artistinfos_similar"):
                client.send_action("Skin.Reset(" + setting + ")")
                wait(lambda: boolean("Skin.HasSetting(" + setting + ")"), False)
        client.send_action('PlayMedia("' + audio.as_posix() + '")')
        wait(lambda: boolean("Player.HasAudio"), True)
        wait(lambda: any(p.get("type") == "audio" for p in rpc("Player.GetActivePlayers")["result"]), True)
        wait(lambda: rpc("Player.GetProperties", {"playerid": 0, "properties": ["time"]})["result"]["time"]["seconds"] >= 2, True)
        # Activate is idempotent, unlike a fullscreen toggle if Kodi already
        # entered Visualisation automatically during audio startup.
        client.send_action("ActivateWindow(visualisation)")
        wait(lambda: boolean("Window.IsVisible(visualisation)"), True)
        if args.background_service:
            wait(lambda: boolean("Skin.HasSetting(Lyrics)"), True)
            wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), True)
            wait(lambda: "HorizonzV audit line one" in label("Window(Home).Property(culrc.lyrics)"), True)
            report["automatic_background_display"] = {"state": snapshot(), "lyrics_setting": boolean("Skin.HasSetting(Lyrics)")}
            original_invokers = provider_invokers()
            assert original_invokers, "Provider invocation IDs missing from native debug log"
            rpc("Input.Back")
            wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), False)
            wait(lambda: label("Window(Home).Property(culrc.guirunning)"), "")
            assert label("Window(Home).Property(culrc.running)") == "true"
            report["background_gui_closed_service_running"] = snapshot()
            osd_lyrics_start()
            assert provider_invokers() == original_invokers
            report["background_force_reshow"] = {"state": snapshot(), "invokers_before": original_invokers, "invokers_after": provider_invokers()}
            # Reuse the same running service through the Home PlayerControls entry.
            rpc("Input.Back")
            wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), False)
            wait(lambda: label("Window(Home).Property(culrc.guirunning)"), "")
            rpc("GUI.ActivateWindow", {"window": "home"})
            wait(lambda: boolean("Window.IsActive(home)"), True)
            client.send_action("ActivateWindow(playercontrols)")
            wait(lambda: boolean("Window.IsVisible(playercontrols)"), True)
            client.send_action("Control.SetFocus(609)")
            wait(lambda: boolean("Control.HasFocus(609)"), True)
            rpc("Input.Select")
            wait(lambda: boolean("Window.IsVisible(playercontrols)"), False)
            client.send_action("ActivateWindow(visualisation)")
            wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), True)
            wait(lambda: "HorizonzV audit line one" in label("Window(Home).Property(culrc.lyrics)"), True)
            assert provider_invokers() == original_invokers
            report["background_playercontrols_reuse"] = {"state": snapshot(), "invokers": provider_invokers()}
            # Exercise the pre-evaluated off->on toggle action in MusicOSD 2401.
            rpc("Input.Back")
            wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), False)
            wait(lambda: label("Window(Home).Property(culrc.guirunning)"), "")
            client.send_action("Skin.Reset(Lyrics)")
            wait(lambda: boolean("Skin.HasSetting(Lyrics)"), False)
            rpc("GUI.ActivateWindow", {"window": "musicosd"})
            wait(lambda: boolean("Window.IsVisible(musicosd)"), True)
            client.send_action("Control.SetFocus(701)")
            wait(lambda: boolean("Control.HasFocus(701)"), True)
            rpc("Input.Down")
            wait(lambda: boolean("Control.IsVisible(2401)"), True)
            client.send_action("Control.SetFocus(2401)")
            wait(lambda: boolean("Control.HasFocus(2401)"), True)
            rpc("Input.Select")
            wait(lambda: boolean("Skin.HasSetting(Lyrics)"), True)
            wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), True)
            wait(lambda: "HorizonzV audit line one" in label("Window(Home).Property(culrc.lyrics)"), True)
            wait(lambda: boolean("Window.IsVisible(musicosd)"), False)
            assert provider_invokers() == original_invokers
            report["background_toggle_reuse"] = {"state": snapshot(), "lyrics_setting": boolean("Skin.HasSetting(Lyrics)"), "invokers": provider_invokers()}
        report["observations"].append({"before_start": snapshot()})
        osd_lyrics_start()
        report["lyrics_setting_after_start"] = boolean("Skin.HasSetting(Lyrics)")
        if args.background_service:
            assert provider_invokers() == original_invokers
            report["already_visible_no_duplicate_invoker"] = provider_invokers()
        report["observations"].append({"lyrics_visible": snapshot()})
        screenshot = repo / "results/kodi22_runtime" / (artifact + ".png")
        screenshot.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
        wait(screenshot.exists, True)
        # Same target used by the provider's own OSD handler.
        client.send_action("ActivateWindow(10120)")
        wait(lambda: boolean("Window.IsVisible(musicosd)"), True)
        client.send_action("Control.SetFocus(701)")
        wait(lambda: boolean("Control.HasFocus(701)"), True)
        rpc("Input.Down")
        wait(lambda: boolean("Control.IsVisible(2402)"), True)
        client.send_action("Control.SetFocus(2402)")
        wait(lambda: boolean("Control.HasFocus(2402)"), True)
        report["observations"].append({"before_native_stop": snapshot(), "lyrics_window_visible": boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)")})
        rpc("Input.Select")
        wait(lambda: label("Window(Home).Property(culrc.running)"), "")
        wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), False)
        report["observations"].append({"after_native_stop": snapshot()})
        client.send_action("Dialog.Close(musicosd)")
        wait(lambda: boolean("Window.IsVisible(musicosd)"), False)
        client.send_action("Skin.Reset(Lyrics)")
        wait(lambda: boolean("Skin.HasSetting(Lyrics)"), False)
        # PlayerControls is intentionally hidden over Visualisation.
        rpc("GUI.ActivateWindow", {"window": "home"})
        wait(lambda: boolean("Window.IsActive(home)"), True)
        client.send_action("ActivateWindow(playercontrols)")
        wait(lambda: boolean("Window.IsVisible(playercontrols)"), True)
        client.send_action("Control.SetFocus(609)")
        wait(lambda: boolean("Control.HasFocus(609)"), True)
        rpc("Input.Select")
        wait(lambda: boolean("Skin.HasSetting(Lyrics)"), True)
        client.send_action("ActivateWindow(visualisation)")
        wait(lambda: boolean("Window.IsVisible(visualisation)"), True)
        wait(lambda: boolean("Window.IsVisible(script-cu-lrclyrics-main.xml)"), True)
        wait(lambda: "HorizonzV audit line one" in label("Window(Home).Property(culrc.lyrics)"), True)
        report["observations"].append({"player_controls_restart": snapshot(), "lyrics_setting": boolean("Skin.HasSetting(Lyrics)")})
        report["provider_invokers_after_restart"] = provider_invokers()
    except Exception as exc:
        failure = repr(exc)
        report["failure"] = failure
        report["failure_trace"] = traceback.format_exc()
        if client:
            report["failure_state"] = snapshot()
            screenshot = repo / "results/kodi22_runtime" / (artifact + "_failure.png")
            screenshot.unlink(missing_ok=True)
            client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
            wait(screenshot.exists, True)
    finally:
        if client:
            client.send_action("PlayerControl(Stop)")
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
            if previous is None:
                assert provider_settings.resolve().parent == (root / "portable_data/userdata/addon_data/script.cu.lrclyrics").resolve()
                provider_settings.unlink(missing_ok=True)
            else:
                provider_settings.write_bytes(previous)
            cleanup["provider_settings_restored"] = (not provider_settings.exists()) if previous is None else provider_settings.read_bytes() == previous
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
            cleanup["all_test_xml_match_production"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        cleanup["all_copied_addon_files_unchanged"] = all(hashlib.sha256((addons / name / rel).read_bytes()).hexdigest() == digest for name, hashes in copied.items() for rel, digest in hashes.items())
        cleanup["all_standard_source_files_unchanged"] = all(hashlib.sha256((repo.parent / name / rel).read_bytes()).hexdigest() == digest for name, hashes in copied.items() for rel, digest in hashes.items())
        report["cleanup"] = cleanup
        lines = (root / "portable_data/kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [line for line in lines if " error " in line.lower() or "fatal" in line.lower()]
        (repo / "results/kodi22_runtime" / (artifact + "_checks.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "background": args.background_service, "observations": report["observations"], "errors": len(report["errors"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
