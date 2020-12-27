from regex import compile, fullmatch, match, DEBUG

__all__ = [
    'test_compile',
    'test_match',
]


def testfors(pattern, strings, flags=0):
    compiled = compile(pattern, flags)

    print()
    print(
        f'Compiled Pattern: {compiled}\n'
        f'Compiled Nodes: {compiled.nodes}\n\n'
    )

    for string in strings:
        print(
            f'Result for fullmatch(r{pattern!r}, {string!r}):\n'
            f'    {compiled.fullmatch(string)}\n'
        )

    print()

    for string in strings:
        print(
            f'Result for match(r{pattern!r}, {string!r}):\n'
            f'    {compiled.match(string)}\n'
        )


def testfor(pattern, string, flags=0):
    compiled = compile(pattern, flags)

    print()
    print(
        f'Compiled Pattern: {compiled}\n'
        f'Compiled Nodes: {compiled.nodes}\n'
        f'\nResult for fullmatch(r{pattern!r}, {string!r}):\n'
        f'    {compiled.fullmatch(string)}\n'
        f'\nResult for match(r{pattern!r}, {string!r}):\n'
        f'    {compiled.match(string)}\n'
    )


def test_compile():
    compiled = compile(r'a', DEBUG)

    print()
    print(
        f'Compiled Pattern: {compiled}\n'
        f'Compiled Nodes: {compiled.nodes}\n'
    )


def test_match():
    pattern = r'12{2,3}'
    strings = [
        '12',
        '122',
        '1222',
        '12222',
    ]

    testfor(pattern, strings[2])
