"""Offline regression tests for the fixture-scoped Immich source verifier."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

PATH = Path(__file__).resolve().parents[1] / "pilots" / "immich-28325" / "verify.py"
SPEC = importlib.util.spec_from_file_location("immich_public_verifier", PATH)
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def synthetic_documents():
    """Original tiny test data; no upstream source snapshot is distributed."""
    schemas = {
        "AudioCodec": {"description": "Test codec", "type": "string",
                       "enum": ["mp3", "aac", "libopus", "opus", "pcm_s16le"]},
        "SystemConfigDto": {"type": "object", "properties": {
            "ffmpeg": {"$ref": verifier.PREFIX + "SystemConfigFFmpegDto"}}},
        "SystemConfigFFmpegDto": {"type": "object", "properties": {
            "targetAudioCodec": {"$ref": verifier.PREFIX + "AudioCodec"},
            "acceptedAudioCodecs": {"type": "array", "items": {"$ref": verifier.PREFIX + "AudioCodec"}}}},
    }
    for index in range(45):
        name = "Synthetic" + str(index)
        schemas[name] = {"type": "string"}
        schemas["SystemConfigDto"]["properties"][name] = {"$ref": verifier.PREFIX + name}
    body = {"content": {"application/json": {"schema": {"$ref": verifier.PREFIX + "SystemConfigDto"}}}}
    operation = {"operationId": "updateConfig", "requestBody": copy.deepcopy(body),
                 "responses": {"200": copy.deepcopy(body)}, "security": [{"test": []}]}
    document = {"openapi": "3.0.0", "info": {"title": "Synthetic test", "version": "1"},
                "servers": [{"url": "/api"}], "paths": {"/system-config": {"put": operation}},
                "components": {"schemas": schemas, "securitySchemes": {"test": {"type": "http", "scheme": "bearer"}}}}
    for index in range(158):
        document["paths"]["/synthetic/" + str(index)] = {}
    after = copy.deepcopy(document)
    after["components"]["schemas"]["AudioCodec"]["enum"].remove("libopus")
    return document, after


class SourceTests(unittest.TestCase):
    def test_exact_byte_identities(self):
        raw = b'{"openapi":"test"}'
        pin = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
               "git_blob_sha1": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}
        with mock.patch.dict(verifier.PINS, {"test": pin}):
            self.assertEqual(verifier.decode_source(raw, "test"), {"openapi": "test"})
            with self.assertRaisesRegex(ValueError, "byte count"):
                verifier.decode_source(raw + b"\n", "test")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                verifier.decode_source(raw.replace(b"test", b"fail"), "test")

    def test_git_blob_identity_is_checked(self):
        raw = b"{}"
        pin = {"bytes": 2, "sha256": hashlib.sha256(raw).hexdigest(), "git_blob_sha1": "incorrect"}
        with mock.patch.dict(verifier.PINS, {"test": pin}):
            with self.assertRaisesRegex(ValueError, "Git blob"):
                verifier.decode_source(raw, "test")

    def test_fixed_public_download(self):
        with mock.patch.object(verifier, "urlopen", return_value=io.BytesIO(b"public")) as opened:
            self.assertEqual(verifier.read_source("before"), b"public")
            self.assertEqual(opened.call_args.args[0].full_url, verifier.source_url("before"))
            self.assertEqual(opened.call_args.kwargs["timeout"], 30)

    def test_download_size_limit(self):
        with mock.patch.object(verifier, "MAX_BYTES", 3), \
                mock.patch.object(verifier, "urlopen", return_value=io.BytesIO(b"large")):
            with self.assertRaisesRegex(ValueError, "size limit"):
                verifier.read_source("before")

    def test_local_mode_does_not_download(self):
        with mock.patch.object(Path, "open", return_value=io.BytesIO(b"local")), \
                mock.patch.object(verifier, "urlopen") as opened:
            self.assertEqual(verifier.read_source("before", Path("example.json")), b"local")
            opened.assert_not_called()

    def test_partial_local_arguments_are_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            verifier.main(["--before", "example.json"])
        self.assertEqual(error.exception.code, 2)

    def test_http_protocol_failure_is_nonzero(self):
        with mock.patch.object(verifier, "read_source", side_effect=verifier.HTTPException("invalid response")), \
                contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(verifier.main([]), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "FAIL")

    def test_fetch_failure_is_nonzero(self):
        with mock.patch.object(verifier, "read_source", side_effect=OSError("unavailable")), \
                contextlib.redirect_stderr(io.StringIO()) as output:
            self.assertEqual(verifier.main([]), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "FAIL")


class ContractTests(unittest.TestCase):
    def test_reference_cycle_terminates(self):
        schemas = {"A": {"$ref": verifier.PREFIX + "B"}, "B": {"$ref": verifier.PREFIX + "A"}}
        self.assertEqual(set(verifier.schema_closure({"$ref": verifier.PREFIX + "A"}, schemas)), {"A", "B"})

    def test_external_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "local component"):
            list(verifier.schema_refs({"$ref": "https://example.invalid/schema.json"}))

    def test_missing_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing referenced"):
            verifier.schema_closure({"$ref": verifier.PREFIX + "missing"}, {})

    def test_codec_fragment_is_narrow(self):
        schema = {"description": "test", "type": "string", "enum": ["opus"]}
        self.assertTrue(verifier.accepts_codec(schema, "opus"))
        self.assertFalse(verifier.accepts_codec(schema, "libopus"))
        self.assertFalse(verifier.accepts_codec(schema, 1))
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            verifier.accepts_codec({**schema, "pattern": ".*"}, "opus")

    def test_scope_and_witnesses(self):
        before, after = synthetic_documents()
        pins = {label: {"scope_sha256": verifier.canonical_scope_hash(verifier.endpoint_scope(doc))}
                for label, doc in (("before", before), ("after", after))}
        with mock.patch.dict(verifier.PINS, pins):
            result = verifier.verify_contracts(before, after)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["runtime_tested"])
        self.assertFalse(result["changeproof_engine_executed"])
        self.assertEqual(result["component_witnesses"][0], {"value": "libopus", "before": True, "after": False})

    def test_unrelated_change_is_rejected(self):
        before, after = synthetic_documents()
        after["info"]["version"] = "2"
        with self.assertRaisesRegex(ValueError, "Another parsed-document change"):
            verifier.verify_contracts(before, after)

    def test_wrong_scope_hash_is_rejected(self):
        before, after = synthetic_documents()
        with mock.patch.dict(verifier.PINS, {"before": {"scope_sha256": "incorrect"}}):
            with self.assertRaisesRegex(ValueError, "scope hash differs"):
                verifier.verify_contracts(before, after)

    def test_missing_reachable_schema_is_rejected(self):
        before, _ = synthetic_documents()
        del before["components"]["schemas"]["Synthetic0"]
        with self.assertRaisesRegex(ValueError, "Missing referenced"):
            verifier.endpoint_scope(before)

    def test_unexpected_enum_is_rejected(self):
        before, after = synthetic_documents()
        after["components"]["schemas"]["AudioCodec"]["enum"].append("new")
        with self.assertRaisesRegex(ValueError, "after enum"):
            verifier.verify_contracts(before, after)


if __name__ == "__main__":
    unittest.main()
