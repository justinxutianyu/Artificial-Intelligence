#!/bin/sh
BNST_ROOT=$("${0%/*}/get-root.sh")
MAIN_CLASS="$1"
shift
$BNST_ROOT/src/main/scripts/get-version.sh
echo mvn -f "$BNST_ROOT/pom.xml" exec:java -Dexec.mainClass="$MAIN_CLASS" -Dexec.args="$*"
mvn -e -f "$BNST_ROOT/pom.xml" exec:java -Dexec.mainClass="$MAIN_CLASS" -Dexec.args="$*"
