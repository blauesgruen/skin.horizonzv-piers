"""Visible Kodi ZIP installation and restart, isolated profile only."""
import argparse
import hashlib
import json
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-review", type=Path, default=repo / "results/kodi22_inventory/switchtimer_package_review.json")
    parser.add_argument("--report-prefix", default="package_install")
    args = parser.parse_args()
    assert args.report_prefix and all(c.isalnum() or c == "_" for c in args.report_prefix)
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440").resolve()
    profile = root / "portable_data"
    skin = profile / "addons/skin.horizonzv"
    review = json.loads(args.package_review.read_text(encoding="utf-8-sig"))
    archive = Path(review["archive"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == review["sha256"]
    with zipfile.ZipFile(archive) as z:
        expected = {n.split("/", 1)[1]: z.read(n) for n in z.namelist() if not n.endswith("/")}
    assert len(expected) == review["file_count"]
    expected_version = ET.fromstring(expected["addon.xml"]).get("version")
    assert expected_version
    assert all((repo / name).read_bytes() == data for name, data in expected.items())

    def no_kodi():
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.stdout.strip() == "0", "Another Kodi is running"

    no_kodi()
    work = Path(tempfile.mkdtemp(prefix="review-zip-install-", dir=root)).resolve()
    backups = {name: (profile / name).read_bytes() if (profile / name).exists() else None for name in ("userdata/guisettings.xml", "userdata/sources.xml", "userdata/addon_data/skin.horizonzv/settings.xml")}
    for i, data in enumerate(backups.values()):
        if data is not None:
            (work / f"profile-{i}.xml").write_bytes(data)
    database = profile / "userdata/Database"
    db_backup = {p.name: p.read_bytes() for p in database.iterdir() if p.is_file()}
    saved_db = work / "database"
    saved_db.mkdir()
    for name, data in db_backup.items():
        (saved_db / name).write_bytes(data)

    def move_owned(source, target):
        source, target = source.resolve(), target.resolve()
        assert root in source.parents and root in target.parents
        assert source != root and target != root and source.exists() and not target.exists()
        # Directory moves remain entirely within this explicitly named owned test root.
        paths = [source, *source.rglob("*")] if source.is_dir() else [source]
        assert all(not (p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT) for p in paths)
        source.rename(target)

    original_skin = work / "original-skin"
    original_hashes = {p.relative_to(skin).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in skin.rglob("*") if p.is_file()}
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc as raw_rpc
    from xbmcclient import XBMCClient
    process = client = None
    failure = None
    report = {"scope": "Native InstallFromZip with no pre-existing skin directory, followed by a separate restart into the packaged skin. Retained test skin settings, not an empty first-run user profile.", "archive": str(archive), "archive_sha256": review["sha256"], "pids": [], "stages": []}

    def rpc(method, params=None):
        r = raw_rpc(method, params)
        assert "result" in r, r
        return r["result"]

    def label(expr):
        return rpc("XBMC.GetInfoLabels", {"labels": [expr]})[expr]

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def wait(probe, expected_value, seconds=20):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            actual = probe()
            if actual == expected_value:
                return actual
            assert process is not None and process.poll() is None, "Owned Kodi exited"
            time.sleep(.15)
        raise AssertionError({"expected": expected_value, "actual": actual})

    def settings(skin_id):
        tree = ET.parse(profile / "userdata/guisettings.xml")
        for name, value in {"lookandfeel.skin": skin_id, "addons.unknownsources": "true", "addons.updatemode": "2", "window.width": "1280", "window.height": "720", "input.enablemouse": "false", "debug.showloginfo": "false"}.items():
            n = tree.find(f"setting[@id='{name}']")
            assert n is not None, name
            n.text = value
            n.attrib.pop("default", None)
        tree.write(profile / "userdata/guisettings.xml", encoding="utf-8", xml_declaration=True)

    def start():
        nonlocal process, client
        no_kodi()
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 1
        process = subprocess.Popen([str(root / "kodi.exe"), "-p", "-w"], cwd=root, startupinfo=startup)
        report["pids"].append(process.pid)
        for _ in range(80):
            try:
                rpc("JSONRPC.Ping")
                break
            except Exception:
                assert process.poll() is None
                time.sleep(.25)
        client = XBMCClient(name="HorizonzV ZIP installation", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.3)

    def stop(stage):
        nonlocal client
        report["stages"].append(stage)
        raw_rpc("Application.Quit")
        process.wait(timeout=25)
        client.close()
        client = None
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        stage["skin_load_log"] = [s for s in lines if "  load skin from:" in s]
        stage["install_log"] = [s for s in lines if ("CAddonInstall" in s or "Installing" in s or "installed" in s.lower()) and "skin.horizonzv" in s]
        stage["errors"] = [s for s in lines if " error " in s.lower() or "fatal" in s.lower()]

    def choose(target):
        # Read the actual focused browser entry before selecting, rather than relying on order.
        client.send_action("Control.SetFocus(450)")
        time.sleep(.2)
        seen = []
        for _ in range(100):
            name = label("Container(450).ListItem.Label")
            seen.append(name)
            if name == target:
                rpc("Input.Select")
                return seen
            rpc("Input.Down")
            time.sleep(.08)
        raise AssertionError({"target": target, "seen": seen})

    try:
        move_owned(skin, original_skin)
        settings("skin.estuary")
        sources = ET.Element("sources")
        files = ET.SubElement(sources, "files")
        source = ET.SubElement(files, "source")
        ET.SubElement(source, "name").text = "HorizonzV Testpaket"
        ET.SubElement(source, "path", {"pathversion": "1"}).text = archive.parent.as_posix() + "/"
        ET.SubElement(source, "allowsharing").text = "false"
        ET.ElementTree(sources).write(profile / "userdata/sources.xml", encoding="utf-8", xml_declaration=True)
        start()
        assert not skin.exists()
        before = raw_rpc("Addons.GetAddonDetails", {"addonid": "skin.horizonzv"})
        assert "error" in before, before
        stage = {"phase": "native_zip_install", "pid": process.pid, "skin_directory_absent_before_install": True, "addon_unavailable_before_install": True}
        client.send_action("InstallFromZip()")
        wait(lambda: boolean("Window.IsVisible(filebrowser)"), True)
        stage["source_selection"] = choose("HorizonzV Testpaket")
        time.sleep(.3)
        stage["file_selection"] = choose(archive.name)
        wait(lambda: (skin / "addon.xml").exists(), True, seconds=45)
        wait(lambda: boolean("System.HasAddon(skin.horizonzv)"), True, seconds=45)
        details = rpc("Addons.GetAddonDetails", {"addonid": "skin.horizonzv", "properties": ["version", "enabled"]})["addon"]
        assert details["version"] == expected_version, details
        stage["addon_details"] = details
        # CSkinInfo::OnPostInstall asks whether to use a newly installed skin.
        # Registration precedes this modal dialog: do not race it with Application.Quit.
        wait(lambda: boolean("Window.IsVisible(yesnodialog)"), True)
        stage["post_install_confirmation_observed"] = True
        rpc("Input.Back")
        wait(lambda: boolean("Window.IsVisible(yesnodialog)"), False)
        stage["post_install_confirmation_dismissed"] = True
        time.sleep(1)
        stop(stage)
        installed = {p.relative_to(skin).as_posix(): p.read_bytes() for p in skin.rglob("*") if p.is_file()}
        assert installed == expected, {"missing": sorted(set(expected) - set(installed)), "extra": sorted(set(installed) - set(expected))}
        report["fresh_install_files"] = len(installed)
        report["all_installed_files_equal_zip"] = True
        settings("skin.horizonzv")
        start()
        wait(lambda: boolean("Window.IsActive(home)"), True)
        time.sleep(1)
        stage = {"phase": "restart_packaged_skin", "pid": process.pid, "home_active": True, "aspect": label("Skin.AspectRatio")}
        image_name = "package_installed_home.png" if args.report_prefix == "package_install" else args.report_prefix + "_home.png"
        screenshot = repo / "results/kodi22_runtime" / image_name
        screenshot.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
        wait(screenshot.exists, True)
        stop(stage)
        assert any("\\skin.horizonzv\\" in s for s in stage["skin_load_log"]), stage
        assert not any(s["errors"] for s in report["stages"]), report["stages"]
        report["packaged_files_after_restart_equal_zip"] = all((skin / name).read_bytes() == data for name, data in expected.items())
        assert report["packaged_files_after_restart_equal_zip"]
    except Exception as exc:
        failure = repr(exc)
        report.update({"failure": failure, "trace": traceback.format_exc()})
    finally:
        if process and process.poll() is None:
            try:
                raw_rpc("Application.Quit")
                process.wait(timeout=25)
            except Exception:
                pass
        if client:
            client.close()
        cleanup = {"owned_process_exited": process is None or process.poll() is not None}
        if cleanup["owned_process_exited"]:
            if original_skin.exists():
                if skin.exists():
                    move_owned(skin, work / "installed-skin-result")
                move_owned(original_skin, skin)
            for name, data in backups.items():
                dest = profile / name
                if data is None:
                    if dest.exists():
                        move_owned(dest, work / (dest.name + ".generated"))
                else:
                    dest.write_bytes(data)
            extra_db = work / "new-database-files"
            extra_db.mkdir(exist_ok=True)
            for p in database.iterdir():
                if p.is_file() and p.name not in db_backup:
                    move_owned(p, extra_db / p.name)
            for name, data in db_backup.items():
                (database / name).write_bytes(data)
            restored = {p.relative_to(skin).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in skin.rglob("*") if p.is_file()}
            cleanup["original_skin_restored"] = restored == original_hashes
            cleanup["profile_settings_and_sources_restored"] = all((profile / name).read_bytes() == data if data is not None else not (profile / name).exists() for name, data in backups.items())
            cleanup["all_database_files_restored"] = {p.name: p.read_bytes() for p in database.iterdir() if p.is_file()} == db_backup
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime" / (args.report_prefix + "_checks.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "stages": report["stages"], "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
