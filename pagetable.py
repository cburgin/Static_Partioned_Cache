# Page Table for cache simulator
import math

class PageTable():
    def __init__(self, memory_size, cache_size, block_size, mapping,
                    allowed_sets, page_size):
        self.memory_size = memory_size
        self.cache_size = cache_size
        self.block_size = block_size

        self.num_blocks = self.cache_size // self.block_size
        if mapping == 0:
            self.mapping = self.num_blocks
        else:
            self.mapping = mapping
        self.num_sets = self.cache_size // (self.mapping * self.block_size)
        # Figure bit lengths
        self.set_bits = int(math.log(self.num_sets,2))
        self.offset_bits = int(math.log(self.block_size,2))
        self.offset_mask = ((2**self.offset_bits) - 1)
        self.tag_bits = int(math.log(self.memory_size,2))-self.set_bits-self.offset_bits
        self.page_bits = int(math.log(self.page_size,2))
        self.color_bits = (self.set_bits + self.offset_bits) - self.page_bits
        self.color_mask = self.__build_color_mask(color_bits, set_bits)
        self.virt_page_num_bits = int(math.log(self.memory_size,2)) - self.offset_bits

        # Get colors for this PageTable
        self.colors = self.__get_colors(self.allowed_sets, self.color_bits, self.set_bits)

        self.page_size = page_size
        self.page_table = [{'valid':0,'physical_page':0} for x in range(self.memory_size)]

    # Translate a virtual addr to a physical addr in one of the allowed pages
    # returns a tuple (present, phys_addr)
    # present - was the value in the page table, if False the cache needs to be invalidated
    #           on this call, cause its really from a diff spot in mem
    # phys_addr - the physical address to send to the cache
    def translate(self, virt_addr):
        # Get virtual page and offset
        virt_page_num = virt_addr >> self.offset_bits
        offset = virt_addr & self.offset_mask
        # Figure out the virtual addrs color
        virt_page_color = (virt_page_num & self.color_mask)>>(self.set_bits - self.color_bits)

        # See if the color is on this page table
        if virt_page_color in self.colors:
            # color is valid - Do a table lookup
            return __table_lookup(virt_page_num, offset)
        else:
            # we need to convert it to an address with the right color
            # and somehow notify the cache its really diff/new data
            # Pick a color to use
            new_color = random.choice(self.colors)
            # Change the address color

    def __change_color(self, virt_page_num, new_color):
        # make it a string for easy slicing and dicing
        tmp = '{:b}'.format(virt_page_num)
        self.virt_page_num_bits
        return new_page_num

    # table lookup -- to shorten the lenght of translate
    def __table_lookup(self, virt_page_num, offset):
        if self.page_table[virt_page_num]['valid'] == 0:
            # page isnt in the table, lets add it
            self.page_table[virt_page_num]['valid'] = 1
            self.page_table[virt_page_num]['physical_page'] = virt_page_num
            phys_addr = (self.page_table[virt_page_num]['physical_page']<<self.offset_bits)+offset
            return False, phys_addr
        else:
            # page is already here
            phys_addr = (page_table[virt_page_num]['physical_page']<<self.offset_bits)+offset
            return True, phys_addr

    # Figure out allowed color bits from allowed sets and total sets
    def __get_colors(self, allowed_sets, color_bits, set_bits):
        lowest_set = allowed_sets[0]
        higest_set = allowed_sets[1]
        low_color = (lowest_set & self.color_mask)>>(set_bits - color_bits)
        high_color = (highest_set & self.color_mask)>>(set_bits - color_bits)
        colors = list(range(low_color,high_color+1))
        return colors

    def __build_color_mask(self, color_bits, set_bits):
        mask = ''
        for i in range(color_bits):
            mask += '1'
        for i in range(set_bits - color_bits):
            mask += '0'
        return int(mask,2)
