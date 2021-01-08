# ABF

This repository includes the implementation in Python of an Adaptive Bloom Filter for the paper:

P. Reviriego, A. Sánchez-Macián, O. Rottenstreich and D. Larrabeiti, "Adaptive Bloom Filters", under submission to IEEE ...

# Dependencies
- Python > 3.6
- hashlib, random, string, getopt and math libraries
- If you want to use the shell script files to generate subsets of traces, then a Unix/Linux/Cygwin system is needed.

# Content
*src* directory includes the following files:
- validationSynthetic.py (to generate synthetic traffic and validate the filter behavior)
- processTraces.py (to process and run the CAIDA traces)
- GenericAdaptiveBloomFilter.py (Adaptive Bloom Filter implementation)
- GenericAdaptiveBloomFilterCheckGroup.py (Alternative GenericAdaptiveBloomFilter. When swapping, it checks if the new set of functions also produces a FP. If so, iterates to the next set and keeps doing it until no FP is produced or the original set is reached.)
- GenericSlowMemoryRepresentation.py (Simulates the slow memory storing the different copies of the Bloom-1 filter)
- GenericHashFunctionsMD5.py (Generates the hash function to select the word and the groups of hash functions to select the bits using MD5)
- GenericHashFunctionsMD5.py (Generates the hash function to select the word and the groups of hash functions to select the bits using SHA512)
- LogScreen, LogFile and LogNull (To log the different messages generated during the execution).
- DataSet (to store the actual values that were stored for later false positive detection).

*src/traces* includes the following bash script:
- genshuf.sh (to create sets of independent random traces from a file, to perform the CAIDA traces experiment).

# Execution of Synthetic Data simulation
To run the synthetic data simulation execute the following command:

`validationSynthetic.py -b <number_of_words> -w <width_of_word> -k <number_of_bits_set> -f <factor> -g <groups of functions> -a <hash_type> -s <fp_times_per_swap>`

Where:
* "-b" sets the number of words/blocks in the ABF filter (1024 by default).
* "-w" sets the width of each of the words (64 by default).
* "-k" indicates the number of bit hash functions per group, i.e. bits to be set (3 by default)
* "-f" is the factor (8 by default) used to indicate how many elements will be stored in the filter, i.e. factor x words
* "-g" is the number of groups of functions used (2 by default).
* "-a" is the type of hash function used (md5 by default). At the moment it only accepts "sha512" or md5.
* "-s" is how many FPs have to be found to trigger the swap between functions from different groups.

For instance:

`validationSynthetic.py -b 1024 -w 64 -k 3 -f 8 -g 2`

`validationSynthetic.py -b 1024 -w 64 -k 3 -f 8 -g 8 -a sha512 -s 2`

# Execution of CAIDA data traces (or other traces)
1. Preprocess the traces.
    1. Remove the leading whitespaces in some of the lines of the CAIDA files if present. E.g. `cat equinix-chicago.dirA.20140619-130900.txt | sed -e "s/^ //" > nospaces.txt`
    1. Generate a file with unique traces. E.f. `sort -u nospaces.txt > sorted.txt`
    1. Generate sets of *factor x words* random entries using genshuf.sh, passing the factor, the number of words and the number of files. E.g. `./genshuf.sh 8 1024 10`
1. Execute the simulations using *processTraces.py*.

Command is as follows:
`processTraces.py -b <number_of_words> -w <width_of_word> -k <number_of_bits_set> -f <factor> -g <groups of functions> -a <hash_type> -s <fp_times_per_swap> -d <directory> -t <trace_file>`
Where:
* "-b" sets the number of words/blocks in the ABF filter (1024 by default).
* "-w" sets the width of each of the words (64 by default).
* "-k" indicates the number of bit hash functions per group, i.e. bits to be set (3 by default)
* "-f" is the factor (8 by default) used to indicate how many elements will be stored in the filter, i.e. factor x words
* "-g" is the number of groups of functions used (2 by default).
* "-a" is the type of hash function used (md5 by default). At the moment it only accepts "sha512" or md5.
* "-s" is how many FPs have to be found to trigger the swap between functions from different groups.
* "-d" directory where the traces file and the random entries files are present. Results will be stored there as well.
* "-f" name of the file with the traces (nospaces.txt in the previous example) 

For instance:
`processTraces.py -b 1024 -w 64 -k 3 -f 8 -g 8 -d ./traces/sanjose.dirA/ -t nospaces.txt -a sha512 -s 2`

`processTraces.py -b 1024 -w 64 -k 6 -f 12 -g 2 -d ./traces/sanjose.dirA/ -t nospaces.txt`

To use the alternative GenericAdaptiveBloomFilter, an import in processTraces.py needs to be changed: *"from GenericAdaptiveBloomFilter import GenericAdaptiveBloomFilter"* to *"from GenericAdaptiveBloomFilterCheckGroup import GenericAdaptiveBloomFilter"*.
