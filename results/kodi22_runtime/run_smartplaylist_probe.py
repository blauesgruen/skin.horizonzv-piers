"""Visible native smartplaylist checks using restored isolated media databases."""
import hashlib
import json
import secrets
import shutil
import sqlite3
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
    work = Path(tempfile.mkdtemp(prefix="review-smartplaylists-", dir=root))
    database = root / "portable_data/userdata/Database"
    backup = work / "database"
    backup.mkdir()
    db_files = [p for pattern in ("MyVideos*.db*", "MyMusic*.db*") for p in database.glob(pattern)]
    for p in db_files:
        shutil.copy2(p, backup / p.name)
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    target = root / "portable_data/addons/skin.horizonzv/playlists"
    for p in (repo / "playlists").glob("*.xsp"):
        shutil.copy2(p, target / p.name)
    baseline = work / "baseline"
    baseline.mkdir()
    baseline_native = {}
    for name in ("Videos_recently.xsp", "TVShows_recent_tvshows.xsp"):
        old = subprocess.run(["git", "-c", "safe.directory=" + repo.as_posix(), "show", "772c767a901b7127fb1f66a4e420c2e1d8beb457:playlists/" + name], capture_output=True)
        assert old.returncode == 0
        (baseline / name).write_bytes(old.stdout)
        baseline_native[name] = root / "portable_data/userdata/playlists/video" / (work.name + "-" + name)
    media = work / "media"
    media.mkdir()
    video = root / "portable_data/testmedia/skin-audit-video.avi"
    for index in (1, 2):
        showpath = media / ("show" + str(index))
        showpath.mkdir()
        filename = showpath / "s01e01.avi"
        shutil.copy2(video, filename)
    music = work / "music"
    music.mkdir()
    sys.path.insert(0, str(root / "portable_data/addons/script.module.mutagen/lib"))
    from mutagen.wave import WAVE
    from mutagen.id3 import TIT2, TPE1, TALB, TPE2
    for index in (1, 2):
        filename = music / (str(index) + ".wav")
        shutil.copy2(root / "portable_data/testmedia/skin-audit-silence.wav", filename)
        tags = WAVE(filename)
        if tags.tags is None:
            tags.add_tags()
        tags.tags.add(TIT2(encoding=3, text="SP Audit Song " + str(index)))
        tags.tags.add(TALB(encoding=3, text="SP Audit Album " + str(index)))
        tags.tags.add(TPE1(encoding=3, text="SP Audit Artist"))
        tags.tags.add(TPE2(encoding=3, text="SP Audit Artist"))
        tags.save()
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient

    def rpc(method, params=None):
        result = raw_rpc(method, params)
        assert "result" in result, result
        return result["result"]

    def wait(probe, expected, attempts=200):
        for _ in range(attempts):
            value = probe()
            if value == expected:
                return value
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": value})

    def query(path, media_type):
        result = rpc("Files.GetDirectory", {"directory": str(path), "media": media_type, "properties": ["title", "playcount", "dateadded", "userrating", "album", "artist"]})
        return [{k: item[k] for k in ("label", "type", "id", "file", "playcount", "dateadded") if k in item} for item in result.get("files", [])]

    def compare(name, media_type, expected):
        old = query("special://profile/playlists/video/" + baseline_native[name].name, media_type)
        new = query("special://skin/playlists/" + name, media_type)
        a, b = [x["label"] for x in old], [x["label"] for x in new]
        row = {"file": name, "baseline_labels": a, "revised_labels": b, "expected_labels": expected, "matches": a == b == expected}
        report["comparisons"].append(row)
        assert row["matches"], row

    report = {"scope": "All shipped smartplaylist directory calls; native before/after comparison of two invalid nested node rules using authored media in isolated databases", "video_fixture_method": "Two shows/episodes seeded offline into backed-up isolated MyVideos149 only; existing authored movie title/state changed through RPC; original DB files restored on exit", "comparisons": [], "all_playlists": []}
    process = client = None
    failure = None
    try:
        # Files.GetDirectory intentionally permits the native playlist location.
        # Do not weaken remote-file access settings for temporary test files.
        for name, path in baseline_native.items():
            assert not path.exists()
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(baseline / name, path)
        db_path = database / "MyVideos149.db"
        assert db_path.resolve().parent == database.resolve() and root.name.startswith("horizonzv-kodi-test-")
        connection = sqlite3.connect(db_path)
        try:
            assert connection.execute("select count(*) from tvshow").fetchone()[0] == 0
            for index in (1, 2):
                folder = media / ("show" + str(index))
                pid = connection.execute("insert into path(strPath,strContent) values (?,?)", (str(folder) + "\\", "tvshows")).lastrowid
                # tvshowcounts uses COUNT(files.playCount): unwatched is NULL.
                fid = connection.execute("insert into files(idPath,strFilename,playCount,dateAdded) values (?,?,?,?)", (pid, "s01e01.avi", None if index == 1 else 1, f"2026-11-0{index} 12:00:00")).lastrowid
                sid = connection.execute("insert into tvshow(c00,c05,userrating) values (?,?,?)", ("SP Audit Show " + str(index), "2026-01-01", 0)).lastrowid
                connection.execute("insert into tvshowlinkpath(idShow,idPath) values (?,?)", (sid, pid))
                season = connection.execute("insert into seasons(idShow,season) values (?,?)", (sid, 1)).lastrowid
                connection.execute("insert into episode(idFile,c00,c11,c12,c13,c18,idShow,idSeason,userrating) values (?,?,?,?,?,?,?,?,?)", (fid, "SP Audit Episode " + str(index), "90", "1", "1", str(folder / "s01e01.avi"), sid, season, 0))
            connection.commit()
        finally:
            connection.close()
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
        client = XBMCClient(name="HorizonzV smartplaylist audit", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        wait(lambda: len(rpc("VideoLibrary.GetTVShows").get("tvshows", [])), 2)
        rpc("AudioLibrary.Scan", {"directory": str(music), "showdialogs": False})
        wait(lambda: len(rpc("AudioLibrary.GetSongs").get("songs", [])), 2, 400)
        movies = rpc("VideoLibrary.GetMovies")["movies"]
        assert len(movies) == 1, movies
        movie_ids = {"SP Audit Movie 1": movies[0]["movieid"]}
        rpc("VideoLibrary.SetMovieDetails", {"movieid": movies[0]["movieid"], "title": "SP Audit Movie 1", "playcount": 0})
        episodes = rpc("VideoLibrary.GetEpisodes", {"properties": ["title", "playcount"]})["episodes"]
        episode_ids = {x["title"]: x["episodeid"] for x in episodes}
        for item in episodes:
            rpc("VideoLibrary.SetEpisodeDetails", {"episodeid": item["episodeid"], "playcount": int(item["title"] != "SP Audit Episode 1")})
        songs = rpc("AudioLibrary.GetSongs")["songs"]
        for item in songs:
            if item["label"] == "SP Audit Song 1":
                rpc("AudioLibrary.SetSongDetails", {"songid": item["songid"], "playcount": 1, "lastplayed": "2026-11-03 12:00:00"})
        for item in rpc("AudioLibrary.GetAlbums")["albums"]:
            rpc("AudioLibrary.SetAlbumDetails", {"albumid": item["albumid"], "userrating": 9})
        compare("Videos_recently.xsp", "video", ["SP Audit Movie 1"])
        compare("TVShows_recent_tvshows.xsp", "video", ["SP Audit Show 1"])
        for path in sorted((repo / "playlists").glob("*.xsp")):
            kind = "music" if ET.parse(path).getroot().get("type") in ("songs", "albums", "artists") else "video"
            items = query("special://skin/playlists/" + path.name, kind)
            report["all_playlists"].append({"file": path.name, "items": items})
        rpc("VideoLibrary.SetMovieDetails", {"movieid": movie_ids["SP Audit Movie 1"], "playcount": 1})
        rpc("VideoLibrary.SetEpisodeDetails", {"episodeid": episode_ids["SP Audit Episode 1"], "playcount": 1})
        report["watched_episode_state"] = rpc("VideoLibrary.GetEpisodes", {"properties": ["title", "playcount"]})
        compare("Videos_recently.xsp", "video", [])
        compare("TVShows_recent_tvshows.xsp", "video", [])
        rpc("VideoLibrary.SetMovieDetails", {"movieid": movie_ids["SP Audit Movie 1"], "playcount": 0})
        rpc("VideoLibrary.SetEpisodeDetails", {"episodeid": episode_ids["SP Audit Episode 2"], "playcount": 0})
        compare("Videos_recently.xsp", "video", ["SP Audit Movie 1"])
        compare("TVShows_recent_tvshows.xsp", "video", ["SP Audit Show 2"])
        rpc("GUI.ActivateWindow", {"window": "videos", "parameters": ["special://skin/playlists/Videos_recently.xsp", "return"]})
        time.sleep(.6)
        client.send_action("Container.SetViewMode(50)")
        client.send_action("Control.SetFocus(50)")
        screenshot = repo / "results/kodi22_runtime/smartplaylist_recent_movie.png"
        screenshot.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
        wait(screenshot.exists, True)
    except Exception as exc:
        failure = repr(exc)
        report["failure"] = failure
        report["failure_trace"] = traceback.format_exc()
    finally:
        if client:
            client.close()
        if process:
            try:
                raw_rpc("Application.Quit")
                process.wait(timeout=20)
            except Exception:
                pass
        exited = process is None or process.poll() is not None
        cleanup = {"process_exited": exited}
        if exited:
            for path in baseline_native.values():
                assert path.resolve().parent == (root / "portable_data/userdata/playlists/video").resolve()
                path.unlink(missing_ok=True)
            cleanup["baseline_test_playlists_removed"] = all(not path.exists() for path in baseline_native.values())
            for pattern in ("MyVideos*.db*", "MyMusic*.db*"):
                for path in database.glob(pattern):
                    assert path.resolve().parent == database.resolve()
                    path.unlink()
            for path in backup.iterdir():
                shutil.copy2(path, database / path.name)
            restored_names = sorted(p.name for pattern in ("MyVideos*.db*", "MyMusic*.db*") for p in database.glob(pattern))
            cleanup["media_databases_restored"] = sorted(p.name for p in backup.iterdir()) == restored_names and all(path.read_bytes() == (database / path.name).read_bytes() for path in backup.iterdir())
            for rel in rels:
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
            cleanup["test_playlists_match_production"] = all(path.read_bytes() == (target / path.name).read_bytes() for path in (repo / "playlists").glob("*.xsp"))
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/smartplaylist_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "comparisons": report["comparisons"], "playlist_count": len(report["all_playlists"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
