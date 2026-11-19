"""Prints the Strike app's output for the test domains under CPython (compared with Pyodide in site-check.yml)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts')); sys.path.insert(0, os.path.join(HERE, '..', 'py')); sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import strike
for d in json.load(open(os.path.join(HERE, 'domains.json'), encoding='utf-8')):
    print(strike.strike(d))
