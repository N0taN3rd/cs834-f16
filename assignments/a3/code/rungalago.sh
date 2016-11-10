#!/usr/bin/env bash

if [ $# -eq 0 ]; then
   ./galago-3.10/contrib/target/appassembler/bin/galago --help
elif [ "$1" = "help" ]; then
 ./galago-3.10/contrib/target/appassembler/bin/galago --help
elif [ "$1" = "build" ]; then
shift
 ./galago-3.10/contrib/target/appassembler/bin/galago build --nonStemmedPosting=true --stemmedPostings=true \
 --stemmer+krovetz --corpus=true --indexPath=$1 --inputPath+$2
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
else
 ./galago-3.10/contrib/target/appassembler/bin/galago $@
fi

