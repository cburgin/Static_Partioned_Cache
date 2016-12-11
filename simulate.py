#!/usr/bin/env python3

#Simulates the entire system

import argparse
import random
import trace_generator
import translator

def auto_int(x):
    return int(x,0)

def main():
    #Parse the command line arguments provided at run time.
    parser = argparse.ArgumentParser(description='Simulates the static partioned cache.')
    parser.add_argument('-c', '--cachesize', dest='cache_size', metavar='C',
                        type=int, nargs='?', default=131072,
                        help='provide the cache size in bytes. Default=131072.')
    parser.add_argument('-b', '--blocksize', dest='block_size', metavar='B',
                        type=int, nargs='?', default=32,
                        help='provide the cache block size in bytes. Default=32.')
    parser.add_argument('-m', '--mapping', dest='mapping', metavar='M',
                        type=int, nargs='?', default=1,
                        help='provide the cache mapping. Default=1.')
    parser.add_argument('-r', '--memsize', dest='memory_size', metavar='R',
                        type=auto_int, nargs='?', default=0x100000000,
                        help='provide the size of the memory. Default=4GB.')
    parser.add_argument('-l', '--length', dest='trace_length', metavar='L', type=int,
                        nargs='?', default=2000,
                        help='provide the length of the simulated trace. Default=2000.')
    parser.add_argument('-t', '--taskids', dest='task_IDs', metavar='T',
                        nargs='?', default='8-0x2000000',
                        help='provide the task mapping. Default=8-0x2000000.')
    parser.add_argument('-n', '--name', dest='filename', metavar='N',
                        nargs='?', default='trace_'+str(random.randint(0,10000)),
                        help='provide a filename. Default=trace_(random num)).')
    parser.add_argument('-s', '--shared', dest='shared',
                        default=False, action='store_true',
                        help='Add Flag to make the cache shared')
    parser.add_argument('-a', '--tracealgorithm', dest='trace_alg', metavar='A',
                        nargs='?', default='std',
                        help='Choose the trace generator algorithm: std, evil')
    parser.add_argument('-x', '--use-existing-trace', dest='existing',
                        default=False, action='store_true',
                        help='Add Flag to make the cache shared')

    #Parse the input arguments
    args = parser.parse_args()
    print(args)

    if args.existing:
        trace = read_trace_file(args.filename)
    else:
        #Generate the traces
        trace = trace_generator.generate_trace(args.memory_size, args.trace_length, args.task_IDs, args.filename, args.trace_alg, args.shared)

    #Translate the virtual task addresses to the physical memory space. AND simulate the cache
    translator.generate_translation(args.memory_size, trace, args.filename, args.shared)


def read_trace_file(filename):
    f = open(filename, 'r')
    return f.read()

if __name__ =='__main__':
    main()
