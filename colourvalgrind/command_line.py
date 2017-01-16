#!/usr/bin/env python

from colourvalgrind import colour_valgrind

import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-t", "--test",
                        help="valgrind log file to run through colour filters",
                        default=None)
    args, valgrind_args = parser.parse_known_args()

    if args.test:
        with open(args.test) as f:
            for line in f:
                print(colour_valgrind(line))
    else:
        cmd = ['valgrind']
        cmd.extend(valgrind_args)
        s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(s.stdout.readline, b''):
            print(colour_valgrind(line.rstrip(b'\n').decode('utf-8')))

        sys.exit(s.returncode)

if __name__ == "__main__":
    main()
