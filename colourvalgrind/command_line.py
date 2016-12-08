#!/usr/bin/env python

from colourvalgrind import colour_valgrind

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",
                        help="valgrind log file to run through colour filters",
                        required=True)
    args = parser.parse_args()

    with open(args.input) as f:
        for line in f:
            print(colour_valgrind(line))

if __name__ == "__main__":
    main()
