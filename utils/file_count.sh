#!/bin/bash

if [[ -n $1 ]]
then
  cd $1
fi
pwd

dirlist=`ls`

for d in $dirlist
do
  if [[ -d "$d" ]]
  then
    echo $d : `ls $d | grep -v Thumbs.db | wc -l`
  fi
done
