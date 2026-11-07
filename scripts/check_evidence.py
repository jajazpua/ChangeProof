#!/usr/bin/env python3
"""Offline checks for tracked evidence files and relative links.

Does not probe external URLs, validate link fragments, execute the private engine,
or assert runtime compatibility. Run from a Git checkout with Python 3.10+.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


def tracked_paths(root):
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return [name for name in result.stdout.decode("utf-8").split("\0") if name]


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON key: " + key)
        value[key] = item
    return value


def reject_constant(value):
    raise ValueError("Non-finite JSON constant: " + value)


def finite_float(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("JSON number exceeds finite float range: " + value)
    return parsed


def parse_json(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


class AssetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ("href", "src") and value)


def relative_link(source, target):
    parts = urlsplit(target.strip("<>"))
    if parts.scheme or parts.netloc or not parts.path:
        return None
    path = unquote(parts.path).replace("\\", "/")
    if path.startswith("/"):
        path = path[1:]
    else:
        path = posixpath.join(posixpath.dirname(source), path)
    normalized = posixpath.normpath(path)
    if normalized == ".." or normalized.startswith("../"):
        raise ValueError("Link escapes repository: " + target)
    return normalized


def markdown_inline_links(text):
    links = []
    for match in re.finditer(r"\]\(\s*", text):
        index = match.end()
        if index < len(text) and text[index] == "<":
            end = text.find(">", index + 1)
            if end >= 0:
                links.append(text[index + 1:end])
            continue
        start, depth = index, 0
        while index < len(text):
            char = text[index]
            if char.isspace() and depth == 0:
                break
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            index += 1
        if index > start:
            links.append(text[start:index])
    return links


def document_links(path, text):
    if path.endswith(".md"):
        # The repository uses inline Markdown links. Ignore fenced examples.
        text = re.sub(r"(?ms)^\s*(`{3,}|~{3,}).*?^\s*\1\s*$", "", text)
        links = markdown_inline_links(text)
    else:
        links = []
    parser = AssetLinks()
    parser.feed(text)
    links.extend(parser.links)
    return links


def check_repository(root, paths):
    root = root.resolve()
    known = set(paths)
    directories = {"."}
    for relative in paths:
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError("Unsafe tracked path: " + relative)
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Symlink or path escape: " + relative)
        directories.update(str(parent) for parent in pure.parents)
    counts = {"json": 0, "python": 0, "svg": 0, "relative_links": 0, "manifest_entries": 0}
    errors = []
    for relative in paths:
        path = root / relative
        suffix = path.suffix.lower()
        if suffix not in {".md", ".json", ".py", ".svg", ".html"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
            if suffix == ".json":
                value = parse_json(text)
                counts["json"] += 1
                if path.name == "SHA256SUMS.json":
                    if not isinstance(value, dict):
                        raise ValueError("Manifest must be an object")
                    if value.get("algorithm") != "SHA-256":
                        raise ValueError("Unsupported manifest algorithm")
                    key = "files" if "files" in value else "snapshots"
                    if key not in value or not isinstance(value[key], dict):
                        raise ValueError("Manifest entries must be an object")
                    folder = path.parent if key == "files" else path.parent / "snapshots"
                    for name, digest in value[key].items():
                        target = (folder / name).resolve()
                        if not target.is_relative_to(root):
                            raise ValueError("Manifest target escapes repository")
                        target_name = target.relative_to(root).as_posix()
                        if target_name not in known:
                            raise ValueError("Manifest target is not tracked: " + target_name)
                        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                            raise ValueError("Invalid SHA-256: " + name)
                        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                            raise ValueError("Hash mismatch: " + name)
                        counts["manifest_entries"] += 1
            elif suffix == ".py":
                ast.parse(text, filename=relative)
                counts["python"] += 1
            elif suffix == ".svg":
                ET.fromstring(text)
                counts["svg"] += 1
            if suffix in {".md", ".html", ".svg"}:
                for target in document_links(relative, text):
                    resolved = relative_link(relative, target)
                    if resolved is not None:
                        if resolved not in known and resolved not in directories:
                            raise ValueError("Missing relative link: " + target)
                        counts["relative_links"] += 1
        except (OSError, ValueError, KeyError, TypeError, SyntaxError, ET.ParseError) as error:
            errors.append({"file": relative, "reason": str(error)})
    return {"status": "FAIL" if errors else "PASS", "checks": counts, "errors": errors,
            "scope": "Tracked JSON, Python syntax, SVG XML, relative link paths and SHA-256 manifests",
            "not_checked": ["External URL availability", "Link fragments", "Runtime compatibility"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = check_repository(args.root, tracked_paths(args.root))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        result = {"status": "FAIL", "reason": str(error)}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
