#!/bin/bash

# Generate the 10 different random entries from the 
# It requires a sorted.txt file generated with "sort -u" to be executed on the CAIDA traces file (preprocessed to remove the leading spaces)
def=1024 # default entry elements
factor=8 # default factor to be stored in the filter 8x1024 entries to be generated in the file by default
files=10 # Number of files to generate

if [ -n "$1" ]; then
 factor=$1 # if we need a different multiple of elements to be randomly generated from the traces.
fi

if [ -n "$2" ]; then
 def=$2 # if we are going to use a different number of blocks/words in the filter
fi

if [ -n "$3" ]; then
 files=$3 # if we are going to generate a different number of files
fi

element=$((factor * def)) # the number of elements to be generated is factor times the number of words in the filter

for (( k = 1; k <= ${files}; k++)); do  # Generate the 10 different random set of entries
 file="shuf${factor}N_${def}B_${k}.txt" # the name of the files will be similar to shuf8N_1024B_1.txt, shuf8N_1024B_2.txt
 param="1,$((element))p;$((element+1))q"
 echo "Generating $file"
 echo "${param}"
 shuf sorted.txt | sed -n $param > $file 
done
