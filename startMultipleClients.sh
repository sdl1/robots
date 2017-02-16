#!/bin/bash
AINAME=$1
TEAM=$2
NUMBER=$3

if [ $# -lt 3 ]; then
  echo "Usage: $0 ai team number"
  exit
fi

for i in `seq 1 $NUMBER`
do
  ./Client.py -a $AINAME -t $TEAM &
done
