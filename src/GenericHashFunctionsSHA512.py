import hashlib
import math

class GenericHashFunctionsSHA512:

    def __init__(self, words=1024, bits=64, nhash=2, hash_groups=2):
        # the underlying hash function to be used. Just one in this class
        # the md5 result is split in a way the subsets are used for
        # all the hash functions
        self.hash = hashlib.sha512

        # the number of total hash groups (f, g ...)
        self.hash_groups = hash_groups
        # the number of hashes per group, apart from the word hash function
        self.nhash = nhash
        # the size of the word index
        self.wordidx_size = int(math.log2(words))
        # the size of each bit index to set/get a bit from the word
        self.bitidx_size = int(math.log2(bits))
        # keep the last hash element and its value to avoid hash recalculation
        self.lastelement = "black_alert"
        self.lasthash = bin(int(self.hash(self.lastelement.encode()).hexdigest(),16))[2:].zfill(512)

        # sha512 hash provides 512 bits. With those bits we have to build:
        #   * The hash function to select the word
        #   * The nhash functions (g) to select the bits to be set/retrieved
        #   * Other (hash_groups-1)*nhash functions (f), alternative to the previous ones.
        #  hash = [word index][g bit index 1]...[g bit index nhash][f bit index 1]...[f bit index nhash]
        assert 512 >= (hash_groups*nhash*self.bitidx_size + self.wordidx_size)
        return

    # Retrieves the word index (the appropriate block) for the element
    def getword_idx(self,element):
    
        if self.lastelement != element:
            # Calculate the hash for the element and use
            # its hex representation
            hexval = self.hash(element.encode()).hexdigest()
            # Assign this element as the active element
            self.lastelement = element
            # Converting into binary adding 0s at the beginning to avoid losing
            # the first values when they are 0
            # Cache the hashed value
            self.lasthash = bin(int(hexval,16))[2:].zfill(512)

        # Calculate the word index using the firs wordidx_size bits from the hash.
        start = int(self.lasthash[0:self.wordidx_size],2)
        return start

    # Retrieves the bit index using the nth hash from group for the element
    def getbit_idx(self, element, n, group):
        assert group < self.hash_groups
        # Due to how the hash is reused, indices for the functions of group i
        # start at the end of the function from i-1. So the code is the
        # same, but skipping the n*(i-1) indices
        n = group*self.nhash + n
        
        if self.lastelement != element:
            # Calculate the sha512 hash for the element and use
            # its hex representation
            hexval = self.hash(element.encode()).hexdigest()
            # Assign this element as the active element
            self.lastelement = element
            # Converting into binary adding 0s at the beginning to avoid losing
            # the first values when they are 0
            # Cache the hashed value
            self.lasthash = bin(int(hexval,16))[2:].zfill(512)

        # Calculate the bit index selecting the start position by skipping
        # the word index and the previous n-1 bit indices
        start = self.wordidx_size+self.bitidx_size*n
        # the bit index indcludes bitidx_size bits from the hash
        bitidx = int(self.lasthash[start:start+self.bitidx_size],2)
        return bitidx

    # Returns the actual hash used to build the indices
    def getHash(self, element):
        if self.lastelement != element:
            # Calculate the sha512 hash for the element and use
            # its hex representation
            hexval = self.hash(element.encode()).hexdigest()
            # Assign this element as the active element
            self.lastelement = element
            # Converting into binary adding 0s at the beginning to avoid losing
            # the first values when they are 0
            # Cache the hashed value
            self.lasthash = bin(int(hexval,16))[2:].zfill(512)
        return self.lasthash        
