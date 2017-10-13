#!/bin/bash
BNST_ROOT=$("${0%/*}/get-root.sh")
SCRIPT_PATH="$(readlink -n -f $0)"
SCRIPTPAR="${SCRIPT_PATH%/*}"
export PERL5LIB="$BNST_ROOT/src/main/perllib:$PERL5LIB"

if [[ $1 == '-n' ]] ; then
	WRITE_MAPS=""
else
	WRITE_MAPS="yes"
fi

if [ -z "$TEST" ] ; then
  echo "Variable TEST not set ; don't know where to read .a1 files from"
  exit 1;
fi

if [ $WRITE_MAPS ] ; then
	"$SCRIPTPAR/bnst-apply-rules.sh" --source-a1 "$TEST" --map-using-perl
fi
"$SCRIPTPAR/raw-matching-to-A2.pl"  
