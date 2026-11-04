"""Visible visits to the two corrected windows with controlled legacy properties."""
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
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-switchtimer-remaining-", dir=root))
    profile = root / "portable_data"
    backups = {rel: (profile / rel).read_bytes() for rel in ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")}
    for i, data in enumerate(backups.values()):
        (work / f"profile-{i}.xml").write_bytes(data)
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

    def boolean(expr):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def labels(exprs):
        return rpc("XBMC.GetInfoLabels", {"labels": exprs})

    def wait(probe, expected):
        for _ in range(120):
            actual = probe()
            if actual == expected:
                return actual
            time.sleep(.1)
        raise AssertionError({"expected": expected, "actual": actual})

    process = client = None
    failure = None
    report = {"scope": "Actual shutdown menu and skin settings opened with controlled old t0 properties present. No button selected, no timer scheduled, no provider run. Not an animation-coordinate or backend test.", "windows": []}
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
        client = XBMCClient(name="HorizonzV legacy timer properties", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        seeded = {"t0:date": "2099-01-01 12:00", "t0:channel": "Skin audit channel", "t0:title": "Skin audit timer"}
        for name, value in seeded.items():
            client.send_action(f"SetProperty({name},{value},home)")
            wait(lambda: labels([f"Window(Home).Property({name})"])[f"Window(Home).Property({name})"], value)
        client.send_action("Skin.SetBool(NavInfo)")
        wait(lambda: boolean("Skin.HasSetting(NavInfo)"), True)
        report["legacy_values"] = seeded
        for window in ("shutdownmenu", "skinsettings"):
            rpc("GUI.ActivateWindow", {"window": window})
            wait(lambda: boolean(f"Window.IsVisible({window})"), True)
            time.sleep(.6)
            snapshot = rpc("GUI.GetProperties", {"properties": ["currentwindow", "currentcontrol"]})
            expressions = ["Skin.AspectRatio", *[f"Window(Home).Property({key})" for key in seeded]]
            values = labels(expressions)
            assert all(values[f"Window(Home).Property({key})"] == value for key, value in seeded.items())
            screenshot = repo / "results/kodi22_runtime" / f"switchtimer_remaining_{window}.png"
            screenshot.unlink(missing_ok=True)
            client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
            wait(screenshot.exists, True)
            report["windows"].append({"target": window, "visible": True, "gui": snapshot, "values": values})
            if window == "shutdownmenu":
                client.send_action("Dialog.Close(shutdownmenu)")
                wait(lambda: boolean("Window.IsVisible(shutdownmenu)"), False)
        rpc("Input.Back")
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
        cleanup = {"process_exited": process is None or process.poll() is not None}
        if cleanup["process_exited"]:
            for rel, data in backups.items():
                (profile / rel).write_bytes(data)
            cleanup["profile_settings_restored"] = all((profile / rel).read_bytes() == data for rel, data in backups.items())
            cleanup["all_skin_xml_match"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        lines = (profile / "kodi.log").read_text(encoding="utf-8", errors="replace").splitlines()
        report["errors"] = [s for s in lines if " error " in s.lower() or "fatal" in s.lower()]
        (repo / "results/kodi22_runtime/switchtimer_remaining_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"failure": failure, "windows": report["windows"], "errors": len(report["errors"]), "cleanup": cleanup}, ensure_ascii=True))
    return int(bool(failure) or bool(report["errors"]) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
