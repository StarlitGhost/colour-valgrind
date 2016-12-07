import re
from collections import OrderedDict

from colorama import Fore, Back, Style

line_regexes = OrderedDict()
def line_regex(regex, func):
    line_regexes[re.compile(regex)] = func

def prefix(match):
    return Fore.LIGHTBLACK_EX + match.group('prefix') + Fore.RESET

def byat(match):
    output = prefix(match)
    output += Fore.YELLOW + match.group('byat')
    output += Fore.RESET + match.group('func')
    
    if match.group('loc'):
        loc = match.group('loc')
        loc_m = re.match(r"^(?P<file>[^:]+):(?P<line>\d+)$", match.group('loc'))
        if loc_m:
            loc = Fore.LIGHTWHITE_EX + loc_m.group('file')
            loc += Fore.LIGHTBLACK_EX + ":"
            loc += Fore.MAGENTA + loc_m.group('line')
        loc_m = re.match(r"^(?P<in>in\s+)(?P<lib>.*\.(?:a|so|dylib|dll))$", match.group('loc'))
        if loc_m:
            loc = Fore.RESET + loc_m.group('in')
            loc += Fore.RED + loc_m.group('lib')
        output += Fore.LIGHTBLACK_EX + " (" + Fore.RESET + loc + Fore.LIGHTBLACK_EX + ")"

    output += Style.RESET_ALL
    return output
line_regex(r"^(?P<prefix>==\d+== +)(?P<byat>(?:by|at) 0x[A-F0-9]+: )(?P<func>.+?)(?: \((?P<loc>[^\)]+)\))?$", byat)

def summary(match):
    output = prefix(match)
    header = match.group('header')
    if re.match(r"^[A-Z ]+:$", header):
        output += Fore.LIGHTGREEN_EX + header
    else:
        output += Fore.GREEN + header
    text = re.sub(r"([0-9][0-9,\.]*)", Fore.MAGENTA + r"\1" + Fore.RESET, match.group('text'))
    output += Fore.RESET + text

    output += Style.RESET_ALL
    return output
line_regex(r"^(?P<prefix>==\d+== )(?P<header>.+?:)(?P<text>.*)$", summary)

def error(match):
    output = prefix(match)
    output += Fore.LIGHTRED_EX + Style.BRIGHT + match.group('error')

    output += Style.RESET_ALL
    return output
line_regex(r"^(?P<prefix>==\d+== )(?P<error>\S.+)$", error)

def info(match):
    output = prefix(match)
    output += Fore.LIGHTBLUE_EX + Style.BRIGHT + match.group('info')

    output += Style.RESET_ALL
    return output
line_regex(r"^(?P<prefix>==\d+==  )(?P<info>\S.+)$", info)

def blank(match):
    output = prefix(match)
    return output
line_regex(r"^(?P<prefix>==\d+== *)$", blank)

PROGRAM = 0
VALGRIND = 1
prev_output = VALGRIND
curr_output = VALGRIND

def get_terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def colourValgrind(output):
    # print break lines between program and valgrind outputs
    global prev_output, curr_output
    prev_output = curr_output

    if not re.match(r"^==\d+==", output):
        curr_output = PROGRAM
    else:
        curr_output = VALGRIND

    if curr_output != prev_output:
        print Fore.LIGHTBLACK_EX + "="*get_terminal_size()[0] + Style.RESET_ALL

    # abort if the line isn't from valgrind
    if curr_output == PROGRAM:
        return output

    # loop through our line matchers and apply the first matching style
    for (regex, func) in line_regexes.iteritems():
        match = regex.match(output)
        if match:
            output = func(match)
            break

    return output

if __name__ == "__main__":
    print line_regexes
