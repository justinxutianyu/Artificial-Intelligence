#!/bin/sh
ORIGDIR=$1
SUBDIR=$2
SUFFIX=$3

if [ -z $SUBDIR ] ; then
	echo "Usage: move-parses.sh orig-dir sub-dir";
	exit 1;
fi

tgt="$SUBDIR/parse$SUFFIX"
if [ ! -e "$tgt" ] ; then
	mkdir -p "$tgt"
fi

echo mv "$ORIGDIR/*.parsed" "$tgt"

mv "$ORIGDIR"/1*.parsed "$tgt"
mv "$ORIGDIR"/[0-9]*.parsed "$tgt"