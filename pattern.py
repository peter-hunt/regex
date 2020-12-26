from dataclasses import dataclass
from typing import List


ASCII = A = 256  # assume ascii "locale"
IGNORECASE = I = 2  # ignore case
LOCALE = L = 4  # assume current 8-bit locale
UNICODE = U = 32  # assume unicode "locale"
MULTILINE = M = 8  # make anchors look for newline
DOTALL = S = 16  # make dot match newline
VERBOSE = X = 64  # ignore whitespace and comments


_special_chars_map = {i: '\\' + chr(i)
                      for i in b'()[]{}?*+-|^$\\.&~# \t\n\r\v\f'}


class error(Exception):
    pass


class Match:
    def __init__(self, span, match):
        self.span = span
        self.match = match

    def __repr__(self):
        return f'<regex.Match object; span={self.span}, match={self.match!r}>'


@dataclass
class Node:
    pass


@dataclass
class Pattern(Node):
    raw: str
    nodes: List[Node]

    def __repr__(self):
        return f'regex.compile({self.raw!r})'

    @classmethod
    def _match(cls, nodes, string, start, end, flags):
        if not nodes:
            return Match((start, start), '')

        _node, *_nodes = nodes

        if isinstance(_node, Start):
            return cls._match(nodes[1:], string, start, end, flags)
        elif isinstance(_node, End):
            return None if string else Match((start, end), string)

        for index in range(len(string) + 1):
            if _node.match(string[:index]):
                trailing = cls._match(
                    _nodes, string[index:],
                    start + index, len(string) + 1 - start, flags
                )
                if trailing:
                    return Match((start, trailing.span[1]),
                                 string[:index] + trailing.match)

    def match(self, string, flags=0):
        return self._match(self.nodes, string, 0, len(string) - 1, flags)


@dataclass
class Start(Node):
    pass


@dataclass
class End(Node):
    pass


@dataclass
class Plain(Node):
    value: str

    def match(self, string, flags=0):
        if flags & IGNORECASE:
            return string.lower() == self.value.lower()
        else:
            return string == self.value


@dataclass
class Decimal(Node):
    def match(self, string, flags=0):
        return string != '' and string in {'0', '1', '2', '3', '4',
                                           '5', '6', '7', '8', '9'}


@dataclass
class NonDecimal(Node):
    def match(self, string, flags=0):
        return string != '' and string not in {'0', '1', '2', '3', '4',
                                               '5', '6', '7', '8', '9'}


@dataclass
class Whitespace(Node):
    def match(self, string, flags=0):
        return string != '' and string in {' ', '\t', '\n',
                                           '\r', '\f', '\v'}


@dataclass
class NonWhitespace(Node):
    def match(self, string, flags=0):
        return string != '' and string not in {' ', '\t', '\n',
                                               '\r', '\f', '\v'}


@dataclass
class WordChar(Node):
    def match(self, string, flags=0):
        return string != '' and string in {
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_'
        }


@dataclass
class NonWordChar(Node):
    def match(self, string, flags=0):
        return string != '' and string not in {
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_'
        }


_special_nodes_map = {
    'A': Start(),
    'd': Decimal(),
    'D': NonDecimal(),
    's': Whitespace(),
    'S': NonWhitespace(),
    'w': WordChar(),
    'W': NonWordChar(),
    'Z': End(),
}

_special_symbol_map = {
    '^': Start(),
    '$': End(),
}

for char in _special_symbol_map:
    _special_nodes_map[char] = char


def compile(pattern, flags=0):
    nodes = []
    skip = False

    for pos, char in enumerate(pattern):
        if skip:
            skip = False
            continue

        if char == '\\':
            if pos == len(pattern) - 1:
                raise error(f'bad escape (end of pattern) at position {pos}')
            else:
                nodes.append(_special_nodes_map.get(
                    pattern[pos + 1],
                    Plain(f'\\{pattern[pos + 1]}'),
                ))
                skip = True
        else:
            nodes.append(_special_symbol_map.get(char, Plain(char)))

    result = []
    is_plain = False
    plain = ''

    for node in nodes:
        if isinstance(node, Plain):
            if is_plain:
                plain = f'{plain}{node.value}'
            else:
                is_plain = True
                plain = node.value
        else:
            if is_plain:
                is_plain = False
                result.append(Plain(plain))
            result.append(node)

    if is_plain:
        is_plain = False
        result.append(Plain(plain))

    return Pattern(pattern, nodes)
