#!/bin/sh
BNST_ROOT=$("${0%/*}/get-root.sh")

if [ -z $PARSER_CLASS ] ; then
    PARSER_CLASS="com.unimelb.biomed.extractor.textprocess.BnstDepPredict"
fi

$BNST_ROOT/src/main/scripts/write-version.sh

cd $BNST_ROOT
$BNST_ROOT/src/main/scripts/exec-class.sh $PARSER_CLASS $*
