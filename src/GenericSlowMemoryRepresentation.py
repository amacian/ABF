import math

# A dummy representation of a Slow memory backend where the
# hashed words with both functions are stored
class GenericSlowMemoryRepresentation:

    def __init__(self, words=2048, bits=32, hash_groups=2):
        # number of blocks/words
        self.words = words
        # number of bits per block
        self.bits = bits
        # the number of total hash groups (f, g ...)
        self.hash_groups = hash_groups

        # the structures are stored as flattened arrays
        # Each group is stored consecutive to the previous one
        self.back_bloom = [False] * hash_groups * (words * bits)
        
        # the size of the word index
        self.wordidx_size = int(math.log2(words))
        # the size of each bit index to set/get a bit from the word
        self.bitidx_size = int(math.log2(bits))
        return

    # set the corresponding bits for words hashed with
    # all the groups of functions
    def setbit(self, idx_array):
        for i in idx_array:
            self.back_bloom[i] = True
        return

    # set the corresponding bits for words hashed with
    # a specific groups of functions
    def setbit(self, group, wordidx, idx_array):
        for i in idx_array:
            actual_i = (group*self.words + wordidx)*self.bits + i
            self.back_bloom[actual_i] = True
        return

    # get the wordidx-indexed word hashed by the
    # selected function (group)
    def getword(self, group, wordidx):
        assert group<self.hash_groups
        # calculate where the current word starts for the appropriate group
        wordinit = (group*self.words + wordidx)*self.bits

        # Getting the proper word 
        word = self.back_bloom[wordinit:wordinit+self.bits]

        return word

    # set the wordidx-indexed block hashed by the
    # selected function replacing its value by word
    # return the old word
    def setword(self, group, wordidx, word):
        assert group<self.hash_groups
        # calculate where the current word starts for the appropriate group
        wordinit = (group*self.words + wordidx)*self.bits
        # Replacing the proper word
        oldword = self.back_bloom[wordinit:wordinit+self.bits]
        self.back_bloom[wordinit:wordinit+self.bits] = word
        return oldword
        

