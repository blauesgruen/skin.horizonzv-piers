"""Read-only comparison against the checked-in Kodi Piers action registry snapshot.

This is a bounded audit, not a full Kodi expression parser. It does not resolve
include parameters/variables, validate window IDs or execute any action.
"""

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ACTION_TAGS = {"onclick", "onfocus", "onunfocus", "onload", "onunload",
               "onstart", "onstop", "onup", "ondown", "onleft", "onright",
               "onback", "oninfo"}
ACTION_PARAM = re.compile(r"on(?:click|focus|unfocus|up|down|left|right|back|info)\d*", re.I)


def arguments(value):
    """Split top-level arguments, respecting quotes, escapes and nested calls."""
    if "(" not in value:
        return [] if ")" not in value else None
    start = value.find("(")
    if not value.endswith(")"):
        return None
    inner = value[start + 1:-1]
    if not inner.strip():
        return []
    parts, current = [], []
    depth, quote, escaped = 0, None, False
    for char in inner:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            current.append(char)
            escaped = True
        elif quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
            current.append(char)
        elif char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            if depth < 0:
                return None
            current.append(char)
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if quote or depth or escaped:
        return None
    return [*parts, "".join(current).strip()]


def audit(root, registry):
    commands = {x["name"].lower(): x for x in registry["commands"]}
    actions = set(registry["actions"])
    references, findings, dynamic, nested = [], [], [], []

    def inspect_nested(parent, name, args, depth=0):
        # GUIBuiltins.cpp: Action translates argument 0; AlarmClock schedules 1.
        index = {"action": 0, "alarmclock": 1}.get(name)
        if index is None or index >= len(args) or depth >= 8:
            return
        value = args[index].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        row = {**parent, "wrapper": name, "nested_value": value}
        if "$" in value:
            dynamic.append(row)
            return
        match = re.match(r"([\w.]+)\s*(?:\(|$)", value)
        if not match:
            findings.append({**row, "rule": "unparsed-nested-action"})
            return
        target = match[1].lower().removeprefix("xbmc.")
        row["nested_name"] = target
        nested.append(row)
        # AlarmClock executes built-ins; Action uses the input action translator,
        # which also accepts registered built-ins.
        if target not in commands and not (name == "action" and target in actions):
            findings.append({**row, "rule": "unregistered-nested-action"})
            return
        child_args = arguments(value)
        if child_args is None:
            findings.append({**row, "rule": "unparsed-nested-arguments"})
        elif target in commands and len(child_args) < commands[target]["min_args"]:
            findings.append({**row, "rule": "too-few-nested-arguments",
                             "minimum": commands[target]["min_args"], "actual": len(child_args)})
        elif child_args is not None:
            inspect_nested(row, target, child_args, depth + 1)

    numeric = 0
    for path in sorted((root / "xml").glob("*.xml")):
        # Comments are excluded by ElementTree's default parser.
        for element in ET.parse(path).getroot().iter():
            if not (element.tag in ACTION_TAGS or
                    (element.tag == "param" and ACTION_PARAM.fullmatch(element.get("name", "")))):
                continue
            value = (element.text or element.get("value", "")).strip()
            if not value:
                continue
            row = {"file": path.relative_to(root).as_posix(), "element": element.tag,
                   "param": element.get("name"), "value": value}
            if re.fullmatch(r"-?\d+", value):
                numeric += 1
                continue
            if value.startswith("$"):
                dynamic.append(row)
                continue
            match = re.match(r"([\w.]+)\s*(?:\(|$)", value)
            if not match:
                findings.append({**row, "rule": "unparsed-action"})
                continue
            name = match[1].lower().removeprefix("xbmc.")
            row["name"] = name
            references.append(row)
            if name not in commands and name not in actions:
                findings.append({**row, "rule": "unregistered-action"})
                continue
            # Kodi substitutes dynamic text before parsing. Do not guess its arity.
            if "$" in value:
                dynamic.append(row)
                continue
            args = arguments(value)
            if args is None:
                findings.append({**row, "rule": "unparsed-arguments"})
            elif name in commands and len(args) < commands[name]["min_args"]:
                findings.append({**row, "rule": "too-few-arguments",
                                 "minimum": commands[name]["min_args"], "actual": len(args)})
            elif args is not None:
                inspect_nested(row, name, args)
    return {"source_ref": registry["source_ref"],
            "scope": "Literal action tags and action include parameters, including Action argument 0 and AlarmClock argument 1; registration and minimum argument count only. No include expansion, variable values, other nested arguments, semantic parameter validation or runtime availability checks. Dynamic text is excluded from argument checks; numeric focus targets are counted separately.",
            "registered_builtins": len(commands), "registered_input_actions": len(actions),
            "literal_references": len(references),
            "distinct_literal_names": sorted({x["name"] for x in references}),
            "findings": findings, "dynamic": dynamic, "nested": nested,
            "numeric_focus_targets": numeric}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skin_directory", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.skin_directory.resolve()
    registry = json.loads((root / "results/kodi22_inventory/kodi_action_registry.json").read_text(encoding="utf-8"))
    print(json.dumps(audit(root, registry), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
