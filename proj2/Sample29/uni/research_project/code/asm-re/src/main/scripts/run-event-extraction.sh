#!/bin/bash
SCRIPTPAR="${0%/*}"

"$SCRIPTPAR/apply-rules.sh" --corpus "$ASM_CORPUS" --relation "$RELATION_TYPE" $LEARN_EXTRACT_OPTIM_ARGS $EXTRACT_OPTIM_ARGS "$TEST" 
