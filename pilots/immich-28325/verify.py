#!/usr/bin/env python3
"""Verify the public Immich #28325 contract facts, not the ChangeProof engine.

Python 3.10+, standard library only. Default: fetch two pinned public files into
memory. Supplying both --before and --after uses local files without networking.
No source snapshots, credentials, application calls, or output files are created.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
from http.client import HTTPException
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

SOURCE_PATH = "open-api/immich-openapi-specs.json"
MAX_BYTES = 2_000_000
PINS = {
    "before": {
        "revision": "eea820fa2f441953bf363179bb18394dbd56b713",
        "bytes": 720431,
        "sha256": "e3f002f2e5b553526739a35e96a121a3796b7a30fd88ce7504f2970a36ae640a",
        "git_blob_sha1": "960d90d91c483685bda027ccddf1cfbed6efee9b",
        "scope_sha256": "8db5f944bb900caf34a123f7711d81e818c771e6adfe544f766f9c667be1ee4c",
    },
    "after": {
        "revision": "d788169bf3333cb5f075482c4eb66ee16c262e16",
        "bytes": 720410,
        "sha256": "b6d53c37b0d70ed859936316173e4987da5fc160027d83edb703e0bfa02d8c51",
        "git_blob_sha1": "c2eb88fb8b5a4b48bec61bd7318ce385240a2fc8",
        "scope_sha256": "174b6c190b33caadf7f64b0c461865167fb960fce01631514a978f3a85b69a7f",
    },
}
PREFIX = "#/components/schemas/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_url(label):
    return ("https://raw.githubusercontent.com/immich-app/immich/"
            + PINS[label]["revision"] + "/" + SOURCE_PATH)


def read_source(label, local_path=None):
    if local_path is not None:
        with Path(local_path).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    else:
        request = Request(source_url(label), headers={"User-Agent": "ChangeProof-public-source-verifier"})
        with urlopen(request, timeout=30) as response:
            raw = response.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, label + ": source exceeds size limit")
    return raw


def decode_source(raw, label):
    pin = PINS[label]
    require(len(raw) == pin["bytes"], label + ": source byte count differs")
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], label + ": SHA-256 differs")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(blob == pin["git_blob_sha1"], label + ": Git blob identity differs")
    document = json.loads(raw)
    require(isinstance(document, dict), label + ": expected an OpenAPI object")
    return document


def schema_refs(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref":
                require(isinstance(value, str) and value.startswith(PREFIX),
                        "Only local component-schema references are supported")
                name = value[len(PREFIX):]
                require(bool(name) and "/" not in name and "~" not in name,
                        "Unexpected component reference syntax")
                yield name
            else:
                yield from schema_refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from schema_refs(value)


def schema_closure(operation, schemas):
    pending = list(schema_refs(operation))
    selected = {}
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        require(name in schemas, "Missing referenced schema: " + name)
        selected[name] = schemas[name]
        pending.extend(schema_refs(selected[name]))
    return selected


def endpoint_scope(document):
    require(document["openapi"] == "3.0.0", "Unexpected OpenAPI version")
    require(len(document["paths"]) == 159, "Unexpected full-document path count")
    require(document["servers"] == [{"url": "/api"}], "Unexpected API base")
    operation = document["paths"]["/system-config"]["put"]
    require(operation["operationId"] == "updateConfig", "Unexpected operation")
    selected = schema_closure(operation, document["components"]["schemas"])
    require(len(selected) == 48, "Expected exactly 48 reachable schemas")
    for schema in (
        operation["requestBody"]["content"]["application/json"]["schema"],
        operation["responses"]["200"]["content"]["application/json"]["schema"],
    ):
        require(schema == {"$ref": PREFIX + "SystemConfigDto"}, "Unexpected body model")
    props = selected["SystemConfigDto"]["properties"]
    require(props["ffmpeg"] == {"$ref": PREFIX + "SystemConfigFFmpegDto"},
            "Unexpected ffmpeg model")
    ffmpeg = selected["SystemConfigFFmpegDto"]["properties"]
    require(ffmpeg["targetAudioCodec"] == {"$ref": PREFIX + "AudioCodec"},
            "Unexpected targetAudioCodec reference")
    accepted = ffmpeg["acceptedAudioCodecs"]
    require(accepted["type"] == "array" and accepted["items"] == {"$ref": PREFIX + "AudioCodec"},
            "Unexpected acceptedAudioCodecs item model")
    security = document["components"]["securitySchemes"]
    require(all(name in security for choice in operation["security"] for name in choice),
            "Missing security definition")
    result = {key: document[key] for key in ("openapi", "info", "servers") if key in document}
    result["paths"] = {"/system-config": {"put": operation}}
    result["components"] = {"schemas": selected, "securitySchemes": security}
    if "tags" in document:
        result["tags"] = [tag for tag in document["tags"] if tag["name"] in operation.get("tags", [])]
    return result


def canonical_scope_hash(scope):
    # Matches the recorded report serialization, not RFC 8785 canonicalization.
    text = json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def accepts_codec(schema, value):
    # Deliberately limited to this simple fragment; not a general JSON Schema validator.
    require(set(schema) == {"description", "enum", "type"} and schema["type"] == "string",
            "Unsupported codec schema shape")
    require(isinstance(schema["enum"], list) and all(isinstance(v, str) for v in schema["enum"]),
            "Expected a string enum")
    return isinstance(value, str) and value in schema["enum"]


def verify_contracts(before, after):
    old_codec = before["components"]["schemas"]["AudioCodec"]
    new_codec = after["components"]["schemas"]["AudioCodec"]
    require(old_codec["enum"] == ["mp3", "aac", "libopus", "opus", "pcm_s16le"],
            "Unexpected before enum")
    require(new_codec["enum"] == ["mp3", "aac", "opus", "pcm_s16le"],
            "Unexpected after enum")
    expected = copy.deepcopy(before)
    expected["components"]["schemas"]["AudioCodec"]["enum"].remove("libopus")
    require(expected == after, "Another parsed-document change exists")
    scopes = {}
    for label, document in (("before", before), ("after", after)):
        scope = endpoint_scope(document)
        digest = canonical_scope_hash(scope)
        require(digest == PINS[label]["scope_sha256"], label + ": reconstructed scope hash differs")
        scopes[label] = digest
    witnesses = [
        {"value": value, "before": accepts_codec(old_codec, value), "after": accepts_codec(new_codec, value)}
        for value in ("libopus", "opus")
    ]
    require(witnesses == [
        {"value": "libopus", "before": True, "after": False},
        {"value": "opus", "before": True, "after": True},
    ], "Unexpected component witness")
    return {
        "status": "PASS",
        "scope": "Public source facts for PUT /api/system-config and 48 referenced schemas",
        "only_document_change": "AudioCodec.enum removes libopus",
        "request_locations": ["ffmpeg.targetAudioCodec", "ffmpeg.acceptedAudioCodecs[]"],
        "component_witnesses": witnesses,
        "reconstructed_scope_sha256": scopes,
        "changeproof_engine_executed": False,
        "runtime_tested": False,
        "limits": [
            "Component witnesses are not complete HTTP requests.",
            "This does not reproduce engine findings, CLI exit codes, SARIF or the identical-input control.",
            "Hash identities are not signatures or proof of upstream authenticity.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, help="Exact pinned before file; requires --after")
    parser.add_argument("--after", type=Path, help="Exact pinned after file; requires --before")
    args = parser.parse_args(argv)
    if (args.before is None) != (args.after is None):
        parser.error("--before and --after must be supplied together")
    try:
        documents = {
            label: decode_source(read_source(label, getattr(args, label)), label)
            for label in ("before", "after")
        }
        result = verify_contracts(documents["before"], documents["after"])
        result["input_mode"] = "local-files" if args.before is not None else "pinned-public-downloads"
        result["sources"] = {
            label: {"url": source_url(label), "sha256": PINS[label]["sha256"]}
            for label in ("before", "after")
        }
    except (OSError, HTTPException, ValueError, KeyError, TypeError, RecursionError) as error:
        print(json.dumps({"status": "FAIL", "reason": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
