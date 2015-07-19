#!/usr/bin/env python
"""
usage: argalign.py [-h] [-o] [-l ROW_LENGTH] [-s COLUMN_SEP] [-i INDENT_STR]
                   [-r INDENT_REP] [-c]

Receives CSV arguments/parameters as input and outputs them as a columnized
string

optional arguments:
  -h, --help            show this help message and exit
  -o, --one-per-line    treat each line as its own argument
  -l ROW_LENGTH, --row-length ROW_LENGTH
                        maximum length of a row
  -s COLUMN_SEP, --column-sep COLUMN_SEP
                        string used to separate columns
  -i INDENT_STR, --indent-str INDENT_STR
                        string added as prefix to each row
  -r INDENT_REP, --indent-rep INDENT_REP
                        # of repetitions of indent string
  -c, --column-major    print elements in column-major order

Ex:
```cpp
GameScene::GameScene(
    GameStage& stage, bool hogs_screen, bool update_floor, View::ID target
    ) :
    // Base init
    Subscriber{},
    // Member init
    m_stage{stage}, m_entities{}, m_hogs_screen{hogs_screen},
    m_update_floor{update_floor}, m_target_view{target}
{
    //...
}
```
Upon application to lines 7-8 becomes:
```cpp
GameScene::GameScene(
    GameStage& stage, bool hogs_screen, bool update_floor, View::ID target
    ) :
    // Base init
    Subscriber{},
    // Member init
    m_stage{stage},             m_entities{},
    m_hogs_screen{hogs_screen}, m_update_floor{update_floor},
    m_target_view{target}
{
    //...
}
```
"""
import sys
import argparse
import itertools

def rowChunks(lst, n):
    """Returns chunks of lst in col form s.t. there are n rows"""
    col_num = (len(lst) + n-1) // max(1, n)
    return [ lst[i:len(lst):col_num] for i in range(col_num) ]

def colChunks(lst, n):
    """Same as rowChunks but values are in column-major order"""
    n = max(1, n)
    return [ lst[i:i+n] for i in range(0, len(lst), n) ]

def transposed(lst, fill=None):
    return [ list(l) for l in itertools.zip_longest(*lst, fillvalue=fill) ]

def columnize(lst, indent, max_row_len, col_sep, colMajor=False):
    """Return a string w/ values from lst printed as an evenly spaced 2d grid

    :param lst: 1d array of data convertible to str
    :param indent: string that prepends each row of the output data
    :param max_row_len: maximum # of characters a row may contain (including
        indent and col_sep) when data won't fit in this space, there will be one
        value per line
    :param col_sep: string that delimits columns
    :param colMajor: when true, values are listed in column-major order
        for example, given input: [1, 2, 3, 4]
            row-major:      col-major:
               1  2            1  3
               3  4            2  4
    :returns: formatted string with data organized using above rules
    """
    lst = list(map(lambda x: str(x).strip(), lst))
    if not any(lst):
        return ""
    max_row_len -= len(indent)
    # search for a working # of rows
    for row_num in range(1, len(lst) + 1):
        cols = rowChunks(lst, row_num) if not colMajor else colChunks(lst, row_num)
        col_len = [ max(len(arg) for arg in col) for col in cols ]
        row_len = sum(col_len) + len(col_sep)*(len(cols) - 1)
        if row_len <= max_row_len:
            break
    # justify strings in each column
    for i in range(len(cols)):
        cols[i] = [ arg.ljust(col_len[i]) for arg in cols[i] ]
    # combine the lines together w/ an indent string and return
    return "\n".join([ indent + col_sep.join(row)
                      for row in transposed(cols, fill="")])

def split(string):
    """split comma delimitted input containing strings or nested structures 

    :param string: input string
    :returns: list of values split after commas in string
    :raise ValueError: when string is unbalanced
    """
    if not string:
        return []
    output = [""]
    escaped = False
    nested, nest_symbols = [], {'[': ']', '(': ')', '<': '>', '{': '}'}
    for c in string:
        # handle escaped characters
        if escaped:
            escaped = False
        elif c == '\\':
            escaped = True
        # handle strings (nest characters are ignored while in strings)
        elif c in ("'", '"'):
            if not nested or nested[-1] not in ("'", '"'):
                nested.append(c)
            elif c == nested[-1]:
                nested.pop()
        # handle nested value semantics
        elif not nested or nested[-1] not in ("'", '"'):
            if c in nest_symbols:
                nested.append(nest_symbols[c])
            elif c in nest_symbols.values():
                if nested and c == nested[-1]:
                    nested.pop()
                else:
                    raise ValueError("unbalanced input")
        # append character to argument
        output[-1] += c
        # move onto next word upon discovery of comma
        if c == ',' and not nested:
            output[-1] = output[-1][:-1].strip() + ','
            output.append("")
    # raise errors when input is unbalanced
    if nested:
        raise ValueError("unbalanced input")
    return output

def main():
    parser = argparse.ArgumentParser(description="Receives CSV "
        "arguments/parameters as input and outputs them as a columnized string")
    parser.add_argument("-o", "--one-per-line", action="store_true",
        help="treat each line as its own argument")
    parser.add_argument("-l", "--row-length", type=int, default=80,
        help="maximum length of a row")
    parser.add_argument("-s", "--column-sep", type=str, default=" ",
        help="string used to separate columns")
    parser.add_argument("-i", "--indent-str", type=str, default="    ",
        help="string added as prefix to each row")
    parser.add_argument("-r", "--indent-rep", type=int, default=1,
        help="# of repetitions of indent string")
    parser.add_argument("-c", "--column-major", action="store_true",
        help="print elements in column-major order")
    # fetch options
    options = parser.parse_args()
    # request input
    args = [ line.strip() for line in sys.stdin ]
    if not options.one_per_line:
        args = split(" ".join(args))
    # columnize and print!
    grid = columnize(args, options.indent_str * options.indent_rep,
        options.row_length, options.column_sep, colMajor=options.column_major)
    print("\n".join([ line.rstrip() for line in grid.split('\n') ]))

if __name__ == "__main__":
    main()
