from dataclasses import dataclass
from typing import List, Tuple

from constants import WHITESPACE, OCTAL, DECIMAL, HEXADECIMAL, WORDCHAR


__all__ = [
    # 'ASCII',
    'IGNORECASE',
    # 'LOCALE',
    # 'UNICODE',
    'MULTILINE',
    'DOTALL',
    'VERBOSE',
    'FLAGS',

    '_special_chars_map',
    '_escape_nodes_map',
    '_symbols_map',
    '_count_map',

    'error',
    'Pattern',
    'Match',

    'Node',
    'Start', 'End', 'Plain', 'Any',
    'Decimal', 'NonDecimal', 'Whitespace', 'NonWhitespace',
    'WordChar', 'NonWordChar',

    'compile', 'purge',
]


# ASCII = A = 256  # assume ascii "locale"
IGNORECASE = I = 2  # ignore case
# LOCALE = L = 4  # assume current 8-bit locale
# UNICODE = U = 32  # assume unicode "locale"
MULTILINE = M = 8  # make anchors look for newline
DOTALL = S = 16  # make dot match newline
VERBOSE = X = 64  # ignore whitespace and comments

FLAGS = {
    'IGNORECASE': 2,
    # 'LOCALE': 4,
    'MULTILINE': 8,
    'DOTALL': 16,
    # 'UNICODE': 32,
    'VERBOSE': 64,
    # 'ASCII': 256,
}


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
class Pattern:
    raw: str
    nodes: List[Node]
    flags: int = 0

    def __repr__(self):
        flag_str = '.'.join(f'regex.{name}' for name, flag in FLAGS.items()
                            if self.flags & flag)
        if flag_str:
            return f'regex.compile({self.raw!r}, {flag_str})'
        else:
            return f'regex.compile({self.raw!r})'

    def _match(self, nodes, string, start, end):
        if not nodes:
            return Match((start, start), '')

        _node, *_nodes = nodes

        if isinstance(_node, Start):
            return self._match(nodes[1:], string, start, end)
        elif isinstance(_node, End):
            return None if string else Match((start, end), string)

        if isinstance(_node, Greedy):
            for index in range(len(string), -1, -1):
                if _node.match(string[:index]):
                    trailing = self._match(
                        _nodes, string[index:],
                        start + index, len(string) + 1 - start
                    )
                    if trailing:
                        return Match((start, trailing.span[1]),
                                     string[:index] + trailing.match)
        else:
            for index in range(len(string) + 1):
                if _node.match(string[:index]):
                    trailing = self._match(
                        _nodes, string[index:],
                        start + index, len(string) + 1 - start
                    )
                    if trailing:
                        return Match((start, trailing.span[1]),
                                     string[:index] + trailing.match)

    def match(self, string):
        return self._match(self.nodes, string, 0, len(string) - 1)

    def _fullmatch(self, nodes, string, start, end):
        if not nodes:
            return Match((start, start), '')
        elif len(nodes) == 1:
            if nodes[0].match(string):
                return Match((start, end), string)
            else:
                return

        _node, *_nodes = nodes

        if isinstance(_node, Start):
            return self._fullmatch(nodes[1:], string, start, end)
        elif isinstance(_node, End):
            return None if string else Match((start, end), string)

        if isinstance(_node, Greedy):
            for index in range(len(string), -1, -1):
                if _node.match(string[:index]):
                    trailing = self._fullmatch(
                        _nodes, string[index:],
                        start + index, len(string) + 1 - start
                    )
                    if trailing:
                        return Match((start, trailing.span[1]),
                                     string[:index] + trailing.match)
        else:
            for index in range(len(string) + 1):
                if _node.match(string[:index]):
                    trailing = self._fullmatch(
                        _nodes, string[index:],
                        start + index, len(string) + 1 - start
                    )
                    if trailing:
                        return Match((start, trailing.span[1]),
                                     string[:index] + trailing.match)

    def fullmatch(self, string):
        return self._fullmatch(self.nodes, string, 0, len(string) - 1)


@dataclass
class Start(Node):
    flags: int


@dataclass
class End(Node):
    flags: int


@dataclass
class Plain(Node):
    value: str
    flags: int

    def match(self, string):
        if self.flags & IGNORECASE:
            return string.lower() == self.value.lower()
        else:
            return string == self.value


@dataclass
class Any(Node):
    flags: int

    def match(self, string):
        if self.flags & DOTALL:
            return len(string) == 1
        else:
            return len(string) == 1 and string != '\n'


@dataclass
class Decimal(Node):
    flags: int

    def match(self, string):
        return string != '' and string in DECIMAL


@dataclass
class NonDecimal(Node):
    flags: int

    def match(self, string):
        return string != '' and string not in DECIMAL


@dataclass
class Whitespace(Node):
    flags: int

    def match(self, string):
        return string != '' and string in WHITESPACE


@dataclass
class NonWhitespace(Node):
    flags: int

    def match(self, string):
        return string != '' and string not in WHITESPACE


@dataclass
class WordChar(Node):
    flags: int

    def match(self, string):
        return string != '' and string in WORDCHAR


@dataclass
class NonWordChar(Node):
    flags: int

    def match(self, string):
        return string != '' and string not in WORDCHAR


@dataclass
class Greedy(Node):
    node: Node
    flags: int


@dataclass
class NonGreedy(Node):
    node: Node
    flags: int


@dataclass
class GreedyPositional(Greedy):
    def match(self, string):
        if self.node.match(string):
            return True
        for index in range(1, len(string)):
            if self.node.match(string[:index]) and (
                self.node.match(string[index:]) or self.match(string[index:])
            ):
                return True
        return False


@dataclass
class NonGreedyPositional(NonGreedy):
    def match(self, string):
        if self.node.match(string):
            return True
        for index in range(1, len(string)):
            if self.node.match(string[:index]) and (
                self.node.match(string[index:]) or self.match(string[index:])
            ):
                return True
        return False


@dataclass
class GreedyOptional(Greedy):
    def match(self, string):
        if not string or self.node.match(string):
            return True
        for index in range(1, len(string)):
            if self.node.match(string[:index]) and (
                self.node.match(string[index:]) or self.match(string[index:])
            ):
                return True
        return False


@dataclass
class NonGreedyOptional(NonGreedy):
    def match(self, string):
        if not string or self.node.match(string):
            return True
        for index in range(1, len(string)):
            if self.node.match(string[:index]) and (
                self.node.match(string[index:]) or self.match(string[index:])
            ):
                return True
        return False


@dataclass
class GreedyOneOrNone(Greedy):
    def match(self, string):
        return not string or self.node.match(string)


@dataclass
class NonGreedyOneOrNone(NonGreedy):
    def match(self, string):
        return not string or self.node.match(string)


_escape_nodes_map = {
    'A': Start,
    'd': Decimal,
    'D': NonDecimal,
    's': Whitespace,
    'S': NonWhitespace,
    'w': WordChar,
    'W': NonWordChar,
    'Z': End,
}

_symbols_map = {
    '^': Start,
    '$': End,
    '.': Any,
}

_count_map = {
    '+': [GreedyPositional, NonGreedyPositional],
    '*': [GreedyOptional, NonGreedyOptional],
    '?': [GreedyOneOrNone, NonGreedyOneOrNone],
}

for char in _symbols_map:
    _escape_nodes_map[char] = char

for char in 'fnrtv':
    _escape_nodes_map[char] = char


def _find_last_repeatable(nodes: List[Node]) -> Tuple[List[Node], Node]:
    nodes = [node for node in nodes if not isinstance(node, (Start, End))]
    if not nodes:
        raise error('got nothing to repeat')
    *_nodes, _node = nodes
    if isinstance(_node, Plain):
        return ([*_nodes, Plain(_node.value[:-1], _node.flags)],
                Plain(_node.value[-1], _node.flags))
    return _nodes, _node


def _compile(pattern: str, flags: int) -> Pattern:
    nodes = []
    skip = 0

    for pos, char in enumerate(pattern):
        if skip > 0:
            skip -= 1
            continue

        if char == '\\':
            if pos == len(pattern) - 1:
                raise error(f'bad escape (end of pattern) at position {pos}')
            else:
                next_char = pattern[pos + 1]
                if next_char == '0':
                    if pos + 3 > len(pattern) - 1:
                        nodes.append(Plain('\x00', flags))
                        skip = 1
                    if pattern[pos + 2] in OCTAL and pattern[pos + 3] in OCTAL:
                        nodes.append(Plain(chr(int(
                            pattern[pos + 2] + pattern[pos + 3], base=8
                        )), flags))
                        skip = 3
                    else:
                        nodes.append(Plain('\x00', flags))
                        skip = 1
                    continue
                elif next_char in {'X', 'x'}:
                    if (
                        pos + 3 <= len(pattern) - 1 and
                        pattern[pos + 2] in HEXADECIMAL and
                        pattern[pos + 3] in HEXADECIMAL
                    ):
                        nodes.append(Plain(chr(int(
                            pattern[pos + 2] + pattern[pos + 3], base=16
                        ))))
                        skip = 3
                        continue
                    else:
                        raise error('invalid hexadecimal literal escape')
                else:
                    if next_char in _escape_nodes_map:
                        nodes.append(_escape_nodes_map[next_char](flags))
                    else:
                        nodes.append(Plain(f'\\{next_char}'))
                    skip = 1
        elif char in _count_map:
            if pos < len(pattern) - 1 and pattern[pos + 1] == '?':
                nodes, node = _find_last_repeatable(nodes)
                nodes.append(_count_map[char][1](node, flags))
                skip = 1
            else:
                nodes, node = _find_last_repeatable(nodes)
                nodes.append(_count_map[char][0](node, flags))
        else:
            if char in _symbols_map:
                nodes.append(_symbols_map[char](flags))
            else:
                nodes.append(Plain(char, flags))

    tokens = []
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
                tokens.append(Plain(plain, flags))
            tokens.append(node)

    if is_plain:
        is_plain = False
        tokens.append(Plain(plain, flags))

    return Pattern(pattern, tokens)


_cache = {}
_MAXCACHE = 512


def compile(pattern: str, flags: int = 0) -> Pattern:
    if (pattern, flags) in _cache:
        return _cache[pattern, flags]

    if isinstance(pattern, Pattern):
        if flags:
            raise ValueError('cannot process flags argument '
                             'with a compiled pattern')
        return pattern
    if not isinstance(pattern, str):
        raise TypeError('first argument must be string or compiled pattern')

    p = _compile(pattern, flags)
    if len(_cache) >= _MAXCACHE:
        try:
            del _cache[next(iter(_cache))]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _cache[pattern, flags] = p
    return p


def purge():
    pass
