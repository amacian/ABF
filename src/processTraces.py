import random
import sys, getopt
from GenericAdaptiveBloomFilter import GenericAdaptiveBloomFilter
from DataSet import DataSet
from LogNull import LogNull
from LogFile import LogFile
from LogScreen import LogScreen
from GenericHashFunctionsSHA512 import GenericHashFunctionsSHA512
from GenericHashFunctionsSHA512All import GenericHashFunctionsSHA512All

# Main method
def main(argv):
    # Default values for
    # Number of words in the filter
    blocks = 1024
    # bit width per word
    width = 64
    # Number of hash functions to set a bit in the word
    k=3
    # Number of groups of functions that can be changed when a false
    # positive is detected
    groups=2
    # Elements stored in the filter will be factor*blocks
    factor=8
    # Default name for the file with all the traces in order
    traces = './traces/chicago.dirA/equinix-chicago.dirA.20140619-130900_noleadingspace.txt'
    # Default name for the folder of the traces and storable elements
    folder = './traces/chicago.dirA/'
    # Hash function to be used (md5 by default)
    hash_f = 'md5'
    # How many false positives are required to swap between groups of functions
    swap=1

    # Retrieve the option values from command line
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hb:w:k:g:f:t:d:a:s:")
    except getopt.GetoptError:
        print ('argv[0] -b <words> -w <width> -k <bits> -g <function_groups> -f <factor> -t <filetraces> -d <folder> -a <hash> -s <false_to_swap>')
        sys.exit(2)

    for opt, arg in opts:
        # Help option. Print help and leave.
        if opt == '-h':
           print ('argv[0] -b <words> -w <width> -k <bits> -g <function_groups> -f <factor> -t <filetraces> -d <folder> -a <hash> -s <false_to_swap>')
           sys.exit()
        # -b option for setting the number of words in the filter
        elif opt == "-b":
            blocks=int(arg)
        # -w option to set the bit width within each word
        elif opt == "-w":
            width=int(arg)
        # -k option to set the number of hash elements to select the bits to be set
        elif opt == "-k":
            k=int(arg)
        # -g options to set the number of groups of hash functions to swap
        # among them when false positives are found
        elif opt == "-g":
            groups=int(arg)
        # -f option to set the factor (factor x words will be stored)
        elif opt == "-f":
            factor=int(arg)
        # -t option to define the traces file to be used
        elif opt == "-t":
            traces = arg
        # -d option to set the directory where the traces and storable element files
        # are to be located
        elif opt == "-d":
            folder = arg
        # -a option to change the default md5 hash to other ("sha512" supported)
        elif opt == "-a":
            hash_f = arg
        # -s option to change the number of false positives required to swap
        # between groups of functions.
        elif opt == "-s":
            swap = int(arg)

    # Pass the parameters to the run function
    run(traces, folder, blocks, width, k, groups, factor, hash_f, swap)
    return

# Run the actual experiment using the parameters received
def run (traces, folder, blocks=1024, width=64, k=3, groups=2, factor=8, hash_f='md5', swap=1):
    # Number of times to execute each experiment to get an average
    # There must exist as many files with the elements to be stored
    # as iterations.
    totalIterations=10

    # Definition of the name of the output files.
    logOutput = 'result_b%s_w%s_k%s_g%s_f%s' % (blocks, width, k, groups, factor)
    logOutput2 = 'resultmin_b%s_w%s_k%s_g%s_f%s' % (blocks, width, k, groups, factor)

    # LogNull does not print, LogFile prints to file and LogScreen to the default output
    # Change the objects depending on which one you want to use
    log = LogNull()
    log2 = LogFile(folder+logOutput, "w")
    sc = LogScreen()

    # Message explaining the file to be read for the traces
    info ="Traces file=%s" % (traces)
    sc.write(info)
    log.write(info+"\n")
    log2.write(info+"\n")

    # Message printing the parameters used for the experiment
    info ="Initializing parameters blocks=%d, width=%d, k=%d, groups=%d, factor=%d, hash_f=%s, swap=%s" % (blocks, width, k, groups, factor, hash_f, swap)
    sc.write(info)
    log.write(info+"\n")
    log2.write(info+"\n")

    # False positive rate accumulation element
    fpr = 0

    # Run the iterations and get the average
    for i in range(1,totalIterations+1):
        # The file name should be similar to "/directory/shuf8N_1024B_1.txt"
        shuf_file = "%sshuf%sN_%sB_%s.txt" % (folder, factor, blocks, i)
        # Data set that keeps the actual elements that were added to the filter
        # to perform false positive check
        ds = DataSet()
        # AdaptiveBloomFilter file
        abf = None
        # Build the filter passing a SHA512 hash function
        if hash_f == 'sha512':
            sha = GenericHashFunctionsSHA512(words=blocks, bits=width, nhash=k, hash_groups=groups)
            abf = GenericAdaptiveBloomFilter(words=blocks, bits=width, nhash=k, hash_groups=groups, hash_f=sha)
        elif hash_f == 'sha512b':
            sha = GenericHashFunctionsSHA512All(words=blocks, bits=width, nhash=k, hash_groups=groups)
            abf = GenericAdaptiveBloomFilter(words=blocks, bits=width, nhash=k, hash_groups=groups, hash_f=sha)
        # Otherwise build it using the default MD5 hash
        else:
            abf = GenericAdaptiveBloomFilter(words=blocks, bits=width, nhash=k, hash_groups=groups)
        # False positives initialized to zero
        fp=0
        # True positives initialized to zero
        tp=0
        # True negatives initialized to zero
        tn=0
        # factor * blocks elements are to be stored
        maxin=factor*blocks

        # Print the file name with the storable elements that is going to be used
        sc.write(shuf_file)
        # Open the file
        dataToStore = open(shuf_file, 'r')

        # Initializing the number of elements stored to zero
        stored=0
        # Keep storing until factor*blocks is reached or the file ends
        while True:
            if stored>=maxin:
                break

            entry = dataToStore.readline()
            if not entry:
                break
            stored+=1
            # Store into the Bloom filter
            abf.add(entry)
            # Store in the slow memory for all the groups of functions
            abf.addslow(entry)
            # Store the actual value to check for false positives
            ds.add(entry)

        # Close the file
        dataToStore.close()

        # Message to verify if we stored the expected number of elements
        sc.write("length stored: %s" % ds.length())

        # Open the file with the traces
        caida = open(folder+traces, 'r')

        # Process all elements
        while True:
            # Read next element
            element = caida.readline()
            if not element:
                break
            # By default, consider it a true negative
            tn+=1
            # If there is a match in the filter
            if abf.check(element):
                # If it is not an element that was stored
                if not ds.test(element):
                    # Then it is a false positive
                    fp+=1
                    # No longer considered true negative
                    tn-=1
                    # Swap between functions will ocurr every "swap" false
                    # positives found. Use module operator to detect
                    if fp%swap == 0:
                        abf.swaphash(element)
                # It was found and it was actually stored
                else:
                    # It is a true positive
                    tp+=1
                    # No longer considered true negative
                    tn-=1

        # Close the file with the traces
        caida.close()

        # Accumulate the False positive rate. It will be divided by the number of iterations
        fpr +=  fp/(fp+tn)

        # Print the result of the iteration
        info = "Iteration %s. FP=%d, TP=%d, TN=%d, FPR=%s." % (i, fp, tp, tn, fp/(fp+tn))
        sc.write(info)
        log.write(info+"\n")
        log2.write(info+"\n")

    # Print the final result
    info = "FPR for  %sx%s. FPR %s." % (factor, blocks, round(fpr/totalIterations,6))
    sc.write(info)
    log.write(info+"\n")
    log2.write(info+"\n")


main("")
