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

# Create a translation table based on mem size and task_map
def build_translation_table(task_map, mem_size):
    total_task_mem = 0
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

# Run a physical trace through the cache, report metrics
def run_trace(trace):
    import cache
    results = {}
    myCache = cache.cache()

    # for every element in the trace
    #   1. grab ID
    #   2. pass RW and Addr to cache
    #   3. Get hit/miss
    #   4. Record Results
    for element in trace:
        taskid = element[0]
        if taskid not in results.keys():
            results[taskid] = {'total':0,'hit':0,'miss':0}
        results[taskid]['total'] += 1

        if myCache.simulate_element(element[1:]):
            results[taskid]['hit'] += 1
        else
            results[taskid]['miss'] += 1

    return results



# Kick off the show
def main():
    # Parse input trace
    task_map,trace = parse_trace_file('sample.txt')

    # Build translation table
    translate_table = build_translation_table(task_map,0x80000000)

    # Use translation table to make physical trace
    phys_trace = translate_trace_file(translate_table, trace)

    # Run trace through cache
    results = run_trace(phys_trace)





if __name__ == '__main__':
    main()
