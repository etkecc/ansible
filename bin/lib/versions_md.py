"""Reading and writing VERSIONS.md, the flat '* Component: 1.2.3' list that is
the whole pipeline's source of truth. One parser here means versions.py,
versions.diff.py and commitmsg.py can't disagree about what a line means.
"""

import re


def parse(text):
    """VERSIONS.md text -> {component: version}. Ignores anything that isn't a
    '* name: version' bullet, so headers and blank lines pass through harmless.
    """
    versions = {}
    for line in text.splitlines():
        if not line.startswith('* '):
            continue
        component, version = line.split(": ", 1)
        versions[component.strip("* ")] = version.strip()
    return versions


def format_lines(versions):
    """{component: version} -> the VERSIONS.md body, sorted so the file is
    stable across runs and a diff only shows real version bumps.
    """
    return ''.join(f'* {key}: {value}\n' for key, value in sorted(versions.items()))


def parse_diff(diff_text):
    """A `git diff` of VERSIONS.md -> {component: "old -> new" | "new"}. Removed
    lines seed the old side, added lines fill the new; a component that only
    gained a line reads as a plain addition. Lowercased because the commit
    message wants it that way.
    """
    change_symbol = "->"
    changes = {}
    for line in diff_text.split('\n'):
        if re.match(r'^\-\*.*', line):
            parts = line.replace('-* ', '').split(':')
            changes[parts[0].lower().strip()] = f"{parts[1].lower().strip()} {change_symbol} "
        if re.match(r'^\+\*.*', line):
            parts = line.replace('+* ', '').split(':')
            item = parts[0].lower().strip()
            changes[item] = changes.get(item, '') + parts[1].lower().strip()
    return changes
