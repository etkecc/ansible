#!/usr/bin/env python3

import os
import re
import yaml

ignored = [
    'matrix_synapse_default_room_version',
]
prefixes = [
    'matrix_',
    'custom_',
    'int_',
    'synapse_default_',
    'synapse_ext_',
    'mailer_container_',
    'bot_',
    'client_',
    'mautrix_',
    'devture_',
    'beeper_',
    'backup_borg_',
]
suffixes = [
    '_version',
]


def find_versions(roles):
    matches = {}
    for root, dirs, files in os.walk('.'):
        if root.endswith('defaults'):
            if not any(role in root for role in roles):
                continue
            for file in files:
                if file.endswith('main.yml'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        data = yaml.safe_load(f)
                        for key, value in data.items():
                            if key.endswith('_version') and value and not re.search(r'{{|master|main|""', str(value)) and key not in ignored:
                                sanitized_key = sanitize_key(key)
                                matches[sanitized_key] = value
    return matches


def sanitize_key(key):
    for prefix in prefixes:
        key = key.removeprefix(prefix)
    for suffix in suffixes:
        key = key.removesuffix(suffix)
    return key.replace('_', ' ').title()

def get_active_roles_from_play(play_file):
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


def generate_versions():
    roles = get_active_roles_from_play(os.path.join(os.getcwd(), 'play/all.yml'))
    versions = find_versions(roles)
    with open(os.path.join(os.getcwd(), 'VERSIONS.md'), 'w') as f:
        for key, value in sorted(versions.items()):
            f.write(f'* {key}: {value}\n')


if __name__ == "__main__":
    generate_versions()
