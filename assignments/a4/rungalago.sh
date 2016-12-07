#!/usr/bin/env bash

if [ $# -eq 0 ]; then
   ./galago-3.10/contrib/target/appassembler/bin/galago --help
elif [ "$1" = "help" ]; then
 ./galago-3.10/contrib/target/appassembler/bin/galago --help
elif [ "$1" = "build" ]; then
shift
 ./galago-3.10/contrib/target/appassembler/bin/galago build --nonStemmedPosting=true --stemmedPostings=false \
  --corpus=true --indexPath=$1 --inputPath+$2
elif [ "$1" = "dump-idx" ]; then
shift
./galago-3.10/contrib/target/appassembler/bin/galago dump-index $@
elif [ "$1" = "search" ]; then
shift
./galago-3.10/contrib/target/appassembler/bin/galago search --port=9000 $@
elif [ "$1" = "build-window" ]; then
shift
./galago-3.10/contrib/target/appassembler/bin/galago build-window --width=$1 --ordered=$2 \
 --stemming=false --spaceEfficiecent=true  --inputPath=$3 --indexPath=$4
elif [ "$1" = "eval" ]; then
shift
 ./galago-3.10/contrib/target/appassembler/bin/galago eval --judgments=$1 --baseline=$2  --details=true --summary=false \
 --metrics+num_ret --metrics+num_rel --metrics+num_rel_ret --metrics+num_unjug_ret \
 --metrics+p --metrics+r --metrics+map --metrics+jmap --metrics+muap   \
 --metrics+ndcg --metrics+ndcg5 --metrics+ndcg10 --metrics+ndcg20 --metrics+ndcg30 --metrics+ndcg100  \
 --metrics+ndcg200 --metrics+ndcg500 --metrics+ndcg1000  \
 --metrics+recip_rank --metrics+R-prec  \
 --metrics+P5 --metrics+P10 --metrics+P20 --metrics+P30 --metrics+P100 --metrics+P200 --metrics+P500 --metrics+P1000
else
 ./galago-3.10/contrib/target/appassembler/bin/galago $@
fi

