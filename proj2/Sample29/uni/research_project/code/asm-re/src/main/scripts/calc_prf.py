#!/usr/bin/env python

from __future__ import division
import sys

def read_res_line(line):
    line = line.strip()
    if not line.strip():
        return None
    comps = line.split()
    try:
        kind, gold, answers, matches = comps
    except ValueError:
        return None
    gold = int(gold)
    answers = int(answers)
    matches = int(matches)
    return (kind, gold, answers, matches)

def get_kind_prf(line):
    comps = read_res_line(line)
    if comps:
        kind, gold, answers, matches = comps
        return (kind, Score(matches, answers, gold))
    else:
        return None

def show_prf(line):
    kind_prf = get_kind_prf(line)
    if kind_prf:
        kind, score = kind_prf
        print "%s\t& %0.2f & %0.2f & %0.2f" % (
            kind, 100 * score.precision, 100 * score.recall, 100 * score.fscore)

class Score(object):
    def __init__(self, matches, answers, gold):
        self.precision = precision(matches, answers)
        self.recall = recall(matches, gold)
        self.fscore = safe_fscore(self.precision, self.recall)


def precision(matches, answers):
    return matches / answers

def recall(matches, gold):
    return matches / gold

def safe_fscore(prec, rec):
    return fscore(prec, rec) if (prec or rec) else 0.0

def fscore(prec, rec):
    return 2.0 * prec * rec / (prec + rec)

def main():
    for line in sys.stdin:
        show_prf(line)
    
if __name__ == "__main__":
    main()
