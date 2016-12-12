#!/usr/bin/env python3

# Trace Generator for ECE5984 Cache Project
# Generates a trace file

import random
import pprint
import sys
import math

# Script Wide Values
rw_options = ['read', 'write']
#addr_options = range(0,0xffffffff+1)  # must be range otherwise will fill mem
crit_options = ['hi', 'low']
#prior_options = range(0,4)
#taskid_options = range(0,4)
# 16M, 32M, 64M, 128M, 256M, 512M,
#addr_range_options = [0x01000000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x20000000]
# All 512M
#addr_range_options = [0x20000000]
# 1 4G
# addr_range_options = [0x100000000]
# #options_list = [rw_options, procid_options]
#
# # task maps for specific cases
# mc_task_map = {0: 0x40000000, 1: 0x40000000, 2: 0x20000000, 3: 0x20000000, \
#                 4: 0x10000000, 5: 0x10000000, 6: 0x10000000, 7: 0x10000000}

# task map is dict with key = taskid, value = memory space
def build_task_map(num_tasks):
    task_map = {}
    for i in range(num_tasks):
        task_map[i] = random.choice(addr_range_options)
    return task_map

def build_rand_element_list(task_map):
    taskid = random.choice(range(len(task_map)))
    num_slices = 64
    slice_size = int(task_map[taskid] / num_slices)
    base_addr = random.choice(range(num_slices))*slice_size
    element_list = []
    for i in range(random.choice(range(1,32))):
        element = []
        element.append(random.choice(rw_options))
        element.append(taskid)
        element.append(base_addr+(i))
        element_list.append(element)
    return element_list

#Builds a set random element list
def build_set_evil_element_list(task_map, cache_size, block_size, mapping, memory_size):
    # Get the cache geometry
    num_sets = calc_num_sets(cache_size, block_size, mapping)
    set_bits = int(math.log(num_sets,2))
    offset_bits = int(math.log(block_size,2))
    tag_bits = int(math.log(memory_size,2))-set_bits-offset_bits

    # Calculate all of the task partition sizes
    task_size_list = []     # List of all of the sizes.
    for taskid in task_map.keys():
        # Grab low and high values
        low_set = task_map[taskid][0]
        high_set = task_map[taskid][1]
        task_size_list.append((high_set - low_set)+1)

    # Get the minimum task space size
    max_size = max(task_size_list)

    # Calculate the operations to occur in a trace
    element_list = []
    for taskid in task_map.keys():
        # Loop for the max task size and reads and write to the cache
        low_set = task_map[taskid][0]
        high_set = task_map[taskid][1]
        curr_task_size = (high_set - low_set)+1
        #Perform reads first
        for i in range(max_size):
            element = []
            #perform reads first.
            element.append(taskid)
            element.append(rw_options[0])
            curr_offset = 0
            curr_set = i % curr_task_size
            curr_tag = i // curr_task_size
            #Build address
            curr_set = curr_set + low_set #Add the current set offset
            address = (curr_tag << set_bits) + curr_set #Shift in the tag
            address = (address << offset_bits) + curr_offset #Shift in the set and add offset
            element.append(address)
            element_list.append(element)

        # Perform writes after the reads
        for i in range(max_size):
            element = []
            #perform reads first.
            element.append(taskid)
            element.append(rw_options[1])
            curr_offset = 0
            curr_set = i % curr_task_size
            curr_tag = i // curr_task_size
            #Build address
            curr_set = curr_set + low_set #Add the current set offset
            address = (curr_tag << set_bits) + curr_set #Shift in the tag
            address = (address << offset_bits) + curr_offset #Shift in the set and add offset
            element.append(address)
            element_list.append(element)

    return element_list

def build_evil_element_list(task_map):
    offset = 2**5  #1M
    element_list = []
    for taskid in range(len(task_map)):
        base_addr = random.choice(range(task_map[taskid]))
        for i in range(0,512*8,8):
            element = []
            element.append(random.choice(rw_options))
            element.append(taskid)
            element.append(base_addr+i)
            element_list.append(element)
            element_list.append(build_opposite_element(element))
            # make 512 offset r/w
            offset_element = build_offset_element(element,offset)
            element_list.append(offset_element)
            element_list.append(build_opposite_element(offset_element))
            if i == 0:
                tag_base = (base_addr / 8) / (4096 / 8)
                tag_offset = ((base_addr+offset) / 8) / (4096 / 8)
                #print("tag_base: ",tag_base, "tag_offset",tag_offset)
    return element_list

def build_virt_set_element_list(task_map, cache_size, block_size, mapping, memory_size):
    element_list = []
    taskid = random.choice(list(task_map.keys()))
    num_instructions = random.choice(range(1,32))
    addr = random.choice(range(memory_size))
    for i in range(num_instructions):
        element = []
        element.append(taskid)
        element.append(random.choice(rw_options))
        element.append(addr+i)
        element_list.append(element)
    return element_list

# Build a list of elements based on the current cache and tasks
def build_set_element_list(task_map, cache_size, block_size, mapping, memory_size):
    element_list=[]
    # Get the cache geometry
    num_sets = calc_num_sets(cache_size, block_size, mapping)
    set_bits = int(math.log(num_sets,2))
    offset_bits = int(math.log(block_size,2))
    tag_bits = int(math.log(memory_size,2))-set_bits-offset_bits
    # Pick a task for this element_list
    taskid = random.choice(list(task_map.keys()))
    # Get the allowed sets (color) of that task
    low_set = task_map[taskid][0]
    high_set = task_map[taskid][1]
    # Pick a number of instructions (sequential) for this element_list
    num_instructions = random.choice(range(1,32))
    # Build the base address, make it fall in this task's partition
    base_addr = random.choice(range(2**tag_bits))
    curr_set = random.choice(range(low_set,high_set+1))
    offset = random.choice(range(block_size))
    # Build sequential instructions -- make sure they stay in this tasks color
    for i in range(num_instructions):
        curr_set = low_set + ((curr_set + (offset+i // block_size)) % (high_set - low_set + 1))
        offset = (offset+i) % block_size
        addr = (base_addr << set_bits) + curr_set
        addr = (addr << offset_bits) + offset
        # Build the element
        element = []
        element.append(taskid)
        element.append(random.choice(rw_options))
        element.append(addr)
        element_list.append(element)
        #element_list.append(build_opposite_element(element))
    return element_list

def build_offset_element(element,offset):
    return [element[0],element[1],element[2]+offset]

# Build random element of a trace - single line entry
# def build_rand_element(task_map):
#     element = []
#     # Make an entry with a random R/W, taskid, virt_addr
#     # choose R/W
#     element.append(random.choice(rw_options))
#     # choose taskid
#     tmp_taskid = random.choice(range(len(task_map)))
#     element.append(tmp_taskid)
#     # choose addr from the selected task id's range
#     element.append(random.choice(range(task_map[tmp_taskid])))
#     return element

def build_opposite_element(element):
    if element[0] == 'read':
        return ['write', element[1], element[2]]
    else:
        return ['read', element[1], element[2]]

def build_trace(length, task_map, trace_alg, cache_size, block_size, mapping, memory_size):
    trace_algorithm = { 'std':build_rand_element_list,
                        'evil':build_set_evil_element_list,
                        'set':build_set_element_list,
                        'virt':build_virt_set_element_list}
    trace = []
    for i in range(length):
        element_list = trace_algorithm[trace_alg](task_map, cache_size, block_size, mapping, memory_size)
        trace.extend(element_list)
        #trace.append(build_opposite_element(element))
    #random.shuffle(trace)
    return trace

# Build random trace
def build_random_trace(length, task_map):
    trace = []
    for i in range(length):
        element_list = build_rand_element_list(task_map)
        trace.extend(element_list)
        #trace.append(build_opposite_element(element))
    #random.shuffle(trace)
    return trace

# Takes trace_list and returns printable string of Trace
def print_trace(trace):
    trace_format = '{},{},{:#010x}'
    for element in trace:
        print(trace_format.format(*element))

def pretty_trace(trace):
    trace_format = '{},{},{:#010x}\n'
    output = ''
    for element in trace:
        output += trace_format.format(*element)
    return output

def pretty_task_map(task_map):
    output = ""
    format_str = "{} {:#010x},"
    for i in task_map.keys():
        output += format_str.format(i,task_map[i])
    return output[:-1] + "\n"

def calc_num_sets(cache_size, block_size, mapping):
    # Figure out cache geometry
    num_blocks = cache_size // block_size
    if mapping == 0:
        mapping = num_blocks
    num_sets = cache_size // (mapping * block_size)
    return num_sets

def task_map_from_string(map_string, shared, memory_size, cache_size, block_size, mapping):
    map_list = map_string.split(',')
    task_map = {}
    taskid = 0
    num_sets = calc_num_sets(cache_size, block_size, mapping)

    # Parse string - get relative memory per task
    for map_pair in map_list:
        map_pair = map_pair.split('-')
        for i in range(int(map_pair[0])):
            if shared:      # In shared everyone gets the whole memory
                task_map[taskid] = 1.00   # percentage of sets they can use
            else:           # Else they go in their own slot
                task_map[taskid] = int(map_pair[1],16)/memory_size  # percentage of sets to use
            taskid += 1

    # Check mem Requests
    if not shared:
        sets_percent = 0
        for taskid in task_map.keys():
            sets_percent += task_map[taskid]
        if sets_percent > 1.00:
            print('---TOO MUCH MEM REQUESTED--- ', sets_percent)
            return 0

        base_set = 0
        for taskid in task_map.keys():
            start_set = base_set
            end_set = int(start_set + (num_sets*task_map[taskid]-1))
            base_set = end_set + 1    # next unused set
            task_map[taskid]=(start_set,end_set)
    else:
        base_set = 0
        for taskid in task_map.keys():
            # All tasks get all sets
            task_map[taskid]=(base_set,num_sets-1)

    print(task_map)
    return task_map

#Generates a trace file and returns a file object
def generate_trace(memory_size, cache_size, block_size, mapping, trace_length,
                    task_id, filename, trace_alg, shared):
    #Parse the task ID mapping and generate a task map
    task_map = task_map_from_string(task_id, shared, memory_size, cache_size, block_size, mapping)
    #Generate the trace list
    trace = build_trace(trace_length, task_map, trace_alg, cache_size, block_size, mapping, memory_size)
    #task_addrs = pretty_task_map(task_map)
    task_addrs = ''
    output = pretty_trace(trace)

    #Write to file
    f = open('traces/'+filename+'.trace', 'w')
    out_file = task_addrs + output
    f.write(out_file)
    f.close
    return task_map,out_file

# # Do everything
# def main():
#     # Create task_map dict
#     if len(sys.argv) > 3:
#         print('Wrong number of params.')
#         return 1
#     if len(sys.argv) == 3:
#         task_map = task_map_from_string(sys.argv[2])
#         filename = sys.argv[1]
#     elif len(sys.argv) == 2:
#         task_map = build_task_map(8)
#         filename = sys.argv[1]
#     else:
#         task_map = build_task_map(8)
#         filename = 'sample.txt'
#     trace = build_random_trace(2500, task_map)
#     task_addrs = pretty_task_map(task_map)
#     output = pretty_trace(trace)
#     f = open(filename,'w')
#     f.write(task_addrs)
#     f.write(output)
#     f.close()
#
#
#
# if __name__ == '__main__':
#     main()
