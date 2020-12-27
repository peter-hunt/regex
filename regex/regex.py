from .pattern import _special_chars_map, compile


__all__ = [
    'search',
    'match',
    'fullmatch',
    'split',
    'findall',
    'finditer',
    'sub',
    'subn',
    'escape',
]


def search(pattern, string, flags=0):
    pass


def match(pattern, string, flags=0):
    return compile(pattern, flags).match(string)


def fullmatch(pattern, string, flags=0):
    return compile(pattern, flags).fullmatch(string)


def split(pattern, string, maxsplit=0, flags=0):
    pass


def findall(pattern, string, flags=0):
    pass


def finditer(pattern, string, flags=0):
    pass


def sub(pattern, repl, string, count=0, flags=0):
    pass


def subn(pattern, repl, string, count=0, flags=0):
    pass


def escape(pattern):
    return pattern.translate(_special_chars_map)
