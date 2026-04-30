#!/usr/bin/env python3
"""Dry-run validator for taiga-push.yml without hitting external APIs."""
import os
import sys
import json

def main():
    path = os.path.join(os.getcwd(), 'taiga-push.yml')
    if not os.path.exists(path):
        print("ERROR: taiga-push.yml not found for dry-run.")
        sys.exit(2)
    # Basic presence checks for demo
    with open(path, 'r') as f:
        content = f.read()
    # Very lightweight checks: ensure essential sections exist
    essential = ['name:', 'description:', 'inputs:', 'taiga_hosting:', 'outputs:']
    ok = all(e in content for e in essential)
    if ok:
        print("Dry-run OK: taiga-push.yml appears to contain required sections.")
        sys.exit(0)
    else:
        print("Dry-run FAIL: taiga-push.yml is missing some essential sections.")
        sys.exit(1)

if __name__ == '__main__':
    main()
