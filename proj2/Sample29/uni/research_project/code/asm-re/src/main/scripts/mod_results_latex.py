#!/usr/bin/env python

from os import path
import os
import subprocess

import calc_prf

param_maps = {
    '--stanford-cc-prop': r'\ccprop',
    '--generalize-pos': r'\coarsetrigpos',
    '--gen-pos-for-kind': r'\coarsetrigpos',
    '--discard-pos': r'\disctrigpos',
    '--disc-pos-for-kind': r'\disctrigpos',
    '--conf-cues-for-kind': r'\confcues',
    '--make-theme-rules-for-kind': r'\themerules',
}


KINDS = ('Negation', 'Speculation')

def read_env_vars(var_matcher, filename):
    command = ['bash', '-c', 'source "%s" && env' % filename]
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    var_values = {}
    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        if var_matcher(key)
            var_values[key] = value
    return values

def remap_env_params(filename):
    var_values = read_env_vars(lambda x: x.startswith('MOD_') && x.endswith('_ARGS'), filename)
    for value in var_values.itervalues():
        flags = [e for e in value.split(" ") if e.startswith('--')]
        for fl in flags:
            yield param_maps.get(fl, fl)

def print_result_line(dirname):
    resfname = path.join(dirname, 'test', 'RESULTS')
    print " \t & \\multicol{3}{c}{Negation} & \\multicol{3}{c}{Speculation} \\\\"
    print " \t &  P & R & F & P & R & F \\\\"
    with open(resfname) as f:
        kinds_scores = [calc_prf.read_res_line(line) for line in f]
        valid_kinds_scores = [v for v in kinds_scores if v]
        relev_kinds_scores = dict([(kind, score) 
            for (kind, score) in valid_kinds_scores 
            if kind in KINDS])
        params = list(remap_env_params(path.join(dirname, 'config_vars')))
        scores = []
        for kind in KINDS:
            score = relev_kinds_scores[kind]
            scores.append(score.precision, score.recall, score.fscore)
        print "%    " + dirname
        print "%s\t& " + " & ".join("%0.1f" for s in scores)

def main():
    for dirname in sys.argv:
        print_result_line(dirname)
    
if __name__ == "__main__":
    main()
