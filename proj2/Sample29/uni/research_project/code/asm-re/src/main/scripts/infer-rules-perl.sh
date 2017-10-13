#!/bin/sh

BNST_ROOT=$("${0%/*}/get-root.sh")
SCRIPT_PATH="$(readlink -n -f $0)"

export PERL5LIB="$BNST_ROOT/src/main/perllib:$PERL5LIB"

cd training
"${SCRIPT_PATH%/*}/SDtoRules.pl"