#!/usr/bin/env python3
"""examples.py -- the practical examples of M322 Cymatic View (Companion Part 91), each computed.
    python3 records/cymatics/examples.py      # diffed in CI against examples_output.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import cymatics as cy
print(cy.fingerprint()); print()
print(cy.recipe(100)); print()
print(cy.modes()); print()
for q in ('What is consciousness?', 'What is grief?', 'How do I resolve this recurring conflict with my business partner?', 'What is the Human Condition?'):
    print(cy.strike(q)); print()
