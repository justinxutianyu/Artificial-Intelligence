#Arguments are:
# 1) Sub-graph matching script
# 2) ASM-RE scripts directory
# 3) Training data
# 4) Optimization/Tuning data
# 5) Test/Development data
# 6) Corpus name (supported values are genia, variome and seedev)

echo $1

perl \
/home/kai/uni/research_project/code/asm-re/src/main/scripts/subgraph-match.pl \
/home/kai/uni/research_project/code/asm-re/src/main/scripts \
/home/kai/uni/research_project/variome_corpus/variome_annotation_corpus/data/$1/train  \
/home/kai/uni/research_project/variome_corpus/variome_annotation_corpus/data/$1/test \
/home/kai/uni/research_project/variome_corpus/variome_annotation_corpus/data/$1/test \
variome \
$1
