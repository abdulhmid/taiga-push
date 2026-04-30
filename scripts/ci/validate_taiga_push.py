#!/usr/bin/env python3
"""Validate taiga-push.yml structure for CI checks."""
import sys
import json
import os
try:
    import yaml
except Exception:
    print("PyYAML is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyyaml'])
    import yaml

REQUIRED_TOP = [
    'name', 'description', 'version', 'inputs', 'taiga_hosting', 'outputs', 'iso_compliance', 'constraints', 'status'
]

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    path = os.path.join(os.getcwd(), 'taiga-push.yml')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        sys.exit(2)
    data = load_yaml(path)
    ok = True
    for key in REQUIRED_TOP:
        if key not in data:
            print(f"ERROR: Missing top-level key: {key}")
            ok = False
    # Basic input checks
    inputs = data.get('inputs', {}) or {}
    doc_input = inputs.get('doc_input', {}) or {}
    if 'path' not in doc_input or 'format' not in doc_input:
        print("WARNING: doc_input should contain 'path' and 'format'.")
        ok = False
    # Validate format
    if 'format' in doc_input:
        if doc_input['format'] not in ['pdf', 'doc', 'docx']:
            print("WARNING: doc_input.format should be one of: pdf, doc, docx.")
            ok = False
    # Taiga hosting
    hosting = data.get('taiga_hosting', {}) or {}
    if hosting.get('hosting') != 'self-hosted':
        print("WARNING: taiga_hosting.hosting should be 'self-hosted'.")
        ok = False
    # Outputs
    outputs = data.get('outputs', {}) or {}
    for k in ['created_tasks', 'failed_rows', 'audit_log']:
        if k not in outputs:
            print(f"WARNING: outputs should include '{k}'.")
            ok = False
    # Constraints 5.4 presence
    constraints = data.get('constraints', []) or []
    has_5_4 = False
    for c in constraints:
        if isinstance(c, dict) and '5.4' in c:
            has_5_4 = True
        if isinstance(c, str) and c.strip().startswith('5.4'):
            has_5_4 = True
    if not has_5_4:
        print("WARNING: constraints does not contain 5.4 detail.")
        ok = False

    if ok:
        print("OK: taiga-push.yml structure looks valid for CI preview.")
        sys.exit(0)
    else:
        print("Please adjust taiga-push.yml based on the above messages.")
        sys.exit(1)

if __name__ == '__main__':
    main()
