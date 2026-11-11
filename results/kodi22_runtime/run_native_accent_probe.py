"""Visible accent-color checks in the existing isolated Kodi runtime."""
import json
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET

from visible_standard_kodi import VisibleKodi


def main():
    repo = Path(__file__).resolve().parents[2]
    root = Path(sys.argv[1]).resolve()
    session = VisibleKodi(repo, "HorizonzV native accent", test_root=root)
    skin = root / "portable_data/addons/skin.horizonzv"
    paths = ["xml/SkinSettings.xml", "xml/Variables.xml", "xml/Includes_SkinAddonsContent.xml",
             "resources/scripts/edit_color.py", "language/resource.language.de_de/strings.po",
             "language/resource.language.en_gb/strings.po", "xml/script-skin_helper_service-ColorPicker.xml"]
    originals = {rel: (skin / rel).read_bytes() if (skin / rel).exists() else None for rel in paths}
    checks = {}
    report = repo / "results/kodi22_runtime/native_accent_checks.json"

    def action(command):
        session.client.send_action(command)
        time.sleep(.35)

    def label(name):
        return session.rpc("XBMC.GetInfoLabels", {"labels": [name]})[name]

    def visible(name):
        expr = "Window.IsVisible(" + name + ")"
        return session.rpc("XBMC.GetInfoBooleans", {"booleans": [expr]})[expr]

    def value():
        return label("Skin.String(MySkinColor)")

    def screenshot(name):
        path = repo / "results/kodi22_runtime" / name
        action('TakeScreenshot("' + path.as_posix() + '")')
        session.wait(lambda: path.exists())

    try:
        for rel in paths:
            source = repo / rel
            target = skin / rel
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            elif target.exists():
                target.unlink()
        session.start()
        action("Skin.SetString(MySkinColor,80112233)")
        session.wait(lambda: value() == "80112233")
        settings = ET.parse(repo / "xml/SkinSettings.xml")
        palette = settings.find(".//control[@id='824']/onclick").text
        edit = settings.find(".//control[@id='825']/onclick").text
        action(palette)
        session.wait(lambda: visible("12008"))
        count = int(label("Container(6).NumItems"))
        if count < 2 or not label("Control.GetLabel(1)"):
            raise RuntimeError("Palette or title missing")
        checks["native_palette"] = {"colors": count, "heading": label("Control.GetLabel(1)")}
        screenshot("native_accent_palette.png")
        action("SetFocus(6)")
        selected = label("Container(6).ListItem.Label2")
        session.rpc("Input.Select")
        session.wait(lambda: not visible("12008"))
        session.wait(lambda: value() == selected)
        checks["palette_selection_saved"] = selected
        action(palette)
        session.wait(lambda: visible("12008"))
        session.rpc("Input.Back")
        session.wait(lambda: not visible("12008"))
        if value() != selected:
            raise RuntimeError("Palette cancel changed the color")
        checks["palette_cancel_preserves_color"] = True
        action(edit)
        session.wait(lambda: visible("12000"))
        screenshot("native_accent_edit_menu.png")
        session.rpc("Input.Select")
        session.wait(lambda: visible("10103"))
        session.rpc("Input.SendText", {"text": "40123456", "done": True})
        session.wait(lambda: value() == "40123456")
        checks["hex_input_saved"] = value()
        action(edit)
        session.wait(lambda: visible("12000"))
        session.rpc("Input.Down")
        session.rpc("Input.Select")
        session.wait(lambda: visible("10109"))
        for control in [23, 23, 15, 10]:
            action(f"Control.SetFocus({control})")
            session.rpc("Input.Select")
        checks["numeric_input"] = label("Control.GetLabel(4)")
        screenshot("native_accent_opacity.png")
        action("Control.SetFocus(21)")
        session.rpc("Input.Select")
        session.wait(lambda: value() == "80123456")
        checks["opacity_50_preserves_rgb"] = value()
        action(edit)
        session.wait(lambda: visible("12000"))
        session.rpc("Input.Back")
        session.wait(lambda: not visible("12000"))
        if value() != "80123456":
            raise RuntimeError("Editor cancel changed the color")
        checks["editor_cancel_preserves_color"] = True
        checks["passed"] = True
    except Exception as exc:
        checks["passed"] = False
        checks["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        checks["cleanup"] = session.close()
        for rel, data in originals.items():
            target = skin / rel
            if data is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(data)
        checks["test_skin_files_restored"] = all(
            ((skin / rel).read_bytes() if (skin / rel).exists() else None) == data
            for rel, data in originals.items())
        report.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(checks, ensure_ascii=True))


if __name__ == "__main__":
    main()
