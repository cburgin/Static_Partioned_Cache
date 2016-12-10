#Simulates the entire system

import argparse

def main():
    parser = argparse.ArgumentParser(description='Simulates the static partioned cache.')
    parser.add_argument('cache_size', metavar='C', type=int, nargs='?', default=131072,
                        help='provide the cache size in bytes. Default=131072.')
    parser.add_argument('block_size', metavar='B', type=int, nargs='?', default=32,
                        help='provide the cache block size in bytes. Default=32.')
    parser.add_argument('mapping', metavar='M', type=int, nargs='?', default=1,
                        help='provide the cache mapping. Default=1.')
    parser.add_argument('memory_size', metavar='R', type=int, nargs='?', default=0x100000000,
                        help='provide the size of the memory. Default=4GB.')

    args = parser.parse_args()
    print(args)

if __name__ =='__main__':
    main()
