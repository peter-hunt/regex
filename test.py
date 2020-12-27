#!/usr/bin/env python3
"""
Tester for Regex Module

Usage:
    test <program-id> [options]
"""

from pathlib import Path

from docopt import docopt


def main(argv=None):
    args = docopt(__doc__, argv)

    if args['<program-id>'] is not None:
        program_id = args['<program-id>']
        path = Path(f'tests/{program_id}.py')

        if not path.exists():
            exit(f'{Path(__file__)}: {path}: No such file or directory')
        elif path.is_dir():
            exit(f'{Path(__file__)}: {path}: Is a directory')

        module = getattr(__import__(f'tests.{program_id}'), program_id)
        for funcname in module.__all__:
            getattr(module, funcname)()


if __name__ == '__main__':
    main()
