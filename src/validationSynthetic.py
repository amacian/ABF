#!/usr/bin/python3

import random, string
import sys, getopt
from GenericAdaptiveBloomFilter import GenericAdaptiveBloomFilter
from DataSet import DataSet
from LogNull import LogNull
from LogFile import LogFile
from LogScreen import LogScreen
from GenericHashFunctionsSHA512 import GenericHashFunctionsSHA512

# Function to generate the random set of elements.
# Current version uses strings, but integers were also used
# in previous versions
# num is the number of elements to generate
# if an AdaptiveBloomFilter abf is passed, elements are stored there
# if a DataSet object ds is passed, elements are stored there
# if a List lis is passed, elements are stored there.
# exclude set are a elements that should not be selected
def generateRandomElements(num, abf=None, ds=None, lis = None, exclude = set()):

    # Elements are added to the set to check for repetitions
    s = set()
    s.clear()

    # Keeps data of stored elements
    stored = 0
    # Generate elements until the value "stored" is reached
    while stored < num:
        # Generate strings of length between 3 a 50
        entry = "".join(random.choice(string.printable) for i in range(random.randint(3,50)))
        # if entry was already selected or is in the exclude set,
        # go to next iteration
        if entry in s or entry in exclude :
            continue
        # When an AdaptiveBloomFilter is received
        if abf is not None:
            # Add the entry to the filter
            abf.add(entry)
            # Add it to the slow memory backing it
            abf.addslow(entry)
        # When a DataSet is received
        if ds is not None:
            # Add the element to the DataSet
            ds.add(entry)
        # If a list is received
        if lis is not None:
            # Add the element to the list
            lis.append(entry)
        # Another element has been stored
        stored = stored + 1
        # Add it to the set so they are not repeated
        s.add(entry)
            
    return

# Main function
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
    # Hash function to be used (md5 by default)
    hash_f = 'md5'
    # How many false positives are required to swap between groups of functions
    swap=1

    # Retrieve the option values from command line
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hb:w:k:g:f:a:s:")
    except getopt.GetoptError:
        print ('argv[0] -b <words> -w <width> -k <bits> -g <function_groups> -f <factor> -a <hash> -s <false_to_swap>')
        sys.exit(2)
        
    for opt, arg in opts:
        # Help option. Print help and leave.
        if opt == '-h':
           print ('argv[0] -b <words> -w <width> -k <bits> -g <function_groups> -f <factor> -a <hash> -s <false_to_swap>')
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
        # -a option to change the default md5 hash to other ("sha512" supported)
        elif opt == "-a":
            hash_f = arg
        # -s option to change the number of false positives required to swap
        # between groups of functions.
        elif opt == "-s":
            swap = int(arg)

    # Pass the parameters to the run function
    run(blocks, width, k, groups, factor, hash_f, swap)

# Run the actual experiment using the parameters received
def run (blocks=1024, width=64, k=3, groups=2, factor=8, hash_f='md5', swap=1):        

    # Factor A=mul*N for the different experiments
    mul = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

    # factor * blocks elements are to be stored    
    maxin=factor*blocks

    # Number of times to execute each experiment to get an average
    totalIterations=10

    # A*t tests (negative element checks in the filter) are executed per iteration
    # A = mul * maxin (stored elements)
    t=100

    # Directory to get the positives and negatives
    directory = './data_test/'
    # File with the positives to be stored in the filter
    positivesFile = 'positives'
    # File with the negatives to check the Bloom filter behavior
    negativesFile = 'negatives'

    # Definition of the name of the output files.
    logOutput = 'result_b%s_w%s_k%s_g%s_f%s' % (blocks, width, k, groups, factor)
    logOutput2 = 'resultmin_b%s_w%s_k%s_g%s_f%s' % (blocks, width, k, groups, factor)

    # LogNull does not print, LogFile prints to file and LogScreen to the default output
    # Change the objects depending on which one you want to use
    log = LogNull()
    log2 = LogFile(directory+logOutput, "w")
    sc = LogScreen()

    # Message printing the parameters used for the experiment
    info ="Initializing parameters blocks=%d, width=%d, k=%d, groups=%d, factor=%d, hash_f=%s, swap=%s" % (blocks, width, k, groups, factor, hash_f, swap) 
    sc.write(info)
    log.write(info+"\n")
    log2.write(info+"\n")

    # For each of the A/N factors to be checked
    for i in mul:
        # Log the start of the experiment 
        info = "Starting execution of A=%d*%d*%d" % (factor, blocks, i) 
        sc.write(info)
        log.write(info+"\n")
        log2.write(info+"\n")

        # Initialized the completed tests
        completed=0
        
        tfp=0 # Total false positives
        ttp=0 # Total true positives
        ttn=0 # Total true negatives
        sfpr=0 # Accumulating False Positive Rates to calculate average
        # The total number of tests is A*t = i*maxin*t = 
        totalTests = maxin*t*i

        # List to store the negative elements
        l=list()
        while True:
            # Run for the number of iterations expected
            if completed>=totalIterations:
                break
            # Clear the list from previous iteration
            l.clear()

            # Create a dataset object
            ds = DataSet()
            # Create the Bloom Filter
            if hash_f == 'sha512':
                sha = GenericHashFunctionsSHA512(words=blocks, bits=width, nhash=k, hash_groups=groups)
                abf = GenericAdaptiveBloomFilter(words=blocks, bits=width, nhash=k, hash_groups=groups, hash_f=sha)
            # Otherwise build it using the default MD5 hash
            else:
                abf = GenericAdaptiveBloomFilter(words=blocks, bits=width, nhash=k, hash_groups=groups)

            # Call to the generateRandomElements function to create
            # the maxin positives that will be stored in the filter and the memory
            while ds.length()<maxin:
                generateRandomElements(maxin, abf, ds)
                sc.write("length stored: %s" % ds.length())

            # Call to the generateRandomElements function to create
            # the mul*maxin negatives that will be checked against the filter.
            # Exclude the positives and check that everything worked properly
                l.clear()
                generateRandomElements(maxin*i, lis=l, exclude=ds.data)
                if ds.data.isdisjoint(l):
                    break
                sc.write("False positive found")

            count = 0 # count of the tests performed
            fp=0 # false positives in this test
            tn=0 # true negatives in this test

            while True:
                # finish if all the tests were run
                if count >= totalTests:
                    break
                # select a random index among all the elements in the negative list
                idx = random.randint(0,len(l)-1)
                # extract the element
                element = l[idx]
                # By default, suppose it is a true negative
                tn+=1
                # Check if it gives a falso positive
                if abf.check(element):
                    # Add it to the false positive count
                    fp+=1
                    tn-=1 # No longer true negative
                    # Swap between functions will ocurr every "swap" false
                    # positives found. Use module operator to detect
                    if fp%swap == 0:
                        abf.swaphash(element) # Bloom filter adaptation
                # A test has been completed
                count+=1
            # Print results of current iteration 
            info = "Iteration %s. FP=%d, TN=%d,FPR=%s." % (completed, fp, tn, fp/(fp+tn)) 
            sc.write(info)
            log.write(info+"\n")
            # Increase the number of completed iterations.
            completed+=1
            # Accumulate the number of false positives and true negatives for all iterations
            tfp+=fp
            ttn+=tn
            # Accumulate the false positive rate (will be averaged by iterations)
            sfpr+=fp/(fp+tn)

        # Print the total number of iterations, false positives and true negatives
        info = "Completados %s. TFP=%s, TTN=%s." % (completed,tfp, ttn) 
        sc.write(info)
        log.write(info+"\n")

        # Print the average values of false positives and true negatives
        info = "Mean: TFP=%s, TTN=%s." % (tfp/completed, ttn/completed)
        sc.write(info)
        log.write(info+"\n")

        # Calculate the mean FPR value based on the total accumulated TFP and TTN numbers
        info = "TFP/(TFP+TTN) for %s*%s*%d = %s" % (factor, blocks, i, tfp/(tfp+ttn))
        sc.write(info)
        log.write(info+"\n")

        # Calculate the mean FPR value dividing the accumulated sfpr by the number of iterations 
        info = "Mean FPR for %s*%s*%d = %s" % (factor, blocks,i, round(sfpr/completed,4)) 
        sc.write(info)
        log.write(info+"\n")
        #log2.write(info+"\n")
        log2.write("%s\n" % round(sfpr/completed,4))

        log.flush()
        log2.flush()

    log.close()
    log2.close()
    return

main(sys.argv)
