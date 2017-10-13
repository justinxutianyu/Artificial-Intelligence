#!/bin/bash
SCRIPTPAR="${0%/*}"

$SCRIPTPAR/run-rule-inference.sh
if ( find ./sub-exp-??/training/optimized-rules/*.rule -quit ) ; then
        mv training/inferred-rules/ training/inferred-rules-no-merge/
        $SCRIPTPAR/merge-subs-with-main.sh
        ln -s inferred-rules-merged-subs training/inferred-rules
else
        echo "No pretrained sub-experiments found"
        exit 1;
fi
$SCRIPTPAR/merge-subs-with-main.sh
