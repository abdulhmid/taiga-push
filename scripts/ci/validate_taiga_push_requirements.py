#!/usr/bin/env python3
"""Validate requirements/taiga-push.yml structure for CI checks (M2M auth)."""
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
    path = os.path.join(os.getcwd(), 'requirements', 'taiga-push.yml')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found")
        sys.exit(2)
    data = load_yaml(path)
    ok = True
    for key in REQUIRED_TOP:
        if key not in data:
            print(f"ERROR: Missing top-level key: {key}")
            ok = False
    if not isinstance(data.get('inputs'), dict):
        print("ERROR: 'inputs' must be a dict")
        ok = False
    # Check doc_input fields
    inputs = data.get('inputs', {}) or {}
    doc_input = inputs.get('doc_input', {}) or {}
    if 'path' not in doc_input or 'format' not in doc_input:
        print("ERROR: doc_input must include 'path' and 'format'")
        ok = False
    if doc_input.get('format') not in ['pdf', 'doc', 'docx']:
        print("ERROR: doc_input.format must be one of: pdf, doc, docx")
        ok = False
    # taiga hosting
    hosting = data.get('taiga_hosting', {}) or {}
    if hosting.get('hosting') != 'self-hosted':
        print("ERROR: taiga_hosting.hosting must be 'self-hosted'")
        ok = False
    # outputs check
    outputs = data.get('outputs', {}) or {}
    for k in ['created_tasks', 'failed_rows', 'audit_log']:
        if k not in outputs:
            print(f"ERROR: outputs missing '{k}'")
            ok = False
    # 5.4 constraint
    constraints = data.get('constraints', []) or []
    has_5_4 = any((isinstance(c, dict) and '5.4' in c) or (isinstance(c, str) and c.strip().startswith('5.4')) for c in constraints)
    if not has_5_4:
        print("WARNING: constraints do not include 5.4 detail; consider adding placeholder if API requires")
        ok = False

    if ok:
        print("OK: requirements/taiga-push.yml structure looks valid for CI preview.")
        sys.exit(0)
    else:
        print("Please adjust requirements/taiga-push.yml based on the above messages.")
        sys.exit(1)

if __name__ == '__main__':
    main()
