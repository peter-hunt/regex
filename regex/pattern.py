from dataclasses import dataclass
from types import FunctionType
from typing import List, Tuple

from .constants import WHITESPACE, OCTAL, DECIMAL, HEXADECIMAL, WORDCHAR


__all__ = [
    # 'ASCII', 'A',
    'IGNORECASE', 'I',
    # 'LOCALE',
    # 'UNICODE',
    'MULTILINE', 'M',
    'DOTALL', 'S',
    'VERBOSE', 'X',
    # 'TEMPLATE', 'T',
    'DEBUG',
    'FLAGS',
    'INDENT', 'LAST_INDENT',

    '_special_chars_map',
    '_escape_nodes_map',
    '_symbols_map',
    '_count_map',

    'error',
    'Pattern',
    'Match',

    'Node',
    'Start', 'End', 'PlainText', 'Any',
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

# TEMPLATE = T = 1 # disable backtracking
DEBUG = 128  # dump pattern after compilation

INDENT = '  '
LAST_INDENT = '| '

FLAGS = {
    'TEMPLATE': 1,
    'IGNORECASE': 2,
    # 'LOCALE': 4,
    'MULTILINE': 8,
    'DOTALL': 16,
    # 'UNICODE': 32,
    'VERBOSE': 64,
    'DEBUG': 128,
    # 'ASCII': 256,
}


_special_chars_map = {i: '\\' + chr(i)
                      for i in b'()[]{}?*+-|^$\\.&~# \t\n\r\v\f'}


_last_indent = 0
_do_debug = False


def _debugable(func: FunctionType, /) -> FunctionType:
    def decorated(*args):
        global _last_indent
        if args[-1] != _last_indent:
            if _do_debug and args[-1] > _last_indent:
                if _last_indent == 0:
                    print('EXECUTION:')
                else:
                    print(f'{INDENT * (_last_indent - 1) + LAST_INDENT}'
                          f'EXECUTION:')
            _last_indent = args[-1]

        def indent():
            if not isinstance(args[-1], int):
                indent = 0
            else:
                indent = args[-1]
            if indent == 0:
                return ''
            else:
                return INDENT * (indent - 1) + LAST_INDENT

        arg_names = [*func.__code__.co_varnames]
        arg_names = arg_names[:arg_names.index('debug_indent') + 1]
        if arg_names[0] == 'self':
            arg_names = arg_names[1:]
            display_args = args[1:]
        elif arg_names[0] == 'cls':
            arg_names = arg_names[1:]
            args = args[1:] if len(args) > len(arg_names) else args
            display_args = args[:]
        args_str = f',\n{indent()}          '.join(
            f'{name}={display_args[index]!r}'
            for index, name in enumerate(arg_names[:-1])
        )
        if _do_debug:
            print(
                f'{indent()}RUNNING: {func.__qualname__}\n'
                f'{indent()}WITH ARG: {args_str}'
            )
        result = func(*args)
        if _do_debug:
            print(f'{indent()}RETURNED: {result}\n{indent()}')
        return result
    return decorated


class error(Exception):
    pass


class Match:
    def __init__(self, span: Tuple[int, int], match: str, /) -> None:
        assert span[1] - span[0] == len(match), (span[1] - span[0], match)
        self.span = span
        self.match = match

    def __repr__(self, /) -> str:
        return f'<regex.Match object; span={self.span}, match={self.match!r}>'


@dataclass
class Node:
    pass


@dataclass
class Pattern:
    raw: str
    nodes: List[Node]
    flags: int = 0

    def __repr__(self, /) -> str:
        flag_str = '.'.join(f'regex.{name}' for name, flag in FLAGS.items()
                            if self.flags & flag)
        if flag_str:
            return f'regex.compile({self.raw!r}, {flag_str})'
        else:
            return f'regex.compile({self.raw!r})'

    @_debugable
    def _match(self, nodes: List[Node], string: str,
               debug_indent: int = 0, /):
        if not nodes:
            return Match((0, 0), '')

        _node, *_nodes = nodes

        if isinstance(_node, Start):
            return self._match(nodes[1:], string, debug_indent + 1)
        elif isinstance(_node, End):
            return None if string else Match((0, len(string)), string)

        if isinstance(_node, Greedy):
            for index in range(len(string), -1, -1):
                if _node.fullmatch(string[:index], debug_indent + 1):
                    trailing = self._match(
                        _nodes, string[index:],
                        debug_indent + 1,
                    )
                    if trailing:
                        return Match((0, index + trailing.span[1]),
                                     string[:index] + trailing.match)
        else:
            for index in range(len(string) + 1):
                if _node.fullmatch(string[:index], debug_indent + 1):
                    trailing = self._match(
                        _nodes, string[index:],
                        debug_indent + 1,
                    )
                    if trailing:
                        return Match((0, index + trailing.span[1]),
                                     string[:index] + trailing.match)

    def match(self, string: str, debug_indent: int = 0, /):
        global _do_debug
        if self.flags & DEBUG:
            _do_debug = True
        result = self._match(self.nodes, string, debug_indent)
        _do_debug = False
        return result

    @_debugable
    def _fullmatch(self, nodes: List[Node], string: str,
                   debug_indent: int = 0, /):
        if not nodes:
            return Match((0, 0), '')
        elif len(nodes) == 1:
            if nodes[0].fullmatch(string, debug_indent + 1):
                return Match((0, len(string)), string)
            else:
                return

        _node, *_nodes = nodes

        if isinstance(_node, Start):
            return self._fullmatch(
                nodes[1:], string, debug_indent + 1
            )
        elif isinstance(_node, End):
            return None if string else Match((0, len(string)), string)

        if isinstance(_node, Greedy):
            for index in range(len(string), -1, -1):
                if _node.fullmatch(string[:index], debug_indent + 1):
                    trailing = self._fullmatch(
                        _nodes, string[index:],
                        debug_indent + 1,
                    )
                    if trailing:
                        return Match((0, index + trailing.span[1]),
                                     string[:index] + trailing.match)
        else:
            for index in range(len(string) + 1):
                if _node.fullmatch(string[:index], debug_indent + 1):
                    trailing = self._fullmatch(
                        _nodes, string[index:],
                        debug_indent + 1,
                    )
                    if trailing:
                        return Match((0, index + trailing.span[1]),
                                     string[:index] + trailing.match)

    def fullmatch(self, string: str, debug_indent: int = 0, /):
        global _do_debug
        if self.flags & DEBUG:
            _do_debug = True
        result = self._fullmatch(self.nodes, string, debug_indent)
        _do_debug = False
        return result


@dataclass
class Start(Node):
    flags: int


@dataclass
class End(Node):
    flags: int


@dataclass
class PlainText(Node):
    value: str
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        if self.flags & IGNORECASE:
            return string.lower() == self.value.lower()
        else:
            return string == self.value


@dataclass
class Any(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        if self.flags & DOTALL:
            return len(string) == 1
        else:
            return len(string) == 1 and string != '\n'


@dataclass
class Decimal(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return string != '' and string in DECIMAL


@dataclass
class NonDecimal(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return string != '' and string not in DECIMAL


@dataclass
class Whitespace(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return string != '' and string in WHITESPACE


@dataclass
class NonWhitespace(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return string != '' and string not in WHITESPACE


@dataclass
class WordChar(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return string != '' and string in WORDCHAR


@dataclass
class NonWordChar(Node):
    flags: int

    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return string != '' and string not in WORDCHAR


@dataclass
class Greedy(Node):
    node: Node


@dataclass
class NonGreedy(Node):
    node: Node


@dataclass
class GreedyPositional(Greedy):
    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        if self.node.fullmatch(string):
            return True
        for index in range(len(string), -1, -1):
            if self.node.fullmatch(string[:index], debug_indent + 1) and (
                self.node.fullmatch(string[index:], debug_indent + 1) or
                self.fullmatch(string[index:], debug_indent + 1)
            ):
                return True
        return False


@dataclass
class NonGreedyPositional(NonGreedy):
    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        for index in range(len(string) + 1):
            if self.node.fullmatch(string[:index], debug_indent + 1) and (
                self.node.fullmatch(string[index:], debug_indent + 1) or
                self.fullmatch(string[index:], debug_indent + 1)
            ):
                return True
        if self.node.fullmatch(string, debug_indent + 1):
            return True
        return False


@dataclass
class GreedyOptional(Greedy):
    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        if self.node.fullmatch(string):
            return True
        for index in range(len(string), -1, -1):
            if self.node.fullmatch(string[:index], debug_indent + 1) and (
                self.node.fullmatch(string[index:], debug_indent + 1) or
                self.fullmatch(string[index:], debug_indent + 1)
            ):
                return True
        if not string:
            return True
        return False


@dataclass
class NonGreedyOptional(NonGreedy):
    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        if not string:
            return True
        for index in range(len(string) + 1):
            if self.node.fullmatch(string[:index], debug_indent + 1) and (
                self.node.fullmatch(string[index:], debug_indent + 1) or
                self.fullmatch(string[index:], debug_indent + 1)
            ):
                return True
        if self.node.fullmatch(string, debug_indent + 1):
            return True
        return False


@dataclass
class GreedyOneOrNone(Greedy):
    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return not string or self.node.fullmatch(string, debug_indent + 1)


@dataclass
class NonGreedyOneOrNone(NonGreedy):
    @_debugable
    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return not string or self.node.fullmatch(string, debug_indent + 1)


@dataclass
class GreedyRepeat(Greedy):
    node: Node
    count: int

    @classmethod
    def _fullmatch(cls, node: Node, string: str, count: int,
                   debug_indent: int = 0, /):
        if count == 0:
            return False if string else True
        if count == 1:
            return node.fullmatch(string, debug_indent + 1)
        if not string:
            return (node.fullmatch('', debug_indent + 1) and
                    cls._fullmatch(node, '', count - 1, debug_indent + 1))
        for index in range(len(string), -1, -1):
            if (
                node.fullmatch(string[:index], debug_indent + 1) and
                cls._fullmatch(
                    node, string[index:], count - 1, debug_indent + 1
                )
            ):
                return True
        return False

    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return self._fullmatch(self.node, string, self.count, debug_indent)


GreedyRepeat._fullmatch = _debugable(GreedyRepeat._fullmatch)


@dataclass
class NonGreedyRepeat(NonGreedy):
    node: Node
    count: int

    @classmethod
    def _fullmatch(cls, node: Node, string: str, count: int,
                   debug_indent: int = 0, /):
        if count == 0:
            return False if string else True
        if count == 1:
            return node.fullmatch(string, debug_indent + 1)
        if not string:
            return (node.fullmatch('', debug_indent + 1) and
                    cls._fullmatch(node, '', count - 1, debug_indent + 1))
        for index in range(len(string) + 1):
            if (
                node.fullmatch(string[:index], debug_indent + 1) and
                cls._fullmatch(
                    node, string[index:], count - 1, debug_indent + 1
                )
            ):
                return True
        return False

    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return self._fullmatch(self.node, string, self.count, debug_indent)


NonGreedyRepeat._fullmatch = _debugable(NonGreedyRepeat._fullmatch)


@dataclass
class GreedyRepeatRange(Greedy):
    node: Node
    lower: int
    upper: int

    @classmethod
    def _fullmatch(cls, node: Node, string: str, lower: int, upper: int,
                   debug_indent: int = 0, /):
        if upper == 0:
            return False if string else True
        if not string:
            return node.fullmatch('', debug_indent + 1) and cls._fullmatch(
                node, '', lower - 1, upper - 1, debug_indent + 1
            )
        for index in range(len(string), -1, -1):
            if (
                node.fullmatch(string[:index], debug_indent + 1) and
                cls._fullmatch(
                    node, string[index:], lower - 1, upper - 1,
                    debug_indent + 1,
                )
            ):
                return True
        if lower == 0:
            return False if string else True
        return False

    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return self._fullmatch(
            self.node, string, self.lower, self.upper, debug_indent
        )


GreedyRepeatRange._fullmatch = _debugable(GreedyRepeatRange._fullmatch)


@dataclass
class NonGreedyRepeatRange(NonGreedy):
    node: Node
    lower: int
    upper: int

    @classmethod
    def _fullmatch(cls, node: Node, string: str, lower: int, upper: int,
                   debug_indent: int = 0, /):
        if lower == 0:
            return False if string else True
        if not string:
            return node.fullmatch('', debug_indent + 1) and cls._fullmatch(
                node, '', lower - 1, upper - 1, debug_indent + 1
            )
        for index in range(len(string) + 1):
            if (
                node.fullmatch(string[:index], debug_indent + 1) and
                cls._fullmatch(
                    node, string[index:], lower - 1, upper - 1,
                    debug_indent + 1,
                )
            ):
                return True
        if upper == 0:
            return False if string else True
        return False

    def fullmatch(self, string: str, debug_indent: int = 0, /):
        return self._fullmatch(
            self.node, string, self.lower, self.upper, debug_indent
        )


NonGreedyRepeatRange._fullmatch = _debugable(NonGreedyRepeatRange._fullmatch)


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

_escape_needed_char = {*'()[]{}?*+-|^$\\.&~# '}

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
    if isinstance(_node, PlainText):
        return ([*_nodes, PlainText(_node.value[:-1], _node.flags)],
                PlainText(_node.value[-1], _node.flags))
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
            next_char = pattern[pos + 1]
            if next_char == '0':
                if pos + 3 > len(pattern) - 1:
                    nodes.append(PlainText('\x00', flags))
                    skip = 1
                if pattern[pos + 2] in OCTAL and pattern[pos + 3] in OCTAL:
                    nodes.append(PlainText(chr(int(
                        pattern[pos + 2] + pattern[pos + 3], base=8
                    )), flags))
                    skip = 3
                else:
                    nodes.append(PlainText('\x00', flags))
                    skip = 1
                continue
            elif next_char in {'X', 'x'}:
                if (
                    pos + 3 <= len(pattern) - 1 and
                    pattern[pos + 2] in HEXADECIMAL and
                    pattern[pos + 3] in HEXADECIMAL
                ):
                    nodes.append(PlainText(chr(int(
                        pattern[pos + 2] + pattern[pos + 3], base=16
                    ))))
                    skip = 3
                    continue
                else:
                    raise error('invalid hexadecimal literal escape')
            else:
                if next_char in _escape_nodes_map:
                    nodes.append(_escape_nodes_map[next_char](flags))
                elif next_char in _escape_needed_char:
                    nodes.append(PlainText(next_char))
                else:
                    nodes.append(PlainText(f'\\{next_char}'))
                skip = 1
        elif char in _count_map:
            if pos < len(pattern) - 1 and pattern[pos + 1] == '?':
                nodes, node = _find_last_repeatable(nodes)
                nodes.append(_count_map[char][1](node))
                skip = 1
            else:
                nodes, node = _find_last_repeatable(nodes)
                nodes.append(_count_map[char][0](node))
        elif char == '{':
            if pos == len(pattern) - 1:
                nodes.append(PlainText('{'))
                continue
            is_two = False
            nums = []
            broken = False
            for index in range(pos + 1, len(pattern) + 1):
                if pattern[index] in DECIMAL:
                    if len(nums) <= is_two:
                        nums.append('')
                    nums[is_two] = nums[is_two] + pattern[index]
                elif pattern[index] == ',':
                    if is_two:
                        broken = True
                        break
                    if not nums:
                        nums.append('')
                    nums.append('')
                    is_two = True
                elif pattern[index] == '}':
                    break
                else:
                    broken = True
                    break
            else:
                broken = True
            if not nums or broken:
                nodes.append(PlainText('{'))
                continue
            nodes, node = _find_last_repeatable(nodes)
            if index != len(pattern) - 1 and pattern(index + 1) == '?':
                skip = index + 1 - pos
                if len(nums) == 1:
                    nodes.append(NonGreedyRepeat(node, int(nums[0])))
                else:
                    nodes.append(NonGreedyRepeatRange(
                        node, int(nums[0]), int(nums[1])
                    ))
            else:
                skip = index - pos
                if len(nums) == 1:
                    nodes.append(GreedyRepeat(node, int(nums[0])))
                else:
                    nodes.append(GreedyRepeatRange(
                        node, int(nums[0]), int(nums[1])
                    ))
        elif char in _symbols_map:
            nodes.append(_symbols_map[char](flags))
        else:
            nodes.append(PlainText(char, flags))

    tokens = []
    is_plain = False
    plain = ''

    for node in nodes:
        if isinstance(node, PlainText):
            if is_plain:
                plain = f'{plain}{node.value}'
            else:
                is_plain = True
                plain = node.value
        else:
            if is_plain:
                is_plain = False
                if plain:
                    tokens.append(PlainText(plain, flags))
            tokens.append(node)

    if is_plain:
        is_plain = False
        tokens.append(PlainText(plain, flags))

    return Pattern(pattern, tokens, flags)


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


def purge() -> None:
    _cache.clear()
