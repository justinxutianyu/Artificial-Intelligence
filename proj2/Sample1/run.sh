#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

python capture.py -b PacManiaSearchAgents -r PacManiaSearchAgentsv2 -q -n 100
