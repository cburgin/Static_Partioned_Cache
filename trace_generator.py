#!/usr/bin/env python3

# Trace Generator for ECE5984 Cache Project
# Generates a trace file

import random
import pprint
import sys

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
    num_slices = 512
    slice_size = int(task_map[taskid] / num_slices)
    base_addr = random.choice(range(num_slices))*slice_size
    element_list = []
    for i in range(random.choice(range(1,128))):
        element = []
        element.append(random.choice(rw_options))
        element.append(taskid)
        element.append(base_addr+((i*512) % slice_size) )
        element_list.append(element)
    return element_list


# Build random element of a trace - single line entry
def build_rand_element(task_map):
    element = []
    # Make an entry with a random R/W, taskid, virt_addr
    # choose R/W
    element.append(random.choice(rw_options))
    # choose taskid
    tmp_taskid = random.choice(range(len(task_map)))
    element.append(tmp_taskid)
    # choose addr from the selected task id's range
    element.append(random.choice(range(task_map[tmp_taskid])))
    return element

def build_opposite_element(element):
    if element[0] == 'read':
        return ['write', element[1], element[2]]
    else:
        return ['read', element[1], element[2]]

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

def task_map_from_string(map_string):
    map_list = map_string.split(',')
    task_map = {}
    taskid = 0
    for map_pair in map_list:
        map_pair = map_pair.split('-')
        for i in range(int(map_pair[0])):
            task_map[taskid]=int(map_pair[1],16)
            taskid += 1
    return task_map

#Generates a trace file and returns a file object
def generate_trace(memory_size, trace_length, task_id, filename):
    #Parse the task ID mapping and generate a task map
    task_map = task_map_from_string(task_id)

    #Generate the trace list
    trace = build_random_trace(trace_length, task_map)
    task_addrs = pretty_task_map(task_map)
    output = pretty_trace(trace)

    #Write to file
    f = open('traces/'+filename+'.trace', 'w')
    out_file = task_addrs + output
    f.write(out_file)
    f.close
    return out_file

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
