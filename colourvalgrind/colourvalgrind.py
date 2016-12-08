#!/usr/bin/env python

import re
from collections import OrderedDict

from colorama import Fore, Back, Style


_line_filters = OrderedDict()

def _register_filter(obj):
    _line_filters[obj.regex] = obj

class Filter(object):
    regex = None

    def __init__(self):
        assert self.regex is not None, (
                "'{}' filter not implemented".format(self.__name__))
        _register_filter(self)

    def filter(self, match):
        assert False, "'{}' filter not implemented".format(self.__name__)

def init_filters():
    for f in Filter.__subclasses__():
        f()

def _prefix(match):
    return Fore.LIGHTBLACK_EX + match.group('prefix') + Fore.RESET

class ByAt(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== +)"
                       r"(?P<byat>(?:by|at) 0x[A-F0-9]+: )"
                       r"(?P<func>.+?)"
                       r"(?: \((?P<loc>[^\)]+)\))?"
                       r"$")

    def filter(self, match):
        output = _prefix(match)
        output += Fore.YELLOW + match.group('byat')
        output += Fore.RESET + match.group('func')

        if match.group('loc'):
            loc = match.group('loc')
            loc_m = re.match(r"^(?P<file>[^:]+):(?P<line>\d+)$", loc)
            if loc_m:
                loc = Fore.LIGHTWHITE_EX + loc_m.group('file')
                loc += Fore.LIGHTBLACK_EX + ":"
                loc += Fore.MAGENTA + loc_m.group('line')
            loc_m = re.match(r"^(?P<in>in\s+)"
                             r"(?P<lib>.*\.(?:a|so|dylib|dll)"
                                r"(?:(?:\.[0-9])+)?)$",
                             loc)
            if loc_m:
                loc = Fore.RESET + loc_m.group('in')
                loc += Fore.RED + loc_m.group('lib')
            output += Fore.LIGHTBLACK_EX + " ("
            output += Fore.RESET + loc
            output += Fore.LIGHTBLACK_EX + ")"

        output += Style.RESET_ALL
        return output

class Summary(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== )"
                       r"(?P<header>.+?:)"
                       r"(?P<text>.*)"
                       r"$")

    def filter(self, match):
        output = _prefix(match)
        header = match.group('header')
        if re.match(r"^[A-Z ]+:$", header):
            output += Fore.LIGHTGREEN_EX + header
        else:
            output += Fore.GREEN + header
        text = re.sub(r"\b([0-9][0-9,\.]*)\b",
                      Fore.MAGENTA + r"\1" + Fore.RESET,
                      match.group('text'))
        output += Fore.RESET + text

        output += Style.RESET_ALL
        return output

class Error(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== )"
                       r"(?P<error>\S.+)"
                       r"$")

    def filter(self, match):
        output = _prefix(match)
        output += Fore.LIGHTRED_EX + Style.BRIGHT + match.group('error')

        output += Style.RESET_ALL
        return output

class Info(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+==  )"
                       r"(?P<info>\S.+)"
                       r"$")

    def filter(self, match):
        output = _prefix(match)
        output += Fore.LIGHTBLUE_EX + Style.BRIGHT + match.group('info')

        output += Style.RESET_ALL
        return output

class Blank(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== *)"
                       r"$")

    def filter(self, match):
        output = _prefix(match)
        return output

_PROGRAM = 0
_VALGRIND = 1
_prev_output = _VALGRIND
_curr_output = _VALGRIND

def _get_terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def colour_valgrind(output):
    # print break lines between program and valgrind outputs
    global _prev_output, _curr_output
    _prev_output = _curr_output

    if not re.match(r"^==\d+==", output):
        _curr_output = _PROGRAM
    else:
        _curr_output = _VALGRIND

    if _curr_output != _prev_output:
        print Fore.LIGHTBLACK_EX + "="*_get_terminal_size()[0] + Style.RESET_ALL

    # abort if the line isn't from valgrind
    if _curr_output == _PROGRAM:
        return output

    # loop through our line matchers and apply the first matching style
    for (regex, obj) in _line_filters.iteritems():
        match = regex.match(output)
        if match:
            output = obj.filter(match)
            break

    return output

init_filters()
