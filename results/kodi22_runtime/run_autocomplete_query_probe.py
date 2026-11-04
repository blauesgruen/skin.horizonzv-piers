"""Visible production keyboard query test with unchanged local dictionary provider."""
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
from pathlib import Path
from urllib.parse import parse_qsl


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(r"C:\Users\zorno\AppData\Local\Temp\horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440")
    check = subprocess.run(["powershell.exe", "-NoProfile", "-Command", "@(Get-Process kodi -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert check.stdout.strip() == "0", "Another Kodi is running"
    work = Path(tempfile.mkdtemp(prefix="review-encoded-autocomplete-", dir=root))
    skin = root / "portable_data/addons/skin.horizonzv"
    for p in (repo / "xml").glob("*.xml"):
        shutil.copy2(p, skin / "xml" / p.name)
    # RPC does not expand $VAR directly; observe it through a native label.
    keyboard_xml = skin / "xml/DialogKeyboard.xml"
    tree = ET.parse(keyboard_xml)
    observation = ET.SubElement(tree.getroot().find("controls"), "control", {"type": "label", "id": "1197"})
    for tag, text in {"top": "-100", "width": "1920", "height": "1", "font": "font12", "label": "$VAR[AutoCompletionContentVar]"}.items():
        ET.SubElement(observation, tag).text = text
    tree.write(keyboard_xml, encoding="utf-8", xml_declaration=True)
    shutil.copy2(repo / "addon.xml", skin / "addon.xml")
    helper = skin / "resources/scripts/autocomplete_query.py"
    helper.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / "resources/scripts/autocomplete_query.py", helper)
    rels = ("userdata/guisettings.xml", "userdata/addon_data/skin.horizonzv/settings.xml")
    for rel in rels:
        shutil.copy2(root / "portable_data" / rel, work / Path(rel).name)
    provider_settings = root / "portable_data/userdata/addon_data/plugin.program.autocompletion/settings.xml"
    previous_settings = provider_settings.read_bytes() if provider_settings.exists() else None
    provider_settings.parent.mkdir(parents=True, exist_ok=True)
    config = ET.Element("settings", {"version": "2"})
    for name, value in {"autocomplete_provider": "Local", "autocomplete_lang": "en", "autocomplete_lang_local": "en"}.items():
        ET.SubElement(config, "setting", {"id": name}).text = value
    ET.ElementTree(config).write(provider_settings, encoding="utf-8", xml_declaration=True)
    sources = [root / "portable_data/addons/plugin.program.autocompletion/plugin.py",
               root / "portable_data/addons/script.module.autocompletion/lib/AutoCompletion.py"]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    hidden_script = work / "hidden_keyboard.py"
    hidden_script.write_text('import xbmc\nxbmc.Keyboard("", "HorizonzV hidden-input test", True).doModal()\n', encoding="utf-8")
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

    query_label = "Window(virtualkeyboard).Property(HorizonzV.AutoCompletion.Query)"
    owner_label = "Window(virtualkeyboard).Property(HorizonzV.AutoCompletion.Owner)"
    report = {"scope": "Production skin query encoder with unchanged AutoCompletion 2.1.2 / local dictionary; no remote suggestion service", "rows": []}
    client = process = None
    enabled = None
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
        enabled = rpc("Addons.GetAddonDetails", {"addonid": "plugin.program.autocompletion", "properties": ["enabled"]})["result"]["addon"]["enabled"]
        rpc("Addons.SetAddonEnabled", {"addonid": "plugin.program.autocompletion", "enabled": True})
        client = XBMCClient(name="HorizonzV encoded keyboard query", uid=secrets.randbits(32))
        client.connect(port=9777)
        time.sleep(.2)
        client.send_action("Skin.SetString(HorizonAudit.Query)")
        wait(lambda: boolean("Window.IsVisible(virtualkeyboard)"), True)
        wait(lambda: bool(label(owner_label)), True)
        for text in ["A&B", "C++", "100%20real", 'A, "B" \\ C', "Bj\u00f6rk \u6771\u4eac", "hel"]:
            assert rpc("Input.SendText", {"text": text, "done": False}).get("result") == "OK"
            wait(lambda: dict(parse_qsl(label("Control.GetLabel(1197)").split("?", 1)[-1])).get("id"), text)
            value = label("Control.GetLabel(1197)")
            report["rows"].append({"input": text, "native_url": value, "decoded_id": dict(parse_qsl(value.split("?", 1)[1]))["id"]})
        wait(lambda: int(label("Container(9010).NumItems") or "0") > 0, True)
        client.send_action("Control.SetFocus(9010)")
        wait(lambda: boolean("Control.HasFocus(9010)"), True)
        selected = label("Container(9010).ListItem.Label")
        assert selected.startswith("hel"), selected
        screenshot = repo / "results/kodi22_runtime/autocomplete_query_native.png"
        screenshot.unlink(missing_ok=True)
        client.send_action('TakeScreenshot("' + screenshot.as_posix() + '")')
        wait(screenshot.exists, True)
        rpc("Input.Select")
        wait(lambda: label("Control.GetLabel(312).index(1)"), selected)
        report["normal_suggestion_selection"] = {"selected": selected, "native_input": label("Control.GetLabel(312).index(1)")}
        rpc("Input.Back")
        wait(lambda: boolean("Window.IsVisible(virtualkeyboard)"), False)
        wait(lambda: label(query_label), "")
        wait(lambda: label(owner_label), "")
        client.send_action('RunScript("' + hidden_script.as_posix() + '")')
        wait(lambda: boolean("System.HasHiddenInput"), True)
        rpc("Input.SendText", {"text": "authored hidden-input fixture", "done": False})
        time.sleep(.3)
        assert label(query_label) == "" and label(owner_label) == ""
        assert label("Control.GetLabel(1197)") == ""
        report["hidden_input"] = {"encoded_query_empty": True, "helper_not_started": True, "content_empty": True}
        rpc("Input.Back")
        wait(lambda: boolean("Window.IsVisible(virtualkeyboard)"), False)
        rpc("Addons.SetAddonEnabled", {"addonid": "plugin.program.autocompletion", "enabled": False})
        client.send_action("Skin.SetString(HorizonAudit.Query)")
        wait(lambda: boolean("Window.IsVisible(virtualkeyboard)"), True)
        time.sleep(.3)
        assert label(query_label) == "" and label(owner_label) == ""
        report["disabled_provider"] = {"helper_not_started": True, "query_empty": True}
        rpc("Input.Back")
    except Exception as exc:
        failure = repr(exc)
        report["failure"] = failure
        report["failure_trace"] = traceback.format_exc()
    finally:
        if enabled is not None:
            try:
                rpc("Addons.SetAddonEnabled", {"addonid": "plugin.program.autocompletion", "enabled": enabled})
                report["enabled_state_restored"] = rpc("Addons.GetAddonDetails", {"addonid": "plugin.program.autocompletion", "properties": ["enabled"]})["result"]["addon"]["enabled"] == enabled
            except Exception:
                report["enabled_state_restored"] = False
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
            shutil.copy2(repo / "xml/DialogKeyboard.xml", keyboard_xml)
            for rel in rels:
                shutil.copy2(work / Path(rel).name, root / "portable_data" / rel)
            if previous_settings is None:
                assert provider_settings.resolve().parent == (root / "portable_data/userdata/addon_data/plugin.program.autocompletion").resolve()
                provider_settings.unlink(missing_ok=True)
            else:
                provider_settings.write_bytes(previous_settings)
            cleanup["provider_settings_restored"] = not provider_settings.exists() if previous_settings is None else provider_settings.read_bytes() == previous_settings
            cleanup["profile_restored"] = all((work / Path(rel).name).read_bytes() == (root / "portable_data" / rel).read_bytes() for rel in rels)
            cleanup["all_test_xml_match_production"] = {p.name: p.read_bytes() for p in (skin / "xml").glob("*.xml")} == {p.name: p.read_bytes() for p in (repo / "xml").glob("*.xml")}
            cleanup["skin_helper_and_manifest_match_production"] = helper.read_bytes() == (repo / "resources/scripts/autocomplete_query.py").read_bytes() and (skin / "addon.xml").read_bytes() == (repo / "addon.xml").read_bytes()
        cleanup["provider_sources_unchanged"] = all(hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        report["cleanup"] = cleanup
        (repo / "results/kodi22_runtime/autocomplete_query_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    return int(bool(failure) or not all(cleanup.values()))


if __name__ == "__main__":
    sys.exit(main())
