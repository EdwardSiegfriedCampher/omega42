#!/usr/bin/env python3
"""examples.py -- M323 Arithmetic Statement Check on the statements examined in Companion Parts 93, 95, 96 and 97.
    python3 records/claimcheck/examples.py      # diffed in CI against examples_output.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import claimcheck as cc
for out in (cc.identity('1*1=2'), cc.identity('1+1=2'), cc.identity('3*3=0'), cc.sqrt(2), cc.roots(), cc.zero(), cc.pythagoras(3, 4), cc.polygons(), cc.operation(), cc.collapse(), cc.ring(), cc.faces(6, 5)):
    print(out); print()
