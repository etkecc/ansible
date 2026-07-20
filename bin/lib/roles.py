"""Finding the roles that actually ship and reading their version pins out
of defaults/main.yml. Three scripts each walked the tree their own slightly
different way; this is the one walk they now share.
"""

import os
import re

import yaml

from lib import naming


def active_roles(play_file):
    """The roles play/all.yml actually enables, in order. A role entry is
    either a bare string or a {'role': name} mapping; anything else is a
    malformed playbook and we say so out loud rather than guess.
    """
    roles = []
    with open(play_file, 'r') as f:
        play = yaml.safe_load(f)
        for role in play[0].get('roles', []):
            if isinstance(role, str):
                roles.append(role)
            elif isinstance(role, dict) and 'role' in role:
                roles.append(role['role'])
            else:
                print(f"Unexpected role format in {play_file}: {role}")
    return roles


def role_default_files(root, active=None, exclude=None):
    """Every defaults/main.yml under root. Pass active to keep only the roles
    the play enables (substring match against the dir path, same as before);
    pass exclude to drop any dir at or under a given path prefix (feeds skips
    the feedless Gitea repo, and the scripts' own bin/tests fixtures). Leave
    both off and you get the lot.
    """
    exclude = exclude or []
    file_paths = []
    for dir_name, _, file_list in os.walk(root):
        if not dir_name.endswith('defaults'):
            continue
        if active is not None and not any(role in dir_name for role in active):
            continue
        if any(dir_name == prefix or dir_name.startswith(prefix + '/') for prefix in exclude):
            continue
        for file_name in file_list:
            if file_name == 'main.yml':
                file_paths.append(os.path.join(dir_name, file_name))
    return file_paths


def version_vars(file):
    """The (var, value) pairs in one defaults file that name a real component
    release. Skips templated pins ({{ ... }}), rolling tags (master/main),
    empty values, and the handful of _version vars that aren't releases at all
    (IGNORED). Returns pairs, not names, so the caller decides how to key them.
    """
    with open(file, 'r') as f:
        data = yaml.safe_load(f)
    pairs = []
    for key, value in data.items():
        if (key.endswith('_version') and value
                and not re.search(r'{{|master|main|""', str(value))
                and key not in naming.IGNORED):
            pairs.append((key, value))
    return pairs


def role_name_from_path(file):
    """The role directory name from a .../<role>/defaults/main.yml path. Reads
    it as the segment right before 'defaults' instead of a fixed split index,
    so a role nested one level deeper doesn't silently mis-slug.
    """
    parts = file.split('/')
    if 'defaults' in parts:
        return parts[parts.index('defaults') - 1]
    return parts[-2]
