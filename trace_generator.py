#!/usr/bin/env python3

# Trace Generator for ECE5984 Cache Project
# Generates a trace file


import random
import pprint

# Script Wide Values
rw_options = ['read', 'write']
#addr_options = range(0,0xffffffff+1)  # must be range otherwise will fill mem
crit_options = ['hi', 'low']
#prior_options = range(0,4)
#taskid_options = range(0,4)
# 128M, 256M, 512M,
addr_range_options = [0x08000000, 0x10000000, 0x20000000]

#options_list = [rw_options, procid_options]

# task map is dict with key = taskid, value = memory space
def build_task_map(num_tasks):
    task_map = {}
    for i in range(num_tasks):
        task_map[i] = random.choice(addr_range_options)
    return task_map

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

# Build random trace
def build_random_trace(length, task_map):
    trace = []
    for i in range(length):
        trace.append(build_rand_element(task_map))
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
    format_str = "{} {:x},"
    for i in task_map.keys():
        output += format_str.format(i,task_map[i])
    return output[:-1] + "\n"

# Do everything
def main():
    # Create task_map dict
    task_map = build_task_map(4)
    trace = build_random_trace(25, task_map)
    task_addrs = pretty_task_map(task_map)
    output = pretty_trace(trace)
    f = open('sample.txt','w')
    f.write(task_addrs)
    f.write(output)
    f.close()



if __name__ == '__main__':
    main()
