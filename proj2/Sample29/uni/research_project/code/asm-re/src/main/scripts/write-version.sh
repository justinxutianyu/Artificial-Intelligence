#!/bin/sh
BNST_ROOT=$("${0%/*}/get-root.sh")

hg -R $BNST_ROOT tip | head -n 1 > ./bnst13-code-version


