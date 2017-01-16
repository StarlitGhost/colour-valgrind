#!/usr/bin/env python

from collections import OrderedDict

import regex as re
import six
from colorama import Fore, Back, Style


_line_filters = OrderedDict()

def _register_filter(filt):
    _line_filters[filt.__class__.__name__] = filt

class Filter(object):
    regex = None
    priority = 0

    def __init__(self):
        self._notImplemented = (
                "'{}' filter not implemented".format(self.__class__.__name__))
        assert self.regex is not None, self._notImplemented
        _register_filter(self)

    def match(self, line):
        assert self.regex is not None, self._notImplemented
        return self.regex.match(line)

    def apply(self, match):
        assert False, self._notImplemented

    def __eq__(self, other):
        return self.regex == other.regex

    def __ne__(self, other):
        return not self.__eq__(other)

def init_filters():
    for f in Filter.__subclasses__():
        f()

def _prefix(match):
    return Fore.LIGHTBLACK_EX + match.group('prefix') + Style.RESET_ALL

class ByAt(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== +)"
                       r"(?P<byat>(?:by|at) 0x[A-F0-9]+: )"
                       r"(?P<func>.+?)"
                       r"(?: \((?P<loc>[^\)]+)\))?"
                       r"$")

    def apply(self, match):
        output = _prefix(match)
        output += Fore.YELLOW + match.group('byat')

        func = self.func_signature(match.group('func'))
        output += Style.RESET_ALL + func

        if match.group('loc'):
            loc = match.group('loc')
            loc_m = re.match(r"^(?P<file>[^:]+):(?P<line>\d+)$", loc)
            if loc_m:
                loc = Fore.LIGHTWHITE_EX + loc_m.group('file')
                loc += Fore.LIGHTBLACK_EX + ":"
                loc += Fore.MAGENTA + loc_m.group('line')
            loc_m = re.match(r"^(?P<in>in\s+)"
                             r"(?P<lib>.*\.(?:a|so|dylib|dll)"
                                r"(?:(?:\.[0-9]+)+)?)$",
                             loc)
            if loc_m:
                loc = Style.RESET_ALL + loc_m.group('in')
                loc += Fore.RED + loc_m.group('lib')
            output += Fore.LIGHTBLACK_EX + " ("
            output += Style.RESET_ALL + loc
            output += Fore.LIGHTBLACK_EX + ")"

        output += Style.RESET_ALL
        return output

    def func_signature(self, func):
        cpp_grammar = (
r"(?(DEFINE)"
r"  (?P<_ID_>               [A-Za-z_][A-Za-z0-9_]* )"
r"  (?P<_TYPENAME_>         (?: typename ) )"
r"  (?P<_CV_QUALIFIER_>     (?: const | volatile ) )"
r"  (?P<_NAMESPACE_>        (?: \:\: )?"
r"                          (?:"
r"                           (?:"
r"                            (?&_ID_) (?&_TEMPLATE_)?"
r"                            |"
r"                            \(anonymous\snamespace\)"
r"                           )"
r"                           \:\:"
r"                          )+ )"
r"  (?P<_OPERATOR_>         (?: \& | \&\& | \* | \*\* ) )"
r"  (?P<_DEPENDENT_>        (?: \:\: (?&_ID_))+ )"
r"  (?P<_TEMPLATE_>         < \s* (?&_TEMPLATE_ARGLIST_)? \s* > )"
r"  (?P<_VOID_TYPE_>        void )"
r"  (?P<_BOOL_TYPE_>        bool )"
r"  (?P<_NULLPTR_TYPE_>     nullptr_t )"
r"  (?P<_SIGN_>             (?: signed | unsigned ) )"
r"  (?P<_CHAR_TYPE_>        (?:"
r"                           (?: (?&_SIGN_) \s+ )? char"
r"                           |"
r"                           wchar_t"
r"                           |"
r"                           char\d\d_t"
r"                          ) )"
r"  (?P<_INTEGRAL_TYPE_>    (?: (?&_SIGN_) \s+ )?"
r"                          (?:"
r"                           int"
r"                           |"
r"                           (?: short | long | long \s+ long )"
r"                           |"
r"                           (?: short | long | long \s+ long ) \s+ int"
r"                          ) )"
r"  (?P<_FLOAT_TYPE_>       (?: float | double | long \s+ double ) )"
r"  (?P<_FUNDAMENTAL_TYPE_> (?:"
r"                           (?&_VOID_TYPE_) | (?&_BOOL_TYPE_)"
r"                           |"
r"                           (?&_NULLPTR_TYPE_) | (?&_CHAR_TYPE_)"
r"                           |"
r"                           (?&_INTEGRAL_TYPE_) | (?&_FLOAT_TYPE_)"
r"                          ) )"
r"  (?P<_CLASS_TYPE_>       (?&_TYPENAME_)? (?&_NAMESPACE_)? (?&_ID_)"
r"                           (?&_TEMPLATE_)? (?&_DEPENDENT_)? )"
r"  (?P<_QUALIFIED_TYPE_>   (?: (?&_FUNDAMENTAL_TYPE_) | (?&_CLASS_TYPE_) )"
r"                           (?: \s+ (?&_CV_QUALIFIER_) )? )"
r"  (?P<_TYPE_>             (?: (?&_QUALIFIED_TYPE_) \s* (?&_OPERATOR_)? ) )"
r"  (?P<_TYPELIST_>         (?&_TYPE_) (?: \s* , \s* (?&_TYPE_))* )"
r"  (?P<_NUMERIC_LITERAL_>  (?:"
r"                           (?:"
r"                            [1-9][0-9]*"
r"                            |"
r"                            0[0-7]*"
r"                            |"
r"                            0[xX][0-9A-Fa-f]+"
r"                            |"
r"                            0[bB][01]+"
r"                           )"
r"                           (?: [uU] | [lL]{1,2} ){0,2}?"
r"                          ) )"
r"  (?P<_CAST_>             (?: \( (?&_TYPE_) \) ) )"
r"  (?P<_TEMPLATE_ARG_>     (?: (?&_TYPE_) | (?&_CAST_)? (?&_NUMERIC_LITERAL_) ) )"
r"  (?P<_TEMPLATE_ARGLIST_> (?&_TEMPLATE_ARG_) (?: \s* , \s* (?&_TEMPLATE_ARG_))* )"
r")")

        cpp_func_signature = re.compile(
r" (?P<PRE_FUNC_NAME>"
r"  (?P<RETURN_TYPE> (?&_TYPE_) \s )?"
r"  \s*"
r"  (?P<NAMESPACE> (?&_NAMESPACE_) )?"
r" )"
r" (?P<FUNC_NAME> (?&_ID_) )"
r" (?P<POST_FUNC_NAME>"
r"  \s*"
r"  (?:"
r"   <\s* (?P<TEMPLATE_TYPE_LIST> (?&_TEMPLATE_ARG_) (?: \s* , \s* (?&_TEMPLATE_ARG_) )* )? \s*>"
r"  )?"
r"  \s*"
r"  \(\s* (?P<PARAMETER_TYPE_LIST> (?&_TYPE_) (?: \s* , \s* (?&_TYPE_) )* (?: \s* , \s* \.\.\. )? )? \s*\)"
r"  (?:"
r"    (?P<QUALIFIER> \s+ (?&_CV_QUALIFIER_)? )"
r"  )?"
r" )"
+ cpp_grammar, re.VERBOSE)

        cpp_operator_overload = re.compile(
r" (?:"
r"   (?P<PRE_OP_NAME>"
r"    (?P<RETURN_TYPE> (?&_TYPE_) \s )?"
r"    \s*"
r"    (?P<NAMESPACE> (?&_NAMESPACE_) )?"
r"    operator"
r"   )"
r"   (?P<OP_NAME>"
r"     \W+(?=\s|\(|$)"
r"     |"
r"     \s+ (?:new|delete) \s* (?:\[\])?"
r"     |"
r"     \s+ (?&_TYPE_)"
r"   )"
r" )"
r" (?P<POST_OP_NAME>"
r"  \s*"
r"  (?:"
r"   <\s* (?P<TEMPLATE_TYPE_LIST> (?&_TEMPLATE_ARG_) (?: \s* , \s* (?&_TEMPLATE_ARG_) )* )? \s*>"
r"  )?"
r"  (?:"
r"   \(\s* (?P<PARAMETER_TYPE_LIST> (?&_TYPE_) (?: \s* , \s* (?&_TYPE_) )* )? \s*\)"
r"  )?"
r" )"
+ cpp_grammar, re.VERBOSE)

        match = cpp_func_signature.match(func)
        if match:
            # C++ functions
            if match.group('FUNC_NAME'):
                pre = match.group('PRE_FUNC_NAME')
                name = match.group('FUNC_NAME')
                post = match.group('POST_FUNC_NAME')
                func = (pre +
                        Fore.LIGHTCYAN_EX + Style.BRIGHT +
                        name +
                        Style.RESET_ALL +
                        post)
            if match.group('QUALIFIER'):
                qual = match.group('QUALIFIER')
                func = _rreplace(func, qual,
                                 Fore.LIGHTGREEN_EX +
                                 qual +
                                 Style.RESET_ALL)
        elif cpp_operator_overload.match(func):
            # operator overloads
            match = cpp_operator_overload.match(func)
            pre = match.group('PRE_OP_NAME')
            op = match.group('OP_NAME')
            post = match.group('POST_OP_NAME')
            func = (pre +
                    Fore.LIGHTCYAN_EX + Style.BRIGHT +
                    op +
                    Style.RESET_ALL +
                    post)
        elif re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", func):
            # C functions
            func = Fore.LIGHTBLUE_EX + Style.BRIGHT + func + Style.RESET_ALL
        else:
            # ???
            func = Back.RED + Fore.BLACK + func + Style.RESET_ALL

        return func

class Summary(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== )"
                       r"(?P<header>.+?:)"
                       r"(?P<text>.*)"
                       r"$")

    def apply(self, match):
        output = _prefix(match)
        header = match.group('header')
        if re.match(r"^[A-Z ]+:$", header):
            output += Fore.LIGHTGREEN_EX + header
        else:
            output += Fore.GREEN + header
        # highlight numbers
        text = re.sub(r"\b([0-9][0-9,\.]*)\b",
                      Fore.MAGENTA + r"\1" + Style.RESET_ALL,
                      match.group('text'))
        output += Style.RESET_ALL + text

        output += Style.RESET_ALL
        return output

class Error(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== )"
                       r"(?P<error>\S.+)"
                       r"$")

    def apply(self, match):
        output = _prefix(match)
        output += Fore.LIGHTRED_EX + Style.BRIGHT + match.group('error')

        output += Style.RESET_ALL
        return output

class Info(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+==  )"
                       r"(?P<info>\S.+)"
                       r"$")

    def apply(self, match):
        output = _prefix(match)
        output += Fore.LIGHTBLUE_EX + Style.BRIGHT + match.group('info')

        output += Style.RESET_ALL
        return output

class Blank(Filter):
    regex = re.compile(r"^"
                       r"(?P<prefix>==\d+== *)"
                       r"$")

    def apply(self, match):
        output = _prefix(match)
        return output

_PROGRAM = 0
_VALGRIND = 1
_prev_output = None
_curr_output = None

def _rreplace(s, old, new, count=1):
    li = s.rsplit(old, count)
    return new.join(li)

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

    if _prev_output is not None and _curr_output != _prev_output:
        print(Fore.LIGHTBLACK_EX +
              "="*_get_terminal_size()[0] +
              Style.RESET_ALL)

    # abort if the line isn't from valgrind
    if _curr_output == _PROGRAM:
        return output

    # loop through our line matchers and apply the first matching style
    for (name, filt) in six.iteritems(_line_filters):
        match = filt.match(output)
        if match:
            output = filt.apply(match)
            break

    return output

init_filters()
