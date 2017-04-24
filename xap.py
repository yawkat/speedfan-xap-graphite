#!/usr/bin/env python3

import re
from binascii import unhexlify
from typing import Union, Dict, Any, List, Tuple

Block = List[Tuple[str, Union[str, bytes, Any]]]


class ParseException(Exception):
    def __init__(self, msg):
        super(ParseException, self).__init__(msg)


def parse_xAP(xAP: str) -> List[Tuple[str, Block]]:
    lines = xAP.splitlines()
    i = 0

    def is_keyword(s: str) -> bool:
        return re.fullmatch(r"[a-zA-Z0-9_\- \.]+", s) and s.strip() == s

    def check_keyword(s: str) -> None:
        if not is_keyword(s):
            raise ParseException("Invalid keyword " + s)

    def parse_block() -> Block:
        nonlocal i
        if lines[i] != '{':
            raise ParseException("Expected '{', got '%s' on line %s" % (lines[i], i + 1))
        items: Block = []
        i += 1
        while lines[i] != '}':
            line = lines[i]
            i += 1
            if i < len(lines) and lines[i] == '{':
                check_keyword(line)
                items.append((line, parse_block()))
                continue
            split_by_equals = line.split("=", maxsplit=1)
            if len(split_by_equals) > 1:
                key, value = split_by_equals
                check_keyword(key)
                items.append((key, value))
                continue
            split_by_bang = line.split("!", maxsplit=1)
            if len(split_by_bang) > 1:
                key, value = split_by_bang
                check_keyword(key)
                items.append((key, unhexlify(value)))
                continue
            raise ParseException("Cannot parse line " + line)
        i += 1
        return items

    blocks: List[Tuple[str, Block]] = []
    while i < len(lines):
        key = lines[i]
        check_keyword(key)
        i += 1
        block = parse_block()
        blocks.append((key, block))
    return blocks


def to_map(list_of_tuples: Block) -> Dict[str, Union[str, bytes, Any]]:
    result = {}
    for k, v in list_of_tuples:
        if type(v) == list:
            v = to_map(v)
        result[k] = v
    return result


if __name__ == '__main__':
    import json
    import sys
    import fileinput

    xap = parse_xAP("".join(fileinput.input()))
    json.dump(to_map(xap), sys.stdout)
