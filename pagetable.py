# Page Table for cache simulator
import math
import random

class PageTable():
    def __init__(self, memory_size, cache_size, block_size, mapping,
                    allowed_sets, page_size):
        self.memory_size = memory_size
        self.cache_size = cache_size
        self.block_size = block_size
        self.page_size = page_size
        self.allowed_sets = allowed_sets
        self.page_size = page_size

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
        self.page_mask = ((2**self.page_bits) - 1)
        self.color_bits = (self.set_bits + self.offset_bits) - self.page_bits
        self.color_mask = self.__build_color_mask(self.color_bits, self.set_bits)
        self.virt_page_num_bits = int(math.log(self.memory_size,2)) - self.page_bits

        # Get colors for this PageTable
        self.colors = self.__get_colors(self.allowed_sets, self.color_bits, self.set_bits)

        self.page_table = [{'valid':0,'physical_page':0} for x in range(self.memory_size)]
        self.recolor_map = {}

    # Translate a virtual addr to a physical addr in one of the allowed pages
    # returns a tuple (present, phys_addr)
    # present - was the value in the page table, if False the cache needs to be invalidated
    #           on this call, cause its really from a diff spot in mem
    # phys_addr - the physical address to send to the cache
    def translate(self, virt_addr):
        # Get virtual page and offset
        virt_page_num = virt_addr >> self.page_bits
        page_offset = virt_addr & self.page_mask
        # Figure out the virtual addrs color
        virt_page_color = (virt_page_num & self.color_mask)
        #print('virt_page_color', virt_page_color)
        # See if the color is on this page table
        if virt_page_color in self.colors:
            # color is valid - Do a table lookup
            present,phys_addr = self.__table_lookup(virt_page_num, page_offset)
            return present,phys_addr
        else:
            # # See if we have mapped this before -- and give same result
            # if virt_page_num in self.recolor_map.keys():
            #     # We have seen this exact request before return its value
            #     present,phys_addr = self.__table_lookup(self.recolor_map[virt_page_num], page_offset)
            #     #print('used a recolor')
            # else:
            #     # we need to convert it to an address with the right color
            #     # and somehow notify the cache its really diff/new data
            #     # Pick a color to use
            #     new_color = random.choice(self.colors)
            #     # Change the address color
            #     new_virt_page_num = self.__change_color(virt_page_num, new_color)
            #     # If we had a page here, we need to make  invalid
            #     self.page_table[new_virt_page_num]['valid'] = 0
            #     self.recolor_map[virt_page_num] = new_virt_page_num
            #     # Now do the lookup
            #     present,phys_addr = self.__table_lookup(new_virt_page_num, page_offset)

            # Pick a color to use
            new_color = random.choice(self.colors)
            # Change the address color
            new_virt_page_num = self.__change_color(virt_page_num, new_color)
            # If we had a page here, we need to make  invalid
            self.page_table[new_virt_page_num]['valid'] = 0
            # Now do the lookup
            present,phys_addr = self.__table_lookup(new_virt_page_num, page_offset)
            return present,phys_addr

    def __change_color(self, virt_page_num, new_color):
        # Get rid of old color
        virt_page_num = virt_page_num >> self.color_bits
        virt_page_num = virt_page_num << self.color_bits
        # Add new color
        virt_page_num = virt_page_num + new_color
        return virt_page_num

    # table lookup -- to shorten the lenght of translate
    def __table_lookup(self, virt_page_num, page_offset):
        if self.page_table[virt_page_num]['valid'] == 0:
            # page isnt in the table, lets add it
            self.page_table[virt_page_num]['valid'] = 1
            self.page_table[virt_page_num]['physical_page'] = virt_page_num
            phys_addr = (self.page_table[virt_page_num]['physical_page']<<self.page_bits)+page_offset
            return False, phys_addr
        else:
            # page is already here
            phys_addr = (self.page_table[virt_page_num]['physical_page']<<self.page_bits)+page_offset
            return True, phys_addr

    # Figure out allowed color bits from allowed sets and total sets
    def __get_colors(self, allowed_sets, color_bits, set_bits):
        lowest_set = allowed_sets[0]
        highest_set = allowed_sets[1]
        low_color = (lowest_set)>>(set_bits - color_bits)
        high_color = (highest_set)>>(set_bits - color_bits)
        colors = list(range(low_color,high_color+1))
        return colors

    def __build_color_mask(self, color_bits, set_bits):
        mask = ''
        for i in range(color_bits):
            mask += '1'
        # for i in range(set_bits - color_bits):
        #     mask += '0'
        return int(mask,2)
