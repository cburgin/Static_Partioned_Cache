#Cache Implementation

class cache:
    """A cache implementation"""
    def __init__(self, cacheSize, blockSize, mapping):
        #Simulation inputs
        self.cacheSize = cacheSize
        self.blockSize = blockSize

        #Calculate internal cache setup
        self.numBlocks = int(self.cacheSize / self.blockSize)
        if mapping != 0:
            self.cacheMap = mapping
        else:
            self.cacheMap = self.numBlocks
        self.numSets = int(self.cacheSize / (self.cacheMap * self.blockSize))

        #Create a 2D array of cacheline elements
        self.cache = [[{'valid':0, 'tag':0} for x in range(self.cacheMap)] for y in range(self.numSets)]

        #Create a 2D array for the lru
        self.lru = [[0 for x in range(self.cacheMap)] for y in range(self.numSets)]

    #Accepts a single atomic operation and runs it through the cache.
    def simulate_element(self, element):
        cacheHit = False

        #Read in the elements r/w and address
        read_write = element[0]
        address = element[1]

        #Find the set and tag based on the input address
        curr_set = int((address / self.blockSize) % self.numSets)
        curr_tag = int((address / self.blockSize) / self.numSets)

        #Increment every location in the LRU every time there is a cache access
        for i in range(self.numSets):
            for j in range(self.cacheMap):
                self.lru[i][j] += 1

        if read_write == 'read':
            found = False
            for i in range(self.cacheMap):
                if self.cache[curr_set][i]['tag'] == curr_tag and self.cache[curr_set][i]['valid'] != 0:
                    #If the tag matches and the data is valid then mark as found
                    #and as a hit and reset the LRU in this location.
                    cacheHit = True
                    found = True
                    self.lru[curr_set][i] = 0

            if not found:
                index = 0
                #Need to pull data into the cache, look for invalid locations
                #before using the lru to evict someone
                for j in range(self.cacheMap):
                    if self.cache[curr_set][j]['valid'] == 0 and not found:
                        #Loop until and invalid location is found.  Once found
                        #set found to true, reset the lru and mark the index that
                        #it was found in.
                        found = True
                        self.lru[curr_set][j] = 0
                        index = j

                #If there aren't any invalid locations then use the lru
                if not found:
                    for j in range(self.cacheMap):
                        if self.lru[curr_set][j] > self.lru[curr_set][index]:
                            index = j

                    #Reset the lru in the location choosen to be replaced
                    self.lru[curr_set][index] = 0

                #Update the cache information
                self.cache[curr_set][index]['tag'] = curr_tag
                self.cache[curr_set][index]['valid'] = 1

        elif read_write == 'write':
            found = False
            index = 0
            for i in range(self.cacheMap):
                if self.cache[curr_set][i]['tag'] == curr_tag and not found:
                    #If the tag matches and it has not been found yet
                    cacheHit = True
                    found = True
                    self.lru[curr_set][i] = 0
                    index = i

            if not found:
                for i in range(self.cacheMap):
                    if self.cache[curr_set][i]['valid'] == 0 and not found:
                        #Loop until and invalid location is found.  Once found
                        #set found to true, reset the lru and mark the index that
                        #it was found in.
                        found = True
                        self.lru[curr_set][i] = 0
                        index = i

                #If there aren't any invalid locations then use the lru
                if not found:
                    for i in range(self.cacheMap):
                        if self.lru[curr_set][i] > self.lru[curr_set][index]:
                            index = i

                    #Reset the lru in the location choosen to be replaced
                    self.lru[curr_set][index] = 0

                #Update the cache information
                self.cache[curr_set][index]['tag'] = curr_tag
                self.cache[curr_set][index]['valid'] = 1

        return cacheHit

    def display_cache(self):
