# Evidence checks

The [Evidence checks workflow](../.github/workflows/evidence.yml) runs on pushes to `main`, pull requests targeting `main`, and manual dispatch. It has read-only repository permissions, no deployment or publishing steps, and does not use private ChangeProof code or credentials.

## What it checks

- Tracked JSON parses, without duplicate keys or non-finite values.
- Tracked Python files parse and the SVG preview is well-formed XML.
- Inline Markdown and HTML relative link paths point to tracked files or directories.
- Existing Denkeeper and ShenYu SHA-256 manifests match their files.
- Independent checker regression tests pass.
- Existing Denkeeper and ShenYu synthetic fixture verifiers pass.
- The independent Immich verifier fetches and verifies the two pinned public source files.

**Limits:** relative-link checking does not probe external websites, validate URL fragments, or handle every possible Markdown extension. Passing checks do not prove runtime compatibility, endorse upstream projects, or reproduce the proprietary engine. An upstream download failure fails the Immich step rather than claiming a successful source check.

The workflow pins its official GitHub Actions by commit and installs `jsonschema==4.25.1` for the existing synthetic fixture checks. Dependency installation and the Immich source download use the network; the repository checker, unit tests and synthetic fixture verification are offline.

## Run locally

Use Python 3.10 or newer from a Git checkout. CI uses Python 3.12. To avoid changing another project environment, create a virtual environment first.

```bash
python -m venv .venv
.venv/bin/python -m pip install "jsonschema==4.25.1"
.venv/bin/python -B scripts/check_evidence.py
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B pilots/denkeeper-583/verify.py
.venv/bin/python -B pilots/shenyu-7935/verify_fixture.py
.venv/bin/python -B pilots/immich-28325/verify.py
```

On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`. The repository checker reads Git's tracked-file list, so a newly created file must be staged before it is included. The Immich [case README](../pilots/immich-28325/README.md#reproduce-the-public-source-checks) also documents a network-free run with your own exact source files.

Tracked text uses LF line endings through [Git attributes](../.gitattributes), preserving evidence byte hashes on Windows as well as Linux and macOS.

Historical fixture files and their manifests are preserved. A legitimate future change to a hashed fixture should update its manifest and explain why; never update hashes merely to conceal an unexpected mismatch.
