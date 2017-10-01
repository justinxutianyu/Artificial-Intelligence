#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

SRC_DIR=./teams/PacManiaSearchAgents
DST_DIR=./build/PacManiaSearchAgents

rm -rf build
mkdir build
mkdir $DST_DIR
cp $SRC_DIR/* *.pddl *.pl $DST_DIR
rm -rf $DST_DIR/*.pyc $DST_DIR/problem*.pddl $DST_DIR/solution*.txt $DST_DIR/ff
cd ./build
zip ./PacManiaSearchAgents.zip ./PacManiaSearchAgents/*