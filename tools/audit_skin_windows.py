"""Read-only check of literal window-action targets against the Piers snapshot.

Known numeric constants and custom XML IDs do not prove runtime availability.
Literal branches of referenced target variables and content targets are checked
too. Literal window identifiers in conditions and qualified properties are checked
without evaluating their conditions. Runtime registration remains outside scope.
No Kodi instance is accessed or started.
"""

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from audit_skin_actions import ACTION_PARAM, ACTION_TAGS, arguments
from audit_skin_info_names import CONDITION_TAGS, call_suffix, info_expressions


WINDOW_ACTIONS = {"activatewindow", "replacewindow", "activatewindowandfocus", "dialog.close"}
WINDOW_BOOLS = re.compile(
    r"(?<![\w])Window\.(Is|IsActive|IsVisible|IsDialogTopmost|IsModalDialogTopmost|"
    r"IsTopmost|Previous|Next)\s*(?=\()", re.I)
QUALIFIED_WINDOW = re.compile(r"(?<![\w])Window\s*(?=\()", re.I)


def resolve_window_target(target, registry, custom, known_ids, *, filename_query=False):
    """Mirror the checked Piers parser distinction; a name is not runtime proof."""
    if "$" in target:
        return {"resolution": "unresolved dynamic window target"}
    # GUIInfoManager checks the literal lowercase substring, not a file suffix.
    if filename_query and "xml" in target:
        return {"resolution": "XML filename query; runtime producer not proven"}
    normalized = target.lower().removesuffix(".xml")
    if normalized.startswith("window") and len(normalized) > 6:
        normalized = normalized[6:]
    normalized = normalized.removeprefix("my")
    if normalized.isdigit():
        number = int(normalized)
        number = number if number > 9999 else number + 10000
        if number in custom:
            resolution = "custom skin XML id; runtime registration not proven"
        elif number in known_ids:
            resolution = "Kodi WindowIDs constant; runtime availability not proven"
        else:
            resolution = "unconfirmed numeric target"
        return {"resolution": resolution, "id": number}
    if normalized in registry["names"]:
        return {"resolution": "Kodi named window", "id": registry["names"][normalized]["id"]}
    return {"resolution": "unregistered window name"}


def window_info_targets(element):
    """Bounded extraction from condition text/attributes and INFO macros only."""
    values = []
    if element.tag in CONDITION_TAGS or element.tag == "info":
        values.append(("condition/info", element.text or ""))
    if element.get("condition"):
        values.append(("condition attribute", element.get("condition")))
    for value in [element.text or "", *element.attrib.values()]:
        values.extend(("info macro", expression) for expression in info_expressions(value))
    for kind, value in values:
        for match in WINDOW_BOOLS.finditer(value):
            suffix = call_suffix(value, match.end())
            if suffix is None:
                yield {"kind": kind, "method": match[1].lower(), "expression": value,
                       "parse_error": "unbalanced window argument"}
                continue
            args = arguments("Window." + match[1] + suffix)
            if args is None or len(args) != 1:
                yield {"kind": kind, "method": match[1].lower(), "expression": value,
                       "parse_error": "expected one window argument"}
                continue
            yield {"kind": kind, "method": match[1].lower(), "expression": value,
                   "target": args[0].strip("\"' "), "filename_query": True}
        for match in QUALIFIED_WINDOW.finditer(value):
            suffix = call_suffix(value, match.end())
            if not suffix:
                continue
            after = value[match.end():].lstrip()[len(suffix):]
            if not re.match(r"\s*\.Property\s*\(", after, re.I):
                continue
            args = arguments("Window" + suffix)
            if args is None or len(args) > 1:
                yield {"kind": kind, "method": "property", "expression": value,
                       "parse_error": "expected at most one window qualifier"}
                continue
            yield {"kind": kind, "method": "property", "expression": value,
                   "target": args[0].strip("\"' ") if args else "", "filename_query": False}


def audit(root, registry):
    known_ids = set(registry["ids"].values())
    custom, documents = {}, []
    for path in sorted((root / "xml").glob("*.xml")):
        window = ET.parse(path).getroot()
        documents.append((path, window))
        if (path.name.lower().startswith("custom_") and window.tag == "window"
                and window.get("id", "").isdigit()):
            value = int(window.get("id"))
            custom[value if value > 9999 else value + 10000] = path.relative_to(root).as_posix()
    rows, findings, dynamic, content_targets = [], [], [], []
    variables = {v.get("name"): (path, v) for path, document in documents
                 for v in document.iter("variable")}
    for path, window in documents:
        for element in window.iter():
            if not (element.tag in ACTION_TAGS or
                    element.tag == "param" and ACTION_PARAM.fullmatch(element.get("name", ""))):
                continue
            value = (element.text or element.get("value", "")).strip()
            match = re.match(r"([\w.]+)\s*\(", value)
            if not match:
                continue
            name = match[1].lower().removeprefix("xbmc.")
            if name not in WINDOW_ACTIONS:
                continue
            args = arguments(value)
            if not args:
                continue
            target = args[0].strip("\"' ")
            row = {"file": path.relative_to(root).as_posix(), "action": value, "target": target}
            if "$" in target:
                dynamic.append(row)
                continue
            normalized = target.lower()
            if name == "dialog.close" and normalized == "all":
                row["resolution"] = "all dialogs"
                rows.append(row)
                continue
            # Match CWindowTranslator's normalization order.
            normalized = normalized.removesuffix(".xml")
            if normalized.startswith("window") and len(normalized) > 6:
                normalized = normalized[6:]
            normalized = normalized.removeprefix("my")
            if normalized.isdigit():
                number = int(normalized)
                number = number if number > 9999 else number + 10000
                row["id"] = number
                if number in custom:
                    row["resolution"] = "custom skin XML id; runtime registration not proven"
                elif number in known_ids:
                    row["resolution"] = "Kodi WindowIDs constant; runtime availability not proven"
                else:
                    row["resolution"] = "unconfirmed numeric target"
                    findings.append(row)
            elif normalized in registry["names"]:
                row.update({"resolution": "Kodi named window", "id": registry["names"][normalized]["id"]})
            else:
                row["resolution"] = "unregistered window name"
                findings.append(row)
            rows.append(row)
    for path, document in documents:
        for content in document.iter("content"):
            target = content.get("target", "").strip()
            if target:
                content_targets.append({"file": path.relative_to(root).as_posix(), "target": target})
    referenced = {}
    unresolved = []
    for row in [*dynamic, *content_targets]:
        match = re.fullmatch(r"\$VAR\[([\w]+)\]", row["target"])
        if match:
            referenced.setdefault(match[1], []).append(row)
        elif "$" in row["target"]:
            unresolved.append(row)
        elif row["target"].lower() not in registry["names"]:
            findings.append({**row, "resolution": "unconfirmed literal content target"})
    expanded = []
    for name, uses in sorted(referenced.items()):
        if name not in variables:
            findings.append({"variable": name, "resolution": "missing target variable"})
            continue
        path, variable = variables[name]
        branches = []
        for value in variable.findall("value"):
            target = (value.text or "").strip()
            branch = {"target": target, "condition": value.get("condition")}
            if "$" in target:
                branch["resolution"] = "unresolved dynamic branch"
                unresolved.append({"variable": name, **branch})
            elif target.lower() in registry["names"]:
                branch["resolution"] = "Kodi named window"
                branch["id"] = registry["names"][target.lower()]["id"]
            else:
                branch["resolution"] = "unconfirmed variable target"
                findings.append({"file": path.relative_to(root).as_posix(), "variable": name, **branch})
            branches.append(branch)
        expanded.append({"variable": name, "file": path.relative_to(root).as_posix(),
                         "uses": len(uses), "branches": branches,
                         "has_unconditional_fallback": any(not v.get("condition") for v in variable.findall("value"))})
    info_targets, info_dynamic = [], []
    for path, document in documents:
        for element in document.iter():
            for target in window_info_targets(element):
                row = {"file": path.relative_to(root).as_posix(), "element": element.tag, **target}
                if "parse_error" in row:
                    findings.append(row)
                elif row["method"] == "property" and not row["target"]:
                    row["resolution"] = "implicit current window"
                else:
                    row.update(resolve_window_target(row["target"], registry, custom, known_ids,
                                                     filename_query=row["filename_query"]))
                    if row["resolution"] == "unresolved dynamic window target":
                        info_dynamic.append(row)
                    elif row["resolution"] in {"unregistered window name", "unconfirmed numeric target"}:
                        findings.append(row)
                info_targets.append(row)
    return {"source_ref": registry["source_ref"],
            "scope": "Literal window-action first targets, content targets, branches of directly referenced target variables, window-condition arguments and explicit Window(...).Property qualifiers. Boolean XML filename queries are distinguished from translator names. Does not evaluate conditions, expand include parameters, validate property keys or prove runtime registration, producer presence or nonempty branch selection.",
            "references": rows, "findings": findings, "dynamic": dynamic,
            "content_targets": content_targets, "target_variables": expanded,
            "unresolved_dynamic": unresolved,
            "window_info_targets": info_targets, "dynamic_window_info_targets": info_dynamic,
            "custom_windows_with_ids": custom}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skin_directory", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.skin_directory.resolve()
    registry = json.loads((root / "results/kodi22_inventory/kodi_window_registry.json").read_text(encoding="utf-8"))
    result = audit(root, registry)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
