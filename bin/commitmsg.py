#!/usr/bin/env python3

import subprocess
import re

def main():
    git_diff = subprocess.check_output(['git', 'diff', '--no-ext-diff', 'VERSIONS.md']).decode('utf-8')
    prefix_old = r"\-\*"
    prefix_new = r"\+\*"
    change_symbol = "->"
    changes = {}

    for line in git_diff.split('\n'):
        if re.match(f'^{prefix_old}.*', line):
            line_parts = line.replace('-* ','').split(':')
            item = line_parts[0].lower().strip()
            version = line_parts[1].lower().strip()
            changes[item] = f"{version} {change_symbol} "

        if re.match(f'^{prefix_new}.*', line):
            line_parts = line.replace('+* ', '').split(':')
            item = line_parts[0].lower().strip()
            version = line_parts[1].lower().strip()
            changes[item] = changes.get(item, '') + version

    message = ""
    for item, change in changes.items():
        if change_symbol in change:
            message += f"update {item} ({change}); "
        else:
            message += f"add {item} ({change}); "

    if not message:
        message = "[skip ci] update without version changes"

    print("COMMIT MESSAGE")
    print(message)

if __name__ == "__main__":
    main()
