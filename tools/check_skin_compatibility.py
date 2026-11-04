"""Check known skin regressions; this is not a complete Kodi schema/API validator.

Run with Python 3: python tools/check_skin_compatibility.py [skin-directory]
Only active XML under xml/ and addon.xml is read. No Kodi instance is required.
Rules reflect the source reviews in results/kodi22_compatibility_audit.md.
"""

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


PIERS_INFO = "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/GUIInfoManager.cpp"
PIERS_FACTORY = "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/guilib/GUIControlFactory.cpp"
V23 = "https://xbmc.github.io/docs.kodi.tv/master/kodi-base/d8/d22/skinning_v23.html"

# Each match flags a literal reference, not proof of its execution or context.
# Unsupported names and deprecated-but-supported names are distinguished.
RULES = [
    ("invalid-shutdown-window", "error", r"\bActivateWindow\s*\(\s*shutdown\s*[,)]", "The registered window name is shutdownmenu, not shutdown.", "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/input/WindowTranslator.cpp"),
    ("invalid-activate", "error", r"(?<![\w.])Activate\s*\(", "Activate is not a registered Piers action; review intent before using ActivateWindow.", "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/interfaces/builtins/GUIBuiltins.cpp"),
    ("invalid-selectbool-single-argument", "error", r"\bSkin\.SelectBool\s*\(\s*[^$,()]+\)", "SelectBool needs a heading and selectable label|setting pairs, not a single setting name.", "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/interfaces/builtins/SkinBuiltins.cpp"),
    ("deprecated-window-istopmost", "warning", r"\bWindow\.IsTopmost\s*\(", "Deprecated alias; use Window.IsDialogTopmost.", PIERS_INFO),
    ("deprecated-system-isinhibit", "warning", r"\bSystem\.IsInhibit\b", "Deprecated alias; use System.IdleShutdownInhibited.", PIERS_INFO),
    ("deprecated-addonbroken", "warning", r"\bListItem\.AddonBroken\b", "Deprecated label; review AddonLifecycleType and AddonLifecycleDesc.", PIERS_INFO),
    ("deprecated-slideshow-metadata", "warning", r"\bSlideshow\.(?:Colour|Process)\b", "Marked for future removal; no replacement established in this audit.", PIERS_INFO),
    ("removed-displayafterseek", "error", r"\bPlayer\.DisplayAfterSeek\b", "Removed in Kodi 20; use Player.HasPerformedSeek(integer seconds).", PIERS_INFO),
    ("removed-isempty", "error", r"(?<![\w.])IsEmpty\s*\(", "Unqualified IsEmpty was removed; use String.IsEmpty.", PIERS_INFO),
    ("invalid-control-isempty", "error", r"\bControl\.IsEmpty\s*\(", "Control.IsEmpty is not registered in Piers.", PIERS_INFO),
    ("invalid-skin-hasaddon", "error", r"\bSkin\.HasAddon\s*\(", "Skin.HasAddon is not registered; inspect System.HasAddon(id).", PIERS_INFO),
    ("invalid-player-mute", "error", r"\bPlayer\.Mute\b", "Piers registers Player.Muted, not Player.Mute.", PIERS_INFO),
    ("removed-player-starrating", "error", r"\bPlayer\.StarRating\b", "Old image label absent from Piers; review MusicPlayer.UserRating and artwork scale.", PIERS_INFO),
    ("invalid-addon-label", "error", r"\bListItem\.Addon(?:Repository|Path|Source)\b", "Name absent from Piers registry; inspect AddonOrigin where appropriate.", PIERS_INFO),
    ("invalid-container-haspages", "error", r"\bContainer\.HasPages\s*\(", "Not registered; inspect Container(id).HasNext/HasPrevious.", PIERS_INFO),
    ("invalid-empty-focus", "error", r"\bControl\.HasFocus\s*\(\s*\)", "Control.HasFocus requires a nonzero control ID.", PIERS_INFO),
    ("invalid-rds-isclassical", "error", r"\bRDS\.IsClassical\b", "RDS.IsClassical is not registered in Piers.", PIERS_INFO),
    ("deprecated-thumb", "warning", r"\bListItem\.Thumb\b", "Deprecated label; use ListItem.Art(thumb).", PIERS_INFO),
    ("deprecated-picture-metadata", "warning", r"\bListItem\.Picture(?:Colour|Process)\b", "Marked for future removal; no replacement established in this audit.", PIERS_INFO),
    ("deprecated-playdvd", "warning", r"(?<![\w.])(?:XBMC\.)?PlayDVD\s*\(", "Deprecated built-in; use PlayDisc().", "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/interfaces/builtins/PlayerBuiltins.cpp"),
]
# Additional GUIInfoManager removal history, not just names previously found in this skin.
# Player.DisplayAfterSeek and IsEmpty already have targeted rules above. Bare on/off
# boolean atoms are covered by audit_skin_info_names.py, not by a text search here.
REMOVED_INFO_BY_VERSION = {
    "13": [
        "Network.SubnetAddress"
    ],
    "16": [
        "System.Platform.ATV2"
    ],
    "17": [
        "ListItem.StarRating",
        "Player.ShowCodec",
        "System.GetBool(pvrmanager.enabled)"
    ],
    "18": [
        "ListItem.Property(artistthumbs)",
        "ListItem.Property(artistthumb)",
        "ADSP.ActiveStreamType",
        "ADSP.DetectedStreamType",
        "ADSP.MasterName",
        "ADSP.MasterInfo",
        "ADSP.MasterOwnIcon",
        "ADSP.MasterOverrideIcon",
        "ListItem.ChannelNumber",
        "ListItem.SubChannelNumber",
        "MusicPlayer.ChannelNumber",
        "MusicPlayer.SubChannelNumber",
        "VideoPlayer.ChannelNumber",
        "VideoPlayer.SubChannelNumber",
        "System.HasModalDialog",
        "StringCompare()",
        "SubString()",
        "IntegerGreaterThan()",
        "System.HasADSP",
        "ADSP.IsActive",
        "ADSP.HasInputResample",
        "ADSP.HasPreProcess",
        "ADSP.HasMasterProcess",
        "ADSP.HasPostProcess",
        "ADSP.HasOutputResample",
        "ADSP.MasterActive"
    ],
    "19": [
        "System.Platform.Linux.RaspberryPi"
    ],
    "21": [
        "Network.DHCPAddress"
    ],
    "22": [
        "Player.Cutlist",
        "Slideshow.EXIFSoftware"
    ]
}


def removed_info_pattern(name):
    if name.endswith("()"):
        body = re.escape(name[:-2]) + r"\s*\("
    elif "(" in name:
        method, argument = name[:-1].split("(", 1)
        body = re.escape(method) + r"\s*\(\s*" + re.escape(argument) + r"\s*\)"
    else:
        body = re.escape(name) + r"\b"
    return r"(?<![\w])" + body


RULES += [
    ("removed-info-history", "error", removed_info_pattern(name),
     f"GUIInfoManager removal history lists {name} as removed in Kodi {version}; review its replacement and actual context.",
     PIERS_INFO)
    for version, names in REMOVED_INFO_BY_VERSION.items() for name in names
]
COMPILED_RULES = [(code, level, re.compile(pattern, re.I), message, source)
                  for code, level, pattern, message, source in RULES]
SCALAR_TAGS = {"visible", "enable", "onclick", "onfocus", "onload", "onunload",
               "label", "texture", "imagepath"}
SINGLETON_CONTROL_TAGS = {"height", "orientation", "texturenofocus", "itemgap",
                          "aspectratio", "viewtype", "align", "font", "right"}


def check(root):
    findings = []
    files = [root / "addon.xml", *sorted((root / "xml").glob("*.xml"))]

    def report(path, node, code, level, message, source, value=None):
        row = {"file": path.relative_to(root).as_posix(), "element": node,
               "rule": code, "severity": level, "message": message, "source": source}
        if value is not None:
            row["value"] = value
        findings.append(row)

    for path in files:
        try:
            tree = ET.parse(path)
        except (ET.ParseError, OSError) as exc:
            report(path, "/", "xml-read", "error", str(exc), "XML parser")
            continue
        # ElementTree's default parser discards XML comments.
        for index, element in enumerate(tree.getroot().iter()):
            location = f"{element.tag}[document-index={index}]"
            condition = element.get("condition", "")
            if re.search(r"(?:^|[+|\[!])\s*Conditional\s*(?=$|[+|\]])", condition, re.I):
                report(path, location, "invalid-conditional-operand", "error",
                       "Conditional is an animation type, not a registered boolean operand.", PIERS_INFO, condition)
            if element.tag in SCALAR_TAGS and len(element):
                report(path, location, "nested-scalar", "error",
                       "Expected text; found nested elements. Review loader semantics.", PIERS_FACTORY)
            if element.tag == "control":
                control_type = element.get("type", "").lower()
                for tag, applies, message in [
                    ("textwidht", True, "Misspelled property; the loader reads textwidth."),
                    ("highlightcolor", control_type == "rss", "RSS reads textcolor, titlecolor and headlinecolor, not highlightcolor."),
                    ("wraparound", control_type == "fixedlist", "The fixedlist loader does not read a wraparound XML property; native navigation decides wrapping."),
                ]:
                    if applies and element.find(tag) is not None:
                        report(path, location, "ignored-control-property", "error",
                               message, PIERS_FACTORY, tag)
                for tag in sorted(SINGLETON_CONTROL_TAGS):
                    if len(element.findall(tag)) > 1:
                        report(path, location, "duplicate-singleton", "error",
                               f"Repeated single-value control property: {tag}", PIERS_FACTORY)
            if element.tag == "control" and element.get("type", "").lower() == "gamewindow":
                if element.find("pixels") is not None:
                    report(path, location, "v23-gamewindow-pixels", "error",
                           "pixels is removed in Kodi 23; use savestate screenshot artwork.", V23)
            if element.tag == "include" and element.get("content"):
                seen = set()
                for param in element.findall("param"):
                    name = param.get("name")
                    if name in seen:
                        report(path, location, "duplicate-include-param", "error",
                               f"Repeated include parameter: {name}",
                               "https://github.com/xbmc/xbmc/blob/22.0rc1-Piers/xbmc/guilib/GUIIncludes.cpp")
                    seen.add(name)
            for value in [element.text or "", *element.attrib.values()]:
                for code, level, pattern, message, source in COMPILED_RULES:
                    if pattern.search(value):
                        report(path, location, code, level, message, source, value.strip())
    if not (root / "xml").is_dir() or len(files) == 1:
        report(root / "xml", "/", "missing-skin-xml", "error",
               "No skin XML files found.", "Filesystem")
    return {"scope": "Known literal regressions and selected XML structures only; no include expansion, dynamic API resolution or runtime validation.",
            "files_checked": len(files), "findings": findings,
            "errors": sum(f["severity"] == "error" for f in findings),
            "warnings": sum(f["severity"] == "warning" for f in findings)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skin_directory", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = check(args.skin_directory.resolve())
    print(json.dumps(result, indent=2, ensure_ascii=True))
    # Warnings also fail: this skin has deliberately migrated the listed deprecations.
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
