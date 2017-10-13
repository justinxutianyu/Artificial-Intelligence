#!/bin/bash
SCRIPTPAR="${0%/*}"

"$SCRIPTPAR/infer-rules.sh" --corpus "$ASM_CORPUS" --relation "$RELATION_TYPE" $LEARN_EXTRACT_OPTIM_ARGS "$TRAINING"
