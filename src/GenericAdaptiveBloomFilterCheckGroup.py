import hashlib
import math
import random
import string
from GenericHashFunctionsMD5 import GenericHashFunctionsMD5
from GenericSlowMemoryRepresentation import GenericSlowMemoryRepresentation

# Adaptive bloom filter
class GenericAdaptiveBloomFilter:

    def __init__(self, words=1024, bits=64, nhash=2, hash_groups=2, backed=True, hash_f=None):
        # number of blocks/words
        self.words = words
        # number of bits per block
        self.bits = bits
        # the structure is stored as a flattened array
        self.bloom_structure = [False] * (words * bits)
        # the selector array with an integer per word to indicate
        # the function being used
        self.selector_structure = [0] * words
        # the hash class used to generate the functions
        if hash_f is None:
            self.hash = GenericHashFunctionsMD5(words, bits, nhash, hash_groups)
        else:
            self.hash = hash_f
        # the number of hashes per group, apart from the word hash function
        self.nhash = nhash
        # the number of total hash groups (f, g ...)

        self.hash_groups = hash_groups
        # the size of the word index
        self.wordidx_size = int(math.log2(words))
        # the size of each bit index to set/get a bit from the word
        self.bitidx_size = int(math.log2(bits))
        # a simulation of the slow memory to swap the words
        # only if the bloom filter is backed by this memory
        if backed and hash_groups>1:
            self.slow = GenericSlowMemoryRepresentation(words, bits, hash_groups)
            self.backed=True
        else:
            self.slow = None
            self.backed = False
        return

    # Change the hash object that generates the function
    def setHash(self, hashObject):
        if hashObject is not None:
            self.hash = hashObject
        return
        
    # method to add an element into the hash
    def add(self, data):
        # retrieve the block index to select the word
        wordidx = self.hash.getword_idx(data)

        # obtain the function group being used for that word
        group_i = self.selector_structure[wordidx]

        # extract a position from each hash to set the bit in the selected word
        for i in range(self.nhash):
            # position for the ith hash of the group_i function 
            # the final position in the array is a combination
            # of word index and bit index
            bitidx = self.hash.getbit_idx(data, i, group_i) 
            idx = int(wordidx*self.bits + bitidx)

            # set the appropriate bit
            self.bloom_structure[idx] = True

        return

    def addslow(self, data):
        if not self.backed:
            return
      # retrieve the block index to select the word
        wordidx = self.hash.getword_idx(data)

        # for each hash group we get the positions to be updated in the
        # slow memory
        idx_list = set()
        for g in range(self.hash_groups):
            idx_list.clear()
            # extract a position from each hash to set the bit in the selected word
            for i in range(self.nhash):
                # position for the ith hash of the group_i function 
                # the final position in the array is a combination
                # of word index and bit index
                bitidx = self.hash.getbit_idx(data, i, g)
                idx_list.add(bitidx)
            # Set all the bits for this group
            self.slow.setbit(g, wordidx, idx_list)    
        return
    
    # check the bloom filer for the specified data
    def check(self, data):
        # retrieve the block index to select the word
        wordidx = self.hash.getword_idx(data)

        # obtain the function group being used for that word
        group_i = self.selector_structure[wordidx]

        # extract a position from each hash to get the bit from the selected word
        for i in range(self.nhash):
            # position for the ith hash of the group_i function
            # the final position in the array is a combination
            # of word index and bit index
            bitidx = self.hash.getbit_idx(data, i, group_i)
            idx = int(wordidx*self.bits + bitidx)

            # check if the bit is set for the specified word
            # if not, the data is not in the included
            if not self.bloom_structure[idx]:
                return False
        return True

    # Swap the hashed word corresponding to data
    # by the word hashed by the alternative function.
    # Retrieving the information from the slow memory
    def swaphash(self, data):
        if not self.backed:
            return
        # retrieve the block index to select the word
        wordidx = self.hash.getword_idx(data)

        # calculate where the current word starts
        wordinit = wordidx*self.bits

        original = self.selector_structure[wordidx]
        while True:
            # Getting the proper word from the slow memory
            new_group = self.selector_structure[wordidx]+1
            if new_group==self.hash_groups:
                new_group = 0
	
            word = self.slow.getword(new_group, wordidx)

            # Replace the hashed word with the alternative hashed word
            self.bloom_structure[wordinit:wordinit+self.bits] = word
            # Update the selector to indicate that a new function is used
            self.selector_structure[wordidx] = new_group

            # until we reach the original group
            if new_group==original:
                break
    
            # or until we reach a function that does not give a false positive
            if not self.check(data):
                break


        return new_group

