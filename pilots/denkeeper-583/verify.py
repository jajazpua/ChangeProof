#!/usr/bin/env python3
"""Independent, offline verifier for the synthetic Denkeeper #583 MCP fixture.

Does not import ChangeProof, contact Denkeeper or invoke an MCP tool.
Requires jsonschema >=4, <5 to check the specific input/output witnesses.
"""
from pathlib import Path
from hashlib import sha256
import json
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
S=HERE/'snapshots'
FILES={
    'description_only':'description_only.after.tools-list.json',
    'annotation_only':'annotation_only.after.tools-list.json',
    'input_required_only':'input_required_only.after.tools-list.json',
    'output_enum_only':'output_enum_only.after.tools-list.json',
    'combined':'combined.after.tools-list.json',
    'key_order_only':'key_order_only.after.tools-list.json',
}
EXPECTED={
    'description_only':(True,False,False,False,True),
    'annotation_only':(False,False,False,True,True),
    'input_required_only':(False,True,False,False,True),
    'output_enum_only':(False,False,True,False,False),
    'combined':(True,True,True,True,True),
    'key_order_only':(False,False,False,False,False),
}

def read(name):
    obj=json.loads((S/name).read_text('utf-8'))
    assert isinstance(obj['tools'],list) and len(obj['tools'])==1
    t=obj['tools'][0]
    assert t['name']=='note_update'
    for schema in ['inputSchema','outputSchema']:
        Draft202012Validator.check_schema(t[schema])
    return t

def digest(obj):
    # Stable for THESE ASCII-only examples; not RFC 8785.
    canonical=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    return sha256(canonical.encode('utf-8')).hexdigest()

def proposed_pin(t):
    # Projection explicitly proposed in Denkeeper issue #583; outputSchema is excluded.
    return {k:t[k] for k in ('name','description','inputSchema','annotations')}

def check_witness(name, old_schema, new_schema, value, old_accepts, new_accepts):
    old=Draft202012Validator(old_schema).is_valid(value)
    new=Draft202012Validator(new_schema).is_valid(value)
    assert (old,new)==(old_accepts,new_accepts),(name,old,new)
    return {'name':name,'sample':value,'old_accepts':old,'new_accepts':new}

def run():
    manifest=json.loads((HERE/'SHA256SUMS.json').read_text('utf-8'))['snapshots']
    for filename,expected_hash in manifest.items():
        actual=sha256((S/filename).read_bytes()).hexdigest()
        assert actual==expected_hash, f'SHA-256 mismatch: {filename}'
    before=read('before.tools-list.json')
    findings={}
    for label,filename in FILES.items():
        after=read(filename)
        observed=(
            before['description']!=after['description'],
            before['inputSchema']!=after['inputSchema'],
            before['outputSchema']!=after['outputSchema'],
            before['annotations']!=after['annotations'],
            digest(proposed_pin(before))!=digest(proposed_pin(after)),
        )
        assert observed==EXPECTED[label], (label,observed,EXPECTED[label])
        findings[label]={
            'description_changed':observed[0],
            'input_schema_changed':observed[1],
            'output_schema_changed':observed[2],
            'annotations_changed':observed[3],
            'proposed_pin_changes':observed[4],
            'tool_name_unchanged':before['name']==after['name'],
        }
    after=read(FILES['combined'])
    witnesses=[
        check_witness('old input rejected by new required field',before['inputSchema'],after['inputSchema'],{'note_id':'N-1'},True,False),
        check_witness('new input accepted by old open schema',before['inputSchema'],after['inputSchema'],{'note_id':'N-1','approval_code':'okay'},True,True),
        check_witness('new output enum rejected by strict old schema',before['outputSchema'],after['outputSchema'],{'status':'queued'},False,True),
        check_witness('old output accepted by new schema',before['outputSchema'],after['outputSchema'],{'status':'updated'},True,True),
    ]
    assert before['annotations']['readOnlyHint'] is False
    assert read(FILES['annotation_only'])['annotations']['readOnlyHint'] is True
    assert (S/'before.tools-list.json').read_bytes()!=(S/FILES['key_order_only']).read_bytes()
    assert digest(before)==digest(read(FILES['key_order_only']))
    return {
        'title':'Denkeeper #583 independent synthetic MCP descriptor-drift fixture',
        'scope':'offline synthetic tools/list structural test, not Denkeeper integration and not ChangeProof engine execution',
        'scenario_count':len(findings),
        'checks_passed':len(manifest)+len(findings)*5+len(witnesses)+3,
        'cases':findings,
        'witnesses':witnesses,
        'notes':[
            'A proposed digest that excludes outputSchema does not detect output-only drift.',
            'Tool name is unchanged in every scenario.',
            'readOnlyHint is untrusted descriptive metadata, not actual permission enforcement.',
            'Stable sorted-key JSON hashing is only a fixture control, not RFC 8785 canonicalization.',
            'No Denkeeper registration, probe, audit emission, operator re-pin, or runtime execution tested.',
        ],
    }

if __name__=='__main__':
    result=run()
    print(json.dumps(result,indent=2,ensure_ascii=False))
