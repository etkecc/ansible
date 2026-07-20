#!/usr/bin/env python3

"""Writes VERSIONS.md: every active role's pinned component version, one bullet
each. The name each component gets is naming.component_name, the same function
versions.diff.py keys its links by, so the two can never drift apart again.
"""

import os

from lib import naming, roles, versions_md


def generate_versions():
    active = roles.active_roles(os.path.join(os.getcwd(), 'play/all.yml'))
    versions = {}
    for file in roles.role_default_files('.', active=active):
        for var, value in roles.version_vars(file):
            versions[naming.component_name(var)] = value
    with open(os.path.join(os.getcwd(), 'VERSIONS.md'), 'w') as out:
        out.write(versions_md.format_lines(versions))


if __name__ == "__main__":
    generate_versions()
