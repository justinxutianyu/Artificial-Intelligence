#!/bin/sh
BNST_ROOT=$("${0%/*}/get-root.sh")

hg -R $BNST_ROOT par | head -n 1
hg -R $BNST_ROOT diff


