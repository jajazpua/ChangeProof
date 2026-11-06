#!/usr/bin/env python3
"""Read-only verifier for ChangeProof's source evidence on Playwright MCP #1828.

Without arguments checks manifest integrity only. With a path, checks pinned
source lines in an upstream microsoft/playwright git checkout.
This does not exercise Zod, MCP, browser tools or the ChangeProof engine.
"""
from pathlib import Path
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'evidence.json').read_text(encoding='utf-8'))
assert len(data['pinned_commit'])==40
assert data['runtime_execution'] is False and data['changeproof_engine_executed'] is False
ids=set()
for f in data['findings']:
    assert f['id'] not in ids, f['id']
    ids.add(f['id'])
    assert f['match'] and f['line']>0
    assert f['source_path'].startswith('packages/playwright-core/src/tools/')
    assert f['source_url'].endswith('#L'+str(f['line']))
print(f'Evidence metadata: PASS ({len(ids)} source anchors)')
if len(sys.argv)==1:
    print('Upstream source checks NOT run; provide a pinned checkout path.')
    sys.exit(0)
root=Path(sys.argv[1]).resolve()
try:
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
except (OSError,subprocess.CalledProcessError):
    sys.exit('ERROR: unreadable Git checkout')
if commit!=data['pinned_commit']:
    sys.exit('ERROR: checkout commit differs from pinned revision')
fail=[]
for f in data['findings']:
    try:
        line=(root/f['source_path']).read_text(encoding='utf-8').splitlines()[f['line']-1]
        ok=f['match'] in line
    except (OSError,IndexError):
        ok=False
    print(('PASS' if ok else 'FAIL')+' '+f['id']+' '+f['target'])
    if not ok: fail.append(f['id'])
if fail:
    sys.exit('FAIL: '+','.join(fail))
print('PASS: all pinned source lines matched. No runtime behavior tested.')
