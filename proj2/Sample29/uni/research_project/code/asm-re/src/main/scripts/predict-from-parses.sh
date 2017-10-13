#!/bin/sh
DIR="$(pwd)"
SCRIPTPAR="${0%/*}"

if [ -z "$TEST" ] ; then
  echo "Variable TEST not set ; don't know where to read .a1 files from"
  exit 1;
fi

"$SCRIPTPAR/bnst-apply-rules.sh" --source-a1 "$TEST"  
  
