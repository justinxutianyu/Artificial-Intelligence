#!/bin/bash
SCRIPTPAR="${0%/*}"

$SCRIPTPAR/merge-rule-dirs.sh -o training/inferred-rules-merged-subs \
        ./sub-exp-??/training/optimized-rules \
        training/inferred-rules-no-merge
