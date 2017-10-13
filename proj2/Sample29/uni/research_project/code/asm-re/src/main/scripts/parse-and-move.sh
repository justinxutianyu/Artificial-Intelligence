#!/bin/bash
DIR="$(pwd)"
SCRIPTPAR="${0%/*}"

if [ "${TRAINING:0:1}" != '/' ] ; then
	TRAINING="$DIR/$TRAINING"
fi
if [ "${TUNING:0:1}" != '/' ] ; then
	TUNING="$DIR/$TUNING"
fi

"$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TRAINING"  -ie \.txt -m "$MODEL" -corpus "$ASM_CORPUS" $PARSER_EXTRA_ARGS
"$SCRIPTPAR/move-parses.sh" "$TRAINING" "$DIR/training"

if [ -n "$AUX_MODEL_01" ] ; then
    "$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TRAINING"  -ie \.txt -m "$AUX_MODEL_01" -corpus "$ASM_CORPUS" $PARSER_EXTRA_ARGS
    "$SCRIPTPAR/move-parses.sh" "$TRAINING" "$DIR/training" .variant-001
fi

if [ -n "$TEST" ] ; then
    "$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TEST"  -ie \.txt -m "$MODEL" -corpus "$ASM_CORPUS" $PARSER_EXTRA_ARGS
    "$SCRIPTPAR/move-parses.sh" "$TEST" "$DIR/test"
fi

if [ -n "$TUNING" ] ; then
    if [ "$TUNING" != "$TRAINING" ] ; then
        "$SCRIPTPAR/bnst-parse.sh" -c "$CONFIG" -i "$TUNING"  -ie \.txt -m "$MODEL" -corpus "$ASM_CORPUS" $PARSER_EXTRA_ARGS
        "$SCRIPTPAR/move-parses.sh" "$TUNING" "$DIR/tuning"
    else
		rm -rf tuning/parse
		if [ ! -d tuning ]; then
			mkdir tuning
		fi
        cp -r training/parse tuning/parse
    fi
fi
