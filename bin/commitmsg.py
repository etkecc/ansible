#!/usr/bin/env python3

"""Prints the commit message for a VERSIONS.md bump: 'update foo (1 -> 2); add
bar (3); ...'. Reads the working-tree diff of VERSIONS.md and lets
versions_md.parse_diff do the line reading, so the parsing lives in one place.
"""

import subprocess

from lib import versions_md

CHANGE_SYMBOL = "->"


def format_message(changes):
    """The one-line commit message from parse_diff's {item: change} map. A bare
    old version with nothing after the arrow means the component was dropped, so
    it reads "remove", not a dangling "update foo (1.2.3 -> )".
    """
    message = ""
    for item, change in changes.items():
        if change.rstrip().endswith(CHANGE_SYMBOL):
            old = change.replace(CHANGE_SYMBOL, '').strip()
            message += f"remove {item} ({old}); "
        elif CHANGE_SYMBOL in change:
            message += f"update {item} ({change}); "
        else:
            message += f"add {item} ({change}); "
    return message or "[skip ci] update without version changes"


def main():
    git_diff = subprocess.check_output(['git', 'diff', '--no-ext-diff', 'VERSIONS.md']).decode('utf-8')
    print("COMMIT MESSAGE")
    print(format_message(versions_md.parse_diff(git_diff)))


if __name__ == "__main__":
    main()
