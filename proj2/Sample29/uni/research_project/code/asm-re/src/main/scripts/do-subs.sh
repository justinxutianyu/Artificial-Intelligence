#!/bin/bash
dir=$(pwd)

for subexp in ./sub-exp-?? ; do
        cd $subexp;
        ./parse.sh && ./infer-rules.sh && ./optim-rules.sh
        cd $dir
done

