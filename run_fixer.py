#!/usr/bin/env python3
from fix_any_pipeline import fix_my_pipeline
import sys

if len(sys.argv) > 1:
    filename = sys.argv[1]
    fix_my_pipeline(filename)
else:
    print("Usage: python run_fixer.py <workflow.yml>")
    print("Available files:")
    import os
    for f in os.listdir('.'):
        if f.endswith('.yml'):
            print(f"  {f}")