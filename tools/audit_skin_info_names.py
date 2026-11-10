"""Read-only candidate scan of literal Kodi info/condition method names.

Uses a pinned GUIInfoManager registry snapshot. Unknown candidates need source
review; this does not validate argument counts, property keys or runtime data.
"""

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from audit_skin_actions import arguments


CONDITION_TAGS = {"visible", "enable", "selected", "usealttexture", "start", "stop", "reset"}
MACRO = re.compile(r"\$(?:INFO|ESCINFO)\[", re.I)
ROOT = re.compile(r"^([a-z][a-z0-9_]*)\s*(?:\([^)]*\))?\s*\.", re.I)
ARITY = {
    "string.isempty": {1}, "string.isequal": {2}, "string.startswith": {2},
    "string.endswith": {2}, "string.contains": {2},
    **{"integer." + name: {2} for name in
       ["isequal", "isgreater", "isgreaterorequal", "isless", "islessorequal"]},
    "integer.iseven": {1}, "integer.isodd": {1}, "integer.valueof": {1},
    "skin.string": {1, 2}, "skin.numeric": {1}, "skin.hassetting": {1},
    "skin.hastheme": {1}, "skin.timerisrunning": {1}, "skin.timerelapsedsecs": {1},
    "control.hasfocus": {1}, "listitem.art": {1}, "listitem.property": {1},
    "window.property": {1}, "window.isactive": {1}, "window.isvisible": {1},
    "window.isdialogtopmost": {1}, "system.hasaddon": {1},
    "system.addonisenabled": {1}, "library.hascontent": {1}, "library.hasnode": {1},
}


def call_suffix(text, start):
    """Return an immediate argument list, or None if balancing is uncertain."""
    suffix = text[start:].lstrip()
    if not suffix.startswith("("):
        return ""
    depth, quote, escaped = 0, None, False
    for index, char in enumerate(suffix):
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return suffix[:index + 1]
    return None


def condition_atoms(text):
    """Split boolean atoms outside calls/brackets; not a Kodi parser."""
    text = text.strip()
    while text.startswith("!"):
        text = text[1:].strip()
    if not text:
        return []
    if text.startswith("["):
        depth, end = 0, None
        for index, char in enumerate(text):
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    end = index
                    break
        if end == len(text) - 1:
            return condition_atoms(text[1:-1])
    depth, square, quote, escaped, start = 0, 0, None, False, 0
    parts = []
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "[":
            square += 1
        elif char == "]":
            square -= 1
        elif char in "+|" and depth == square == 0:
            parts.append(text[start:index])
            start = index + 1
    if parts:
        parts.append(text[start:])
        return [atom for part in parts for atom in condition_atoms(part)]
    return [text]


def info_expressions(text):
    for match in MACRO.finditer(text):
        depth, index = 1, match.end()
        while index < len(text) and depth:
            if text[index] == "[":
                depth += 1
            elif text[index] == "]":
                depth -= 1
            index += 1
        if not depth:
            yield text[match.end():index - 1]


def audit(root, registry):
    names = {namespace: set(methods) for namespace, methods in registry["namespaces"].items()}
    # Lookahead permits the overlapping Container(...).ListItem(...).Property
    # reference to inspect both Container.ListItem and ListItem.Property names.
    pattern = re.compile(r"(?<![\w])(?=(" + "|".join(sorted(names, key=len, reverse=True)) +
                         r")(?:\([^)]*\))?\s*\.\s*([a-z][a-z0-9_]*))", re.I)
    references, candidates, unrecognized_roots = [], [], []
    arity_findings, arity_skipped, arity_checked = [], [], 0
    atom_count, atom_candidates, dynamic_atoms = 0, [], []
    files = sorted((root / "xml").glob("*.xml"))
    for path in files:
        for index, element in enumerate(ET.parse(path).getroot().iter()):
            values = []
            if element.tag in CONDITION_TAGS or element.tag == "info":
                values.append(("condition/info", element.text or ""))
            if element.get("condition"):
                values.append(("condition attribute", element.get("condition")))
            for value in [element.text or "", *element.attrib.values()]:
                for expression in info_expressions(value):
                    values.append(("info macro", expression))
            for kind, value in values:
                origin = {"file": path.relative_to(root).as_posix(), "element": element.tag,
                          "document_index": index, "kind": kind, "expression": value.strip()}
                if kind == "condition attribute" or (kind == "condition/info" and element.tag in CONDITION_TAGS):
                    for atom in condition_atoms(value):
                        if atom.startswith("$"):
                            dynamic_atoms.append({**origin, "atom": atom})
                            continue
                        if atom.lower() in {"true", "false", "yes", "no"}:
                            continue
                        atom_count += 1
                        first = re.match(r"([a-z][a-z0-9_]*)\s*(?:\(|\.)", atom, re.I)
                        if not first or first[1].lower() not in names:
                            atom_candidates.append({**origin, "atom": atom})
                if kind in {"info macro", "condition/info"} and (kind == "info macro" or element.tag == "info"):
                    match = ROOT.match(value.strip())
                    if match and match[1].lower() not in names:
                        unrecognized_roots.append({**origin, "root": match[1]})
                for match in pattern.finditer(value):
                    namespace, method = match[1].lower(), match[2].lower()
                    row = {**origin, "name": namespace + "." + method}
                    references.append(row)
                    if method not in names[namespace]:
                        candidates.append(row)
                    if row["name"] in ARITY:
                        suffix = call_suffix(value, match.end(2))
                        if suffix is None:
                            arity_skipped.append({**row, "reason": "unbalanced argument text"})
                        elif "$" in suffix:
                            arity_skipped.append({**row, "reason": "dynamic argument text"})
                        else:
                            params = arguments("Call" + suffix)
                            if params is None:
                                arity_skipped.append({**row, "reason": "arguments not parsed"})
                            else:
                                arity_checked += 1
                                if len(params) not in ARITY[row["name"]]:
                                    arity_findings.append({**row, "actual": len(params),
                                                           "expected": sorted(ARITY[row["name"]])})
    # The same expression can occur as both condition text and a nested macro.
    def unique(rows):
        seen, result = set(), []
        for row in rows:
            key = json.dumps(row, sort_keys=True)
            if key not in seen:
                result.append(row)
                seen.add(key)
        return result
    return {"source_ref": registry["source_ref"],
            "scope": "Literal method names in conditions/info expressions; selected static argument counts also checked. Candidates may be literal property keys/strings and require source review. No complete argument semantics, nested qualifier, provider-property, dynamic substitution or runtime validation.",
            "xml_files": len(files), "references": len(references),
            "distinct_names": sorted({row["name"] for row in references}),
            "candidates": unique(candidates), "unrecognized_info_roots": unique(unrecognized_roots),
            "arity_checked": arity_checked, "arity_candidates": unique(arity_findings),
            "arity_skipped": unique(arity_skipped),
            "condition_atom_count": atom_count, "condition_atom_candidates": unique(atom_candidates),
            "dynamic_condition_atoms": unique(dynamic_atoms)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skin_directory", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.skin_directory.resolve()
    registry = json.loads((root / "results/kodi22_inventory/kodi_info_registry.json").read_text(encoding="utf-8"))
    print(json.dumps(audit(root, registry), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
