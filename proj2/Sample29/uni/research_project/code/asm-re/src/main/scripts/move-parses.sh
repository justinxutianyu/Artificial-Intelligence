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

#mv "$ORIGDIR"/*.parsed "$tgt"

for file in "$ORIGDIR"/*.parsed;
do
    cp $file "$tgt"
done
