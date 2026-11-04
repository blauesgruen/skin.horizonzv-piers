"""Real Artist Slideshow local metadata -> production artist-info controls."""
import hashlib
import json
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
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-artist-local-info-", dir=root))
    profile = root / "portable_data"
    addons = profile / "addons"
    copies = {}

    def provider_copy(name):
        if name.startswith("xbmc.") or name in copies:
            return
        source, dest = repo.parent / name, addons / name
        files = {p.relative_to(source).as_posix(): p for p in source.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git", ".codex", "__pycache__"))}
        assert "addon.xml" in files, name
        copies[name] = {}
        for rel, p in files.items():
            data = p.read_bytes()
            target = dest / rel
            if target.exists():
                assert target.read_bytes() == data, str(target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            copies[name][rel] = hashlib.sha256(data).hexdigest()
        for dep in ET.parse(source / "addon.xml").findall("requires/import"):
            if dep.get("optional") != "true":
                provider_copy(dep.get("addon"))

    provider_copy("script.artistslideshow")
    provider_copy("script.module.mutagen")
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml", "userdata/addon_data/script.artistslideshow/settings.xml", "userdata/addon_data/script.cu.lrclyrics/settings.xml")
    backups = {rel: (profile / rel).read_bytes() if (profile / rel).exists() else None for rel in rels}
    for i, data in enumerate(backups.values()):
        if data is not None:
            (work / f"profile-{i}.xml").write_bytes(data)
    lyrics_config = profile / rels[3]
    lyrics_tree = ET.fromstring(backups[rels[3]]) if backups[rels[3]] is not None else ET.Element("settings", {"version": "2"})
    service = lyrics_tree.find("setting[@id='service']")
    if service is None:
        service = ET.SubElement(lyrics_tree, "setting", {"id": "service"})
    service.text = "false"
    service.attrib.pop("default", None)
    lyrics_config.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(lyrics_tree).write(lyrics_config, encoding="utf-8", xml_declaration=True)
    database = profile / "userdata/Database"
    music_backup = {p.name: p.read_bytes() for p in database.glob("MyMusic*.db*")}
    saved = work / "database"
    saved.mkdir()
    for name, data in music_backup.items():
        (saved / name).write_bytes(data)
    skin_xml = addons / "skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, skin_xml / p.name)
    info_file = skin_xml / "Custom_1100_Artistslideshow_Artistinfo.xml"
    xml = ET.parse(info_file)
    parents = {child: parent for parent in xml.iter() for child in parent}
    # Existing controls receive observation IDs only; read-only probes are added below.
    for cid, marker, probe_id in [(1100, "ArtistSlideshow.1.AlbumName", 1188), (1110, "ArtistSlideshow.1.SimilarName", 1189)]:
        node = xml.find(f".//control[@id='{cid}']")
        while node is not None:
            node = parents.get(node)
            if node is not None and any(marker in (n.text or "") for n in node.findall("visible")):
                node.set("id", str(probe_id))
                break
        assert node is not None
    bio = next(n for n in xml.iter("control") if n.get("type") == "textbox" and n.findtext("description") == "Artist Biography from Artist Slideshow")
    bio.set("id", "1187")
    parent = parents[bio]
    assert any("ArtistSlideshow.ArtistBiography" in (n.text or "") for n in parent.findall("visible"))
    parent.set("id", "1190")
    row = next(n for n in xml.iter("control") if any("ArtistSlideshow.1.AlbumName" in (v.text or "") and "ArtistSlideshow.1.SimilarName" in (v.text or "") for v in n.findall("visible")))
    row.set("id", "1193")
    xml.find("controls/control[@type='grouplist']").set("id", "1186")
    group_probe = ET.SubElement(xml.getroot().find("controls"), "control", {"type": "group", "id": "1194"})
    for tag, value in {"left": "-3000", "top": "0", "width": "1", "height": "1", "visible": "Control.IsVisible(1186)"}.items():
        ET.SubElement(group_probe, tag).text = value
    # Python ControlList.size() reads only its own vecItems. Observe static
    # containers through GUI info labels evaluated in their parent window.
    probes = {1191: "$INFO[Container(1100).NumItems]", 1192: "$INFO[Container(1110).NumItems]"}
    for i in range(2):
        probes[1200 + i] = f"$INFO[Container(1100).ListItemAbsolute({i}).Label]"
    for i in range(5):
        probes[1210 + i] = f"$INFO[Container(1110).ListItemAbsolute({i}).Label]"
    probes[1220] = "$INFO[Container(1100).ListItemAbsolute(0).Icon]"
    probes[1221] = "$INFO[Container(1110).ListItemAbsolute(0).Icon]"
    for cid, expression in probes.items():
        node = ET.SubElement(xml.getroot().find("controls"), "control", {"type": "textbox", "id": str(cid)})
        for tag, value in {"left": "-3000", "top": "0", "width": "1800", "height": "50", "font": "font13", "label": expression}.items():
            ET.SubElement(node, tag).text = value
    xml.write(info_file, encoding="utf-8", xml_declaration=True)
    artist_root, info_root = work / "artists", work / "information"
    config = ET.Element("settings", {"version": "2"})
    defaults = {n.get("id"): n.findtext("default") or "" for n in ET.parse(addons / "script.artistslideshow/resources/settings.xml").iter("setting") if n.find("default") is not None}
    defaults.update(artist_image_storage="2", local_artist_path=str(artist_root), artist_info_storage="1", local_info_path=str(info_root), use_extrafanart_folder="true", fanart_folder="extrafanart", slideshow="false", fadetoblack="false", include_artistfanart="false", include_albumfanart="false", use_audio_stream_monitor="false", main_sleep="1", storage_target="0")
    for name in list(defaults):
        if any(name == prefix + plugin for prefix in ("", "ab_", "ai_", "sa_") for plugin in ("kodi", "fanarttv", "theaudiodb", "lastfm")):
            defaults[name] = "false"
    for name, value in defaults.items():
        ET.SubElement(config, "setting", {"id": name}).text = value
    dest = profile / rels[2]
    dest.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(config).write(dest, encoding="utf-8", xml_declaration=True)
    sys.path.insert(0, str(addons / "script.module.mutagen/lib"))
    from mutagen.wave import WAVE
    from mutagen.id3 import TIT2, TPE1, TALB
    cases = []
    picture = work / "fixture.jpg"
    shutil.copy2(repo / "backgrounds/gambit/background.jpg", picture)
    for suffix, albums_count, similar_count in [("A", 2, 1), ("B", 1, 5), ("Empty", 0, 0)]:
        artist = "HorizonzV Local Artist " + suffix
        audio = work / ("artist-" + suffix + ".wav")
        with wave.open(str(root / "portable_data/testmedia/skin-audit-silence.wav"), "rb") as source:
            params, data = source.getparams(), source.readframes(source.getnframes())
        with wave.open(str(audio), "wb") as out:
            out.setparams(params)
            out.writeframes(data * 3)
        tags = WAVE(audio)
        tags.add_tags()
        tags.tags.add(TIT2(encoding=3, text="Local Artist Test " + suffix))
        tags.tags.add(TPE1(encoding=3, text=artist))
        tags.tags.add(TALB(encoding=3, text="Authored Skin Fixture"))
        tags.save()
        folder = artist_root / artist
        (folder / "extrafanart").mkdir(parents=True)
        shutil.copy2(picture, folder / "extrafanart/fixture.jpg")
        cache = info_root / artist / "information"
        cache.mkdir(parents=True)
        (cache / "musicbrainz.nfo").write_text("00000000-0000-4000-8000-000000000001\n", encoding="utf-8")
        bio_text = "" if suffix == "Empty" else "Authored local biography for skin fixture " + suffix + "."
        albums = [f"Fixture {suffix} Album {i}" for i in range(1, albums_count + 1)]
        similar = [f"Fixture {suffix} Similar {i}" for i in range(1, similar_count + 1)]
        if suffix != "Empty":
            override = folder / "override"
            override.mkdir()
            node = ET.Element("artist")
            ET.SubElement(node, "content").text = bio_text
            ET.ElementTree(node).write(override / "artistbio.nfo", encoding="utf-8")
            for file, items in [("artistsalbums.nfo", albums), ("artistsimilar.nfo", similar)]:
                node = ET.Element("items")
                for label in items:
                    item = ET.SubElement(node, "item")
                    ET.SubElement(item, "name").text = label
                    # The existing provider accepts absolute local image paths.
                    ET.SubElement(item, "image").text = str(picture)
                ET.ElementTree(node).write(override / file, encoding="utf-8")
        cases.append({"case": suffix, "artist": artist, "audio": str(audio), "bio": bio_text, "albums": albums, "similar": similar})
    observer = work / "observe.py"
    observer.write_text('''import json,sys,traceback,xbmcgui,xbmc
from pathlib import Path
try:
 w=xbmcgui.Window(11000)
 r={'bio':w.getControl(1187).getText(),'groups':{str(i):w.getControl(i).isVisible() for i in (1188,1189,1190,1193)},'window_visible':xbmc.getCondVisibility('Window.IsVisible(11000)')}
 r['groups']['1186']=w.getControl(1194).isVisible()
 base=r['window_visible'] and r['groups']['1186']
 r['effective_sections']={'albums':base and r['groups']['1193'] and r['groups']['1188'],'similar':base and r['groups']['1193'] and r['groups']['1189'],'bio':base and r['groups']['1190']}
 r['counts']={'albums':w.getControl(1191).getText(),'similar':w.getControl(1192).getText()}
 for kind,start,count in [('albums',1200,2),('similar',1210,5)]:
  r[kind]=[w.getControl(start+i).getText() for i in range(count)]
 r['first_icons']={'albums':w.getControl(1220).getText(),'similar':w.getControl(1221).getText()}
except Exception:
 r={'error':traceback.format_exc()}
Path(sys.argv[1]).write_text(json.dumps(r),encoding='utf-8')
''', encoding="utf-8")
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        data = raw_rpc(method, params)
        assert "result" in data, data
        return data["result"]

    def label(expr):
        return rpc("XBMC.GetInfoLabels", {"labels": [expr]})[expr]

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def wait(probe, expected, attempts=250):
        for _ in range(attempts):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})

    observation_id = 0

    def observe():
        nonlocal observation_id
        observation_id += 1
        file = work / f"observation-{observation_id}.json"
        client.send_action('RunScript("' + observer.as_posix() + '","' + file.as_posix() + '")')
        wait(file.exists, True, attempts=100)
        data = json.loads(file.read_text())
        assert "error" not in data, data
        return data

    report = {"scope": "Unchanged Artist Slideshow 4.2.1 consumes authored local NFO/WAV/image fixtures and drives the real skin artist-info window. Fanart skin option set off and three artist-info options set on before playback. No online metadata test.", "cases": [], "verified_files": {k: len(v) for k, v in copies.items()}, "observation_hooks": "Temporary IDs on existing info groups/biography textbox and offscreen read-only GUI-info/visibility probes in the real window; production conditions and data sources unchanged."}
    process = client = None
    failure = None
    try:
        gui = ET.parse(profile / rels[0])
        for name, value in {"window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            node = gui.find(f"setting[@id='{name}']")
            assert node is not None
            node.text = value
            node.attrib.pop("default", None)
        gui.write(profile / rels[0], encoding="utf-8", xml_declaration=True)
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
        for addon in copies:
            rpc("Addons.SetAddonEnabled", {"addonid": addon, "enabled": True})
        client = XBMCClient(name="HorizonzV local artist data", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action("Skin.Reset(fanart)")
        wait(lambda: boolean("Skin.HasSetting(fanart)"), False)
        for name in ("bio", "albums", "similar"):
            client.send_action("Skin.SetBool(artistslideshow_artistinfos_" + name + ")")
            wait(lambda: boolean("Skin.HasSetting(artistslideshow_artistinfos_" + name + ")"), True)
        for case in cases:
            client.send_action('PlayMedia("' + Path(case["audio"]).as_posix() + '")')
            wait(lambda: boolean("Player.HasAudio"), True)
            wait(lambda: label("MusicPlayer.Artist"), case["artist"])
            client.send_action("ActivateWindow(visualisation)")
            wait(lambda: boolean("Window.IsVisible(visualisation)"), True)
            if boolean("Player.ShowInfo"):
                rpc("Input.ExecuteAction", {"action": "info"})
                wait(lambda: boolean("Player.ShowInfo"), False)
            wait(lambda: label("Window(visualisation).Property(ArtistSlideshowRunning)"), "True")
            wait(lambda: label("Window(visualisation).Property(ArtistSlideshow.ArtistBiography)"), case["bio"])
            wait(lambda: label("Window(visualisation).Property(ArtistSlideshow.1.AlbumName)"), case["albums"][0] if case["albums"] else "")
            wait(lambda: label("Window(visualisation).Property(ArtistSlideshow.1.SimilarName)"), case["similar"][0] if case["similar"] else "")
            wait(lambda: boolean("Window.IsVisible(11000)"), True)
            actual = None
            for _ in range(40):
                actual = observe()
                if case["case"] == "Empty":
                    if actual["window_visible"] and actual["groups"]["1186"] and not any(actual["effective_sections"].values()):
                        break
                elif all(actual["effective_sections"].values()) and actual["albums"][:len(case["albums"])] == case["albums"] and actual["similar"][:len(case["similar"])] == case["similar"] and actual["bio"] == case["bio"] and actual["counts"] == {"albums": str(len(case["albums"])), "similar": str(len(case["similar"]))}:
                    break
                if boolean("Player.ShowInfo"):
                    rpc("Input.ExecuteAction", {"action": "info"})
                time.sleep(.2)
            assert actual is not None
            if case["case"] == "Empty":
                assert actual["window_visible"] and actual["groups"]["1186"], actual
                assert not any(actual["effective_sections"].values()), actual
            else:
                assert all(actual["effective_sections"].values()), actual
                assert actual["bio"] == case["bio"], actual
                assert actual["albums"][:len(case["albums"])] == case["albums"], actual
                assert actual["similar"][:len(case["similar"])] == case["similar"], actual
                assert actual["counts"] == {"albums": str(len(case["albums"])), "similar": str(len(case["similar"]))}, actual
            values = rpc("XBMC.GetInfoLabels", {"labels": ["Window(visualisation).Property(ArtistSlideshow.1.AlbumThumb)", "Window(visualisation).Property(ArtistSlideshow.1.SimilarThumb)", "Window(visualisation).Property(ArtistSlideshow.2.AlbumName)", "Skin.AspectRatio"]})
            if case["case"] != "Empty":
                for prop in ["Window(visualisation).Property(ArtistSlideshow.1.AlbumThumb)", "Window(visualisation).Property(ArtistSlideshow.1.SimilarThumb)"]:
                    assert Path(values[prop]).resolve() == picture.resolve(), values
            if case["case"] == "B":
                assert values["Window(visualisation).Property(ArtistSlideshow.2.AlbumName)"] == "", values
            report["cases"].append({"expected": case, "native_controls": actual, "properties": values})
            screenshot = repo / "results/kodi22_runtime" / ("artist_local_info_" + case["case"].lower() + ".png")
            screenshot.unlink(missing_ok=True)
            time.sleep(.5)
            client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
            wait(screenshot.exists, True)
        rpc("Player.Stop", {"playerid": 0})
        wait(lambda: boolean("Player.HasAudio"), False)
        wait(lambda: label("Window(visualisation).Property(ArtistSlideshowRunning)"), "")
        report["after_stop"] = {"running": label("Window(visualisation).Property(ArtistSlideshowRunning)"), "bio": label("Window(visualisation).Property(ArtistSlideshow.ArtistBiography)")}
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                if boolean("Player.HasAudio"):
                    rpc("Player.Stop", {"playerid": 0})
                raw_rpc("Application.Quit")
                process.wait(timeout=25)
            except Exception:
                pass
        if client:
            client.close()
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():
                target = profile / rel
                if data is not None:
                    target.write_bytes(data)
                else:
                    target.unlink(missing_ok=True)
            shutil.copy2(repo / "xml/Custom_1100_Artistslideshow_Artistinfo.xml", info_file)
            extra = work / "new-music-database-files"
            extra.mkdir(exist_ok=True)
            for p in database.glob("MyMusic*.db*"):
                if p.name not in music_backup:
                    assert root.resolve() in p.resolve().parents and root.resolve() in extra.resolve().parents
                    p.rename(extra / p.name)
            for name, data in music_backup.items():
                (database / name).write_bytes(data)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data if data is not None else not (profile / rel).exists() for rel, data in backups.items())
            cleanup["music_databases_restored"] = {p.name: p.read_bytes() for p in database.glob("MyMusic*.db*")} == music_backup
            cleanup["skin_xml_restored"] = {p.name: p.read_bytes() for p in skin_xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        cleanup["standard_provider_sources_unchanged"] = all(hashlib.sha256((repo.parent / name / rel).read_bytes()).hexdigest() == digest for name, files in copies.items() for rel, digest in files.items())
        cleanup["test_provider_copies_unchanged"] = all(hashlib.sha256((addons / name / rel).read_bytes()).hexdigest() == digest for name, files in copies.items() for rel, digest in files.items())
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [x for x in lines if " error " in x.lower() or "fatal" in x.lower()]
        (repo / "results/kodi22_runtime/artist_local_info_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "cases": report["cases"], "errors": len(report["errors"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
