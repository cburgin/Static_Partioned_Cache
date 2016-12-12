#! /usr/bin/env python3

# This is the main translator function for a given trace
# Requires the cache object to actually run the cache

# Program Flow
# Read in trace file
#   Parse out task information
#
# Create Translation Table For Tasks
# Translate Trace File to Physical trace
#
# Instantiate Cache
#
# Process Physical trace
#   Update Statistics

# Read out stats from cache
# Print report

import pprint
import copy
import cache
import pagetable

# parse the trace file from generator
# return dict task_map and list trace
def parse_trace_file(filename):
    f = open(filename,'r')
    data = f.readlines()

    # Parse task_map from line 0
    task_map = {}
    task_data = data[0]
    task_data = task_data.strip()
    task_data = task_data.split(',')
    for i in task_data:
        i = i.split()
        task_map[i[0]] = int(i[1],16)

    trace = []
    # Parse trace from lines 1-n
    for line in data[1:]:
        line = line.strip()
        trace.append(line.split(','))
        trace[-1][2] = int(trace[-1][2],16)
    return task_map,trace

# Parse the trace
def parse_trace(data):
    # Parse task_map from line 0
    data = data.strip().split('\n')
    task_map = {}
    start = 0
    # old style
    if data[0][0:2] == '0 ':
        start = 1
        task_data = data[0]
        task_data = task_data.strip()
        task_data = task_data.split(',')
        for i in task_data:
            i = i.split()
            task_map[i[0]] = int(i[1],16)

    trace = []
    # Parse trace from lines 1-n
    for line in data[start:]:
        line = line.strip()
        trace.append(line.split(','))
        trace[-1][2] = int(trace[-1][2],16)
    return task_map,trace

# Create a translation table based on mem size and task_map
def build_translation_table(task_map, mem_size, shared):
    total_task_mem = 0
    if shared:
        for value in task_map.values():
            if value > mem_size:
                print('ERROR TOO MUCH MEM REQUESTED')
                return 0
        translate_table = {}
        for task,size in task_map.items():
            translate_table[task] = 0
    else:
        for value in task_map.values():
            total_task_mem += value
        if total_task_mem > mem_size:
            print('ERROR TOO MUCH MEM REQUESTED')
            return 0

        avail_location = 0
        translate_table = {}
        for task,size in task_map.items():
            translate_table[task] = avail_location
            avail_location = avail_location + size
    return translate_table

def translate_trace_file(translate_table, virt_trace):
    # modify each element in trace
    phys_trace = []
    for element in virt_trace:
        phys_element = []
        rw = element[0]
        taskid = element[1]
        virt_addr = element[2]
        # Keep taskID for reference - only pass [1:] to cache
        phys_element.append(taskid)
        # R/W doesn't change
        phys_element.append(rw)
        # Phys Addr = Virt Addr + translate offset
        phys_element.append(virt_addr+translate_table[taskid])
        phys_trace.append(phys_element)
    return phys_trace

def run_trace_with_page_table(trace, myCache, page_tables, task_map, shared):
    results ={}
    partition_previous_taskid = {}
    preemption_count = 0
    # for every element in the trace
    #   1. grab ID
    #   2. convert addr with page table
    #   3. invalidate cache line if PT says so
    #   4. pass RW and Addr to cache
    #   5. Get hit/miss
    #   6. Record Results
    for index,element in enumerate(trace):
        if (index % 10000) == 0:
            print('still working...', index)
        taskid = int(element[0])
        # If tasks are sharing a partition, preemption occurs - invalidate partition
        # if (taskid != previous_taskid) and (task_map[taskid] == task_map[previous_taskid]):
        #     myCache.mark_partition_invalid(task_map[taskid])
        #     previous_taskid = taskid
        #     preemption_count += 1

        # Check if tasks are sharing a partition by looking at their colors
        if tuple(page_tables[taskid].colors) not in partition_previous_taskid.keys():
            # If a color set has never been seen add it to the tracker
            partition_previous_taskid[tuple(page_tables[taskid].colors)] = taskid
            previous_taskid = taskid
        else:
            # If a color set has been seen, see if it was previously accessed by same task
            if (taskid != partition_previous_taskid[tuple(page_tables[taskid].colors)]):
                # If it is a different task, we invalidate the cache cause preemption occurred
                for tid in task_map.keys():
                    if page_tables[tid].colors == page_tables[taskid].colors:
                        myCache.mark_partition_invalid(task_map[tid])
                previous_taskid = taskid
                partition_previous_taskid[tuple(page_tables[taskid].colors)] = taskid
                preemption_count += 1


        # Create a results entry if one doesn't exist
        if taskid not in results.keys():
            results[taskid] = {'total':0,'hit':0,'miss':0,'misspairs':{}, 'marked_invalid':0}
        results[taskid]['total'] += 1
        # Use the page table to update the address with the physical address
        valid,element[2] = page_tables[taskid].translate(element[2])
        # If the addr is valid in the page table -- go normally
        if valid:
            hitmiss_result,curr_set,curr_tag = myCache.simulate_element(element[1:])
        else:
            # If the addr was invalid in the page table, invalidate the cache line
            myCache.mark_line_invalid(element[2])
            hitmiss_result,curr_set,curr_tag = myCache.simulate_element(element[1:])
            results[taskid]['marked_invalid'] += 1

        if hitmiss_result:
            results[taskid]['hit'] += 1
        else:
            results[taskid]['miss'] += 1
            if (curr_set,curr_tag) in results[taskid]['misspairs'].keys():
                results[taskid]['misspairs'][(curr_set,curr_tag)] += 1
            else:
                results[taskid]['misspairs'][(curr_set,curr_tag)] = 1

    print('Preemption count: ', preemption_count)
    print('partition_previous_taskid')
    pprint.pprint(partition_previous_taskid)
    return results

# Run a physical trace through the cache, report metrics
def run_trace(trace, myCache):
    results = {}

    # for every element in the trace
    #   1. grab ID
    #   2. pass RW and Addr to cache
    #   3. Get hit/miss
    #   4. Record Results
    for element in trace:
        taskid = element[0]
        if taskid not in results.keys():
            results[taskid] = {'total':0,'hit':0,'miss':0,'misspairs':{}}
        results[taskid]['total'] += 1
        hitmiss_result,curr_set,curr_tag = myCache.simulate_element(element[1:])
        # if curr_tag > 0x100000:
        #     print(element, curr_set, curr_tag)
        if hitmiss_result:
            results[taskid]['hit'] += 1
        else:
            results[taskid]['miss'] += 1
            if (curr_set,curr_tag) in results[taskid]['misspairs'].keys():
                results[taskid]['misspairs'][(curr_set,curr_tag)] += 1
            else:
                results[taskid]['misspairs'][(curr_set,curr_tag)] = 1

    return results

# Run a physical trace through the cache, report metrics
# This method does a premption context switch whenver the taskid changes
# This will probably significantly reduce preformance
def run_shared_trace(trace, myCache):
    results = {}
    current_taskid = 0

    # for every element in the trace
    #   1. grab ID
    #   2. pass RW and Addr to cache
    #   3. Get hit/miss
    #   4. Record Results
    num_context_switches = 0
    for element in trace:
        taskid = element[0]
        # Did a context switch occur?
        if taskid != current_taskid:
            myCache.mark_invalid()
            current_taskid = taskid
            num_context_switches += 1

        if taskid not in results.keys():
            results[taskid] = {'total':0,'hit':0,'miss':0,'misspairs':{}}
        results[taskid]['total'] += 1
        hitmiss_result,curr_set,curr_tag = myCache.simulate_element(element[1:])
        if hitmiss_result:
            results[taskid]['hit'] += 1
        else:
            results[taskid]['miss'] += 1
            if (curr_set,curr_tag) in results[taskid]['misspairs'].keys():
                results[taskid]['misspairs'][(curr_set,curr_tag)] += 1
            else:
                results[taskid]['misspairs'][(curr_set,curr_tag)] = 1
    print("number of context switches: ", num_context_switches)
    return results

def make_stats(results):
    stats = ''
    header = 'TaskID Requests     Hits   Misses   Hit Rate\n'
    format_str = '{:>6} {:>8} {:>8} {:>8} {:>10.4f}\n'
    stats = stats + header
    # sorted(results.key(), key=int) returns the dict keys in integer order
    # keys are taskids
    for key in sorted(results.keys(), key=int):
        stats = stats + format_str.format(key, results[key]['total'], results[key]['hit'], results[key]['miss'], results[key]['hit']/float(results[key]['total']))
    return stats

def make_miss_stats(results):
    print("Number of unique curr_set,curr_tag pairs that missed per taskid")
    for key in sorted(results.keys(), key=int):
        ordered_miss_pairs_by_set = sorted(results[key]['misspairs'].keys())
        print(key, len(ordered_miss_pairs_by_set), ordered_miss_pairs_by_set[0], ordered_miss_pairs_by_set[-1], results[key]['marked_invalid'])

def new_parse(input_trace):
    return input_trace

def build_page_tables(task_map, memory_size, cache_size, block_size, mapping, page_size):
    page_tables = {}
    for taskid in task_map.keys():
        # allowed_sets is the data in task_map dict at key taskid
        page_tables[taskid] = pagetable.PageTable(memory_size, cache_size, block_size,
                                                    mapping, task_map[taskid], page_size)
    return page_tables

#Translates the virtual task address space into the physical address space
def generate_translation(task_map,memory_size, cache_size, block_size, mapping,
                            input_trace, shared, page_size):
    #Parse the File
    print('Parsing File...')
    empty_task_map,trace = parse_trace(input_trace)
    print('task map from trace', task_map)
    # if task_map != {}:
    #     #Build the translation table
    #     print('Building translation table...')
    #     translate_table = build_translation_table(task_map, memory_size, shared)
    #
    #     #Use translation table to make physical trace
    #     print('Building physical trace...')
    #     phys_trace = translate_trace_file(translate_table, trace)
    # else:
    #     phys_trace = trace

    phys_trace = trace
    # Create cache from perameters
    print('Building Cache...')
    myCache = cache.cache(cache_size, block_size, mapping)
    print('Cache Stats: Size: ', myCache.cacheSize, 'Block Size: ', myCache.blockSize, 'Mapping: ', myCache.cacheMap)

    print('Building Page Tables (one per task)...')
    page_tables = build_page_tables(task_map, memory_size, cache_size, block_size, mapping, page_size)

    for taskid in page_tables.keys():
        print(taskid, page_tables[taskid].allowed_sets, page_tables[taskid].colors)
    # Run trace through cache
    print('Running trace...')

    results = run_trace_with_page_table(phys_trace, myCache, page_tables, task_map, shared)
    print(results.keys())
    print('Making stats...')
    stats = make_stats(results)
    print(stats)
    make_miss_stats(results)
    print('Partition invalidates', myCache.partition_invalidates)
    #print('Writing File')
    #print('Filename: '+filename)
    #write_stats_file('results/'+filename+'.result', stats)
    return stats

# # Kick off the show
# def main():
#     # Parse input trace
#     print('Parsing File...')
#     filename = 'set_trace_8_MC_2500.txt'
#     task_map,trace = parse_trace_file(filename)
#
#     # Build translation table
#     system_ram = 0x100000000    # 4G RAM for 32b system
#     print('Building translate table...')
#     translate_table = build_translation_table(task_map,system_ram)
#
#     # Use translation table to make physical trace
#     print('Building physical trace...')
#     phys_trace = translate_trace_file(translate_table, trace)
#
#     # Run trace through cache
#     print('Running trace...')
#     results = run_trace(phys_trace)
#
#     pprint.pprint(results)
#     print('Making stats...')
#     stats = make_stats(results)
#     print(stats)
#     print('Writing File')
#     write_stats_file(filename, stats)
#
#
#
# if __name__ == '__main__':
#     main()
