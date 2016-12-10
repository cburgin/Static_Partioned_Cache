#!/usr/bin/env python3

#Simulates the entire system

import argparse
import random
import trace_generator

def main():
    #Parse the command line arguments provided at run time.
    parser = argparse.ArgumentParser(description='Simulates the static partioned cache.')
    parser.add_argument('cache_size', metavar='C', type=int, nargs='?', default=131072,
                        help='provide the cache size in bytes. Default=131072.')
    parser.add_argument('block_size', metavar='B', type=int, nargs='?', default=32,
                        help='provide the cache block size in bytes. Default=32.')
    parser.add_argument('mapping', metavar='M', type=int, nargs='?', default=1,
                        help='provide the cache mapping. Default=1.')
    parser.add_argument('memory_size', metavar='R', type=int, nargs='?', default=0x100000000,
                        help='provide the size of the memory. Default=4GB.')
    parser.add_argument('trace_length', metavar='L', type=int, nargs='?', default=2000,
                        help='provide the length of the simulated trace. Default=2000.')
    parser.add_argument('task_IDs', metavar='T', nargs='?', default='8-0x2000000',
                        help='provide the task mapping. Default=8-0x2000000.')
    parser.add_argument('filename', metavar='N', nargs='?', default='trace_'+str(random.randint(0,10000)),
                        help='provide a filename. Default=trace_(random num)).')

    #Parse the input arguments
    args = parser.parse_args()
    print(args)

    trace_generator.generate_trace(args.memory_size, args.trace_length, args.task_IDs, args.filename)

    #Run the code.

if __name__ =='__main__':
    main()
