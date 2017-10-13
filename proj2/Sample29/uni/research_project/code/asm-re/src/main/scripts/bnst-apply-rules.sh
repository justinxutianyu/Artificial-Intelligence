#!/bin/sh

BNST_ROOT=$("${0%/*}/get-root.sh")

mvn -f "$BNST_ROOT/pom.xml" exec:java -Dexec.mainClass=com.nicta.biomed.bnst13.RuleApply -Dexec.args="$*"
