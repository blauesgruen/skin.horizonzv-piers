"""Visible, isolated native checks for idle-inhibit menu and addon origin.

The temporary idle timeout is 120 minutes and is restored before exit.
Only the two identified inhibit/allow menu items may be selected.
"""
import json
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"],
                           capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Kodi already running"
    work = Path(tempfile.mkdtemp(prefix="review-idle-origin-", dir=root))
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    xml = root / "portable_data/addons/skin.horizonzv/xml"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, xml / p.name)
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root.parent / "horizonzv-standard-integration-20261103"))
    from skin_rpc import rpc
    from xbmcclient import XBMCClient

    def wait(probe, expected, attempts=80):
        for _ in range(attempts):
            value = probe()
            if value == expected:
                return value
            time.sleep(.1)
        raise AssertionError({"actual": value, "expected": expected})

    def labels(names):
        return rpc("XBMC.GetInfoLabels", {"labels": names})["result"]

    def label(name):
        return labels([name])[name]

    def boolean(name):
        return rpc("XBMC.GetInfoBooleans", {"booleans": [name]})["result"][name]

    def window():
        return rpc("GUI.GetProperties", {"properties": ["currentwindow"]})["result"]["currentwindow"]["id"]

    def menu_labels():
        n = int(label("Container(9000).NumItems"))
        keys = [f"Container(9000).ListItemAbsolute({i}).Label" for i in range(n)]
        values = labels(keys)
        return [values[k] for k in keys]

    def capture(name):
        path = repo / "results/kodi22_runtime" / (name + ".png")
        client.send_action('TakeScreenshot("' + path.as_posix() + '")')
        wait(path.exists, True)

    report = {"scope": "Native idle-inhibit menu actions and official repository addon origin", "rows": []}
    process = None
    client = None
    baseline_timeout = baseline_inhibit = None
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
        client = XBMCClient(name="HorizonzV native contract checks", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        baseline_timeout = rpc("Settings.GetSettingValue", {"setting": "powermanagement.shutdowntime"})["result"]["value"]
        baseline_inhibit = boolean("System.IdleShutdownInhibited")
        # Setting 120 allows the real System.HasShutdown gate, with two hours to expiry.
        rpc("Settings.SetSettingValue", {"setting": "powermanagement.shutdowntime", "value": 120})
        client.send_action("InhibitIdleShutdown(false)")
        wait(lambda: boolean("System.IdleShutdownInhibited"), False)
        for blocked, target, next_state in [(False, "Inhibit idle shutdown", True), (True, "Allow idle shutdown", False)]:
            rpc("GUI.ActivateWindow", {"window": "shutdownmenu"})
            wait(window, 10111)
            time.sleep(.3)
            items = menu_labels()
            other = "Allow idle shutdown" if not blocked else "Inhibit idle shutdown"
            assert target in items and other not in items, items
            client.send_action("Control.SetFocus(9000)")
            wait(lambda: boolean("Control.HasFocus(9000)"), True)
            for _ in range(len(items) + 1):
                if label("Container(9000).ListItem.Label") == target:
                    break
                rpc("Input.Down")
                time.sleep(.08)
            assert label("Container(9000).ListItem.Label") == target
            capture("idle_inhibited" if blocked else "idle_allowed")
            rpc("Input.Select")
            wait(lambda: boolean("System.IdleShutdownInhibited"), next_state)
            report["rows"].append({"before_inhibited": blocked, "visible_items": items, "clicked": target, "after_inhibited": next_state})
            # Close only this menu, and wait out its animation before reopening.
            client.send_action("Dialog.Close(shutdownmenu)")
            wait(lambda: window() != 10111, True)
            wait(lambda: boolean("Window.IsVisible(shutdownmenu)"), False)
        rpc("Settings.SetSettingValue", {"setting": "powermanagement.shutdowntime", "value": baseline_timeout})
        client.send_action("InhibitIdleShutdown(" + str(baseline_inhibit).lower() + ")")
        rpc("GUI.ActivateWindow", {"window": "addonbrowser", "parameters": ["addons://user/xbmc.python.script/", "return"]})
        time.sleep(.5)
        client.send_action("Container.SetViewMode(50)")
        client.send_action("Control.SetFocus(50)")
        wait(lambda: boolean("Control.HasFocus(50)"), True)
        for _ in range(70):
            if label("ListItem.Property(Addon.ID)") == "script.extendedinfo":
                break
            rpc("Input.Down")
            time.sleep(.08)
        assert label("ListItem.Property(Addon.ID)") == "script.extendedinfo"
        rpc("Input.ExecuteAction", {"action": "info"})
        wait(window, 10146)
        time.sleep(.4)
        origin = labels(["ListItem.AddonOrigin", "ListItem.Label", "ListItem.Property(Addon.ID)", "ListItem.Property(Addon.Status)", "ListItem.AddonLifecycleType", "Container(400).CurrentPage", "Container(400).NumPages"])
        assert origin["ListItem.Property(Addon.ID)"] == "script.extendedinfo"
        assert origin["ListItem.AddonOrigin"] == "Kodi Add-on repository", origin
        report["repository_origin"] = origin
        capture("addon_info_repository")
    except Exception as exc:
        failure = repr(exc)
        report["failure"] = failure
        report["failure_trace"] = traceback.format_exc()
    finally:
        if client and baseline_timeout is not None:
            try:
                rpc("Settings.SetSettingValue", {"setting": "powermanagement.shutdowntime", "value": baseline_timeout})
                client.send_action("InhibitIdleShutdown(" + str(baseline_inhibit).lower() + ")")
                wait(lambda: boolean("System.IdleShutdownInhibited"), baseline_inhibit)
                report["live_power_baseline_restored"] = True
            except Exception as exc:
                report["live_restore_failure"] = repr(exc)
        if client:
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
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
            cleanup["all_test_xml_match_production"] = {p.name: p.read_bytes() for p in xml.glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/idle_origin_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    return int(bool(failure) or not all(report["cleanup"].values()))


if __name__ == "__main__":
    sys.exit(main())
