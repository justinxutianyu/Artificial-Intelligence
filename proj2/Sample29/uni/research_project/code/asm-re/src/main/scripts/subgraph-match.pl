#!/usr/bin/perl -w
# Usage: ./subgraph-match.pl script_dir train optim test
# Example: ./subgraph-match.pl /home/davidm/bnst13/src/main/scripts /home/davidm/BioNLP2013-Data/Data/BioNLP-ST-2013_GE_train_data_rev3 /home/davidm/BioNLP2013-Data/Data/BioNLP-ST-2013_GE_train_data_rev3 /home/davidm/BioNLP2013-Data/Data/BioNLP-ST-2013_GE_devel_data_rev3

use strict;

if (not defined $ARGV[3]) {
    die "Usage: ./subgraph-match.pl script_dir train optim test";}

my $scr_dir = $ARGV[0];

$ENV{'TRAINING'}= $ARGV[1];
$ENV{'TUNING'}= $ARGV[2];
$ENV{'TEST'}= $ARGV[3];

$ENV{'ASM_CORPUS'}=$ARGV[4];
$ENV{'RELATION_TYPE'}=$ARGV[5];

$ENV{'EXTRACT_OPTIM_ARGS'}="--zero-thresholds";
$ENV{'CONFIG'}="/home/kai/uni/research_project/code/asm-re/src/main/resources/configure/config_en_dep-craft-fromraw.xml";
$ENV{'MODEL'}="/home/kai/uni/research_project/code/asm-re/model/craft-en-dep-1.1.0b1.jar";

system("rm -r -f training");
system("rm -r -f test");
system("rm -r -f tuning");
system("$scr_dir/parse-and-move.sh");
system("$scr_dir/run-rule-inference.sh");
system("$scr_dir/run-rule-optimization.sh");
system("$scr_dir/run-event-extraction.sh");
