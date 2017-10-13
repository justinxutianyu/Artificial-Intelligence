#!/bin/sh
SCRIPT_PATH="$(readlink -n -f $0)"
echo ${SCRIPT_PATH%/*}/../../..
