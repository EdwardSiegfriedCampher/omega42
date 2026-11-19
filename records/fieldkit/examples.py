#!/usr/bin/env python3
"""examples.py -- the practical examples of M321 Field Kit (Companion Part 90), each computed, none invented.
Physical sequences marked ILLUSTRATIVE are made up to show the instrument's behaviour, not measured data.
    python3 records/fieldkit/examples.py      # diffed in CI against examples_output.txt"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import fieldkit as fk
def fib(n):
    a, b, o = 1, 1, []
    for _ in range(n): o.append(a); a, b = b, a + b
    return ', '.join(map(str, o))
EX = [
 ('C1 CAREER (cognitive)', fk.decide('I have to decide whether to leave this job', 'I expect to feel relieved within three months.')),
 ('C2 TEAM (cognitive)', fk.decide('Should we spend six months rebuilding the legacy system from scratch?', 'We expect the rebuild to ship in seven months.')),
 ('C3 CONFLICT, under F0-CF (cognitive)', fk.decide('How do I resolve this recurring conflict with my business partner?', frame='cf')),
 ('C4 STUDY (cognitive)', fk.decide('How can I learn enough calculus before the exam?')),
 ('F1 A FELT STATE, WITH YOUR OWN PROFILE (experiential)', fk.feel('I have to decide whether to leave this job', 'I feel anxious about leaving.', 'valence=-1, activation=2, orientation=-1, clarity=-1, relation=0', 'C3')),
 ('F2 THE SAME FEELING IN OTHER WORDS (experiential)', fk.feel('I have to decide whether to leave this job', 'Leaving scares me.')),
 ('P1 SUNFLOWER PARASTICHY COUNTS, the Fibonacci numbers (physical)', fk.detect('1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89', source='spiral counts (parastichies) of sunflower heads, a count with no unit, counted along each spiral family, used as counted')),
 ('P2 A LUCAS-NUMBERED SPIRAL FAMILY (physical)', fk.detect('2, 1, 3, 4, 7, 11, 18, 29, 47, 76', source='spiral counts of a plant whose spirals follow the Lucas numbers, a count with no unit, used as counted')),
 ('P3 FIBONACCI COUNTS WITH TWO MISCOUNTS, ILLUSTRATIVE (physical)', fk.detect('1, 1, 2, 3, 5, 8, 13, 22, 34, 56, 89', source='ILLUSTRATIVE: spiral counts with two miscounts, as a hurried observer might record them')),
 ('P4 HOURLY SENSOR COUNTS, ILLUSTRATIVE (physical)', fk.detect('12, 15, 11, 14, 13, 16, 12, 15, 14, 13, 12, 16', source='ILLUSTRATIVE: events per hour from a door sensor, a count per hour, logged automatically, used as counted')),
 ('P5 A LONG FIBONACCI RECORD, 30 TERMS (physical)', fk.detect(fib(30), source='a generation-by-generation count that follows the Fibonacci rule exactly, 30 generations, used as counted')),
 ('R1 AN 08:00 COMMITMENT (rhythm)', fk.rhythm('08:00')),
]
for title, out in EX: print('##### %s' % title); print(out); print()
