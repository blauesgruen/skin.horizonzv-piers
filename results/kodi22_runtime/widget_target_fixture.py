"""Prepare an isolated variable-input fixture; never modifies this skin's source.

Run only with the isolated Kodi stopped. Inputs are static list properties;
copied production conditions and result values are evaluated by Kodi itself.
"""

import copy
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TEST = Path(os.environ["TEMP"]) / "horizonzv-kodi-test-146cbb2c139f4f68b53148a6e4286440"
XML = TEST / "portable_data/addons/skin.horizonzv/xml"
FIXTURE = XML / "Custom_1198_AuditWidgetTargets.xml"
assert XML.is_dir()
assert not FIXTURE.exists(), "Do not overwrite an existing fixture."
for path in (ROOT / "xml").glob("*.xml"):
    element = ET.parse(path).getroot()
    assert element.get("id") not in ("1198", "11198"), path

CASES = [
    ("Movie", "movie", "", "", ["videos"] * 3),
    ("Musicvideo", "musicvideo", "", "", ["videos"] * 3),
    ("Song", "song", "", "", ["music"] * 3),
    ("Album", "album", "", "", ["music"] * 3),
    ("Artist", "artist", "", "", ["music"] * 3),
    ("TV timers", "", "pvr://timers/tv/timers/", "", ["tvtimers"] * 3),
    ("Radio timers", "", "pvr://timers/radio/timers/", "", ["radiotimers"] * 3),
    ("TV rules", "", "pvr://timers/tv/rules/", "", ["tvtimerrules"] * 3),
    ("Radio rules", "", "pvr://timers/radio/rules/", "", ["radiotimerrules"] * 3),
    ("Radio rule child", "", "pvr://timers/radio/rules/1/2", "", ["radiotimerrules"] * 3),
    ("TV recordings", "", "pvr://recordings/tv/active/", "", ["tvrecordings"] * 3),
    ("TV channels", "", "pvr://channels/tv/All channels/", "", ["tvchannels"] * 3),
    ("Addon directory", "", "addons://user/all/", "", ["addonbrowser"] * 3),
    ("Favourites", "", "favourites://", "", ["favouritesbrowser", "favouritesbrowser", ""]),
    ("Unknown video plugin", "", "plugin://plugin.video.fixture/", "", ["videos", "videos", "videos"]),
    ("Unknown plugin", "", "plugin://fixture/", "", ["videos", "videos", ""]),
    ("Audio plugin", "", "plugin://plugin.audio.fixture/", "", ["music"] * 3),
    ("Local folder", "", "C:/skin-audit-folder/", "", ["videos", "videos", ""]),
    ("Games", "", "plugin://fixture/", "games", ["games"] * 3),
    ("Empty", "", "", "", ["videos", "videos", ""]),
    ("Musicvideo again", "musicvideo", "", "", ["videos"] * 3),
]

names = ["WidgetTarget_Dash", "WidgetTarget_Dash_FirstItem", "WidgetTarget"]
definitions = {v.get("name"): v for path in (ROOT / "xml").glob("*.xml")
               for v in ET.parse(path).getroot().iter("variable")}
replacements = {}
for source, prop in [("DBTYPE", "DBTYPE"), ("FolderPath", "Path")]:
    for prefix in ["Container.ListItem(1).", "Container.ListItem.", "ListItem."]:
        replacements[prefix + source] = "Container(600).ListItem.Property(Audit." + prop + ")"
for source in ["Container(9000).ListItem(1).Property(homemenu_id)",
               "Container(9000).ListItem.Property(homemenu_id)"]:
    replacements[source] = "Container(600).ListItem.Property(Audit.HomeID)"
replacements["Window(home).Property(WidgetLabel)"] = "Container(600).ListItem.Property(Audit.WidgetLabel)"

variables = ET.parse(ROOT / "xml/Variables.xml")
for name in names:
    variable = copy.deepcopy(definitions[name])
    variable.set("name", "Audit_" + name)
    for value in variable.findall("value"):
        condition = value.get("condition")
        if condition:
            for old, new in sorted(replacements.items(), key=lambda pair: -len(pair[0])):
                condition = condition.replace(old, new)
            value.set("condition", condition)
    variables.getroot().append(variable)
variables.write(XML / "Variables.xml", encoding="utf-8", xml_declaration=True)

window = ET.Element("window", {"id": "1198"})
ET.SubElement(window, "defaultcontrol", {"always": "true"}).text = "600"
controls = ET.SubElement(window, "controls")
background = ET.SubElement(controls, "control", {"type": "image"})
for tag, text in [("width", "100%"), ("height", "100%"), ("texture", "BlackBack.png")]:
    ET.SubElement(background, tag).text = text
listing = ET.SubElement(controls, "control", {"type": "list", "id": "600"})
for tag, text in [("left", "40"), ("top", "80"), ("width", "700"), ("height", "850"),
                  ("onup", "600"), ("ondown", "600")]:
    ET.SubElement(listing, tag).text = text
for layout in ["itemlayout", "focusedlayout"]:
    block = ET.SubElement(listing, layout, {"height": "44", "width": "700"})
    label = ET.SubElement(block, "control", {"type": "label"})
    for tag, text in [("label", "$INFO[ListItem.Label]"), ("font", "font12"), ("width", "700"),
                      ("textcolor", "white" if layout == "focusedlayout" else "grey")]:
        ET.SubElement(label, tag).text = text
content = ET.SubElement(listing, "content")
for label, dbtype, path, home, expected in CASES:
    item = ET.SubElement(content, "item")
    ET.SubElement(item, "label").text = label
    for name, text in [("DBTYPE", dbtype), ("Path", path), ("HomeID", home)]:
        ET.SubElement(item, "property", {"name": "Audit." + name}).text = text
for index, name in enumerate(names, 601):
    label = ET.SubElement(controls, "control", {"type": "label", "id": str(index)})
    for tag, text in [("left", "800"), ("top", str(120 + (index - 601) * 100)),
                      ("width", "1000"), ("font", "font12"), ("label", "$VAR[Audit_" + name + "]")]:
        ET.SubElement(label, tag).text = text
ET.indent(window)
ET.ElementTree(window).write(FIXTURE, encoding="utf-8", xml_declaration=True)

timers = ET.parse(ROOT / "xml/Timers.xml")
timer = ET.SubElement(timers.getroot(), "timer")
for tag, text in [("name", "auditwidgettargetopen"), ("start", "Window.IsActive(home)"),
                  ("stop", "false"), ("onstart", "ActivateWindow(1198)")]:
    ET.SubElement(timer, tag).text = text
timers.write(XML / "Timers.xml", encoding="utf-8", xml_declaration=True)
(ROOT / "results/kodi22_runtime/widget_target_fixture_cases.json").write_text(
    json.dumps({"variables": names, "cases": CASES, "input_replacements": replacements}, indent=2) + "\n")
print(json.dumps({"fixture": str(FIXTURE), "cases": len(CASES), "variables": names}))
