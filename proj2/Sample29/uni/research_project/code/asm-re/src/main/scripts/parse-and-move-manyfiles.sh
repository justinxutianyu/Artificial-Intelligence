#!/bin/bash
DIR="$(pwd)"
SCRIPTPAR="${0%/*}"

if [ "${TRAINING:0:1}" != '/' ] ; then
	TRAINING="$DIR/$TRAINING"
fi

"$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TRAINING"  -ie \.txt -m "$MODEL" $PARSER_EXTRA_ARGS
"$SCRIPTPAR/move-parses-manyfiles.sh" "$TRAINING" "$DIR/training"

if [ -n "$AUX_MODEL_01" ] ; then
    "$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TRAINING"  -ie \.txt -m "$AUX_MODEL_01" $PARSER_EXTRA_ARGS
    "$SCRIPTPAR/move-parses-manyfiles.sh" "$TRAINING" "$DIR/training" .variant-001
fi    

if [ -n "$TEST" ] ; then
    "$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TEST"  -ie \.txt -m "$MODEL" $PARSER_EXTRA_ARGS
    "$SCRIPTPAR/move-parses-manyfiles.sh" "$TEST" "$DIR/test"
fi

if [ -n "$TUNING" ] ; then
    if [ "$TUNING" != "$TRAIN" ] ; then
        "$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TUNING"  -ie \.txt -m "$MODEL" $PARSER_EXTRA_ARGS
        "$SCRIPTPAR/move-parses-manyfiles.sh" "$TUNING" "$DIR/tuning"
    else 
        cp -r train tuning
    fi
fi

