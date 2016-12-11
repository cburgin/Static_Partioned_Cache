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
        self.tag_bits = int(math.log(self.memory_size,2))-self.set_bits-self.offset_bits
        self.page_bits = int(math.log(self.page_size,2))
        self.color_bits = (self.set_bits + self.offset_bits) - self.page_bits
        self.color_mask = self.__build_color_mask(color_bits, set_bits)
        self.virt_page_num_bits = int(math.log(self.memory_size,2)) - self.offset_bits

        # Get colors for this PageTable
        self.colors = self.__get_colors(self.allowed_sets, self.color_bits, self.set_bits)

        self.page_size = page_size
        self.page_table = [{'valid':0,'physical_page':0} for x in range(self.memory_size)]

    def translate(virt_addr):
        # Get virtual page and offset
        virt_page_num = virt_addr >> self.offset_bits
        virt_page_color = self.__get_virt_page_color(virt_page_num)

    def __get_virt_page_color(virt_page_num):
        

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
