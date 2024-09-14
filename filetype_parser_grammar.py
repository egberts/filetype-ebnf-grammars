#!/usr/bin/env python
#  Copyright by Egbert S., 
#  License: MIT License
#
import argparse
import glob
import os
import re


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbosity",
        metavar="<level>",
        help="verbosity level",
        type=str
    )
    parser.add_argument('files', metavar="<filespec>", nargs='*', help='a file specification, may include wildcard')
    args = parser.parse_args()
    return args


def init_regex() -> dict:
    patterns = {}
    patterns[0] = {'name': 'EBNF', 'pattern': '::-'}
    patterns[1] = {'name': 'PEG', 'pattern': 'definition'}
    patterns[2] = {'name': 'BNF', 'pattern': r'\s*=\s*'}  # BNF, Parsimonious
    patterns[3] = {'name': 'Ford PEG', 'pattern': r'\s\<\-\s'}  # Ford [2004] Bryan Ford, Parsing Expression Grammars: A Recognition-Based Syntactic Foundation. ACM SIGPLAN Symposium on Principles of Programming Languages (POPL), 2004.
    patterns[4] = {'name': 'Marpa:R2 SLIF-DSL', 'pattern': ':\w'}  # SLIF-DSL, scanless Interface Domain-specific Language (Marpa::R2)
    patterns[5] = {'name': 'JANET', 'pattern': r'^\(\s*def\s'}  # JANET (Lpeg, REBOL/Red)
    patterns[6] = {'name': 'JANET2', 'pattern': r'^\(\s*peg\/match\s'}  # JANET (Lpeg, REBOL/Red)
    patterns[7] = {'name': 'Pointlander GO Peg', 'pattern': r'^package\s'}  # https://github.com/pointlander/peg/blob/master/peg.peg
    patterns[8] = {'name': 'Pointlander GO Peg', 'pattern': r'^\s*\/.*END$'}  # https://github.com/pointlander/peg/blob/master/peg.peg
    patterns[9] = {'name': 'Python PEG', 'pattern': r'\s\w\n\s*;'}  # Python-variant (Ford 2004)
    patterns[10] = {'name': 'Python PEG', 'pattern': r'\s\w\[\w*\]:s'}  # Python-internal PEG 
    patterns[11] = {'name': 'Arepeggio PEG', 'pattern': r'^\s*[&]?\w*\s*\<\-\s'}  # Arepeggio, Peg.py

    for idx in range(0, len(patterns)):
        myflags = re.MULTILINE
        pattern = patterns[idx]
        this_pattern = pattern['pattern']
        my_regex: re.Pattern = re.compile(this_pattern, myflags)
        patterns[idx].update({'re': my_regex})
                               #.update({'re': my_regex}))

    return patterns


def main(this_file: str, buffer: str):
    check_patterns = init_regex()
    for pattern_index in check_patterns:
        pattern = check_patterns[pattern_index]
        my_re = pattern['re']
        if my_re.search(buffer):
            name = pattern['name']
            print(f'{pattern_index}: ', end='')
            print(f'{this_file}: ', end='')
            thispattern = my_re.pattern
            print(f'"{thispattern}": {name}')


if __name__ == "__main__":
    args = arg_parser()
    matched_files = []

    for file in args.files:
        # Work in current working directory (and no subdirectory)
        if glob.escape(file) != file:
            # -> There are glob pattern chars in the string
            matched_files.extend(glob.glob(file))
        else:
            matched_files.append(file)
    if len(matched_files):
        for this_file in matched_files:
            f = open(this_file)
            textbuf = f.read()
            f.close()
            main(this_file, textbuf)
    else:
        textbuf = "a ::= b | c"   # EBNF
        textbuf = "a = b \n    | c\n    ;"   # Python PEG (semicolon EOS)
        textbuf = ":start ::= abc\nabc ::= xyz"  # Marpa (SLIF-DSL > EBNF)
        print('textbuf: ', textbuf)
        main('(buffer)', textbuf)
