#!/usr/bin/env python3

import git
import os
import yaml
from urllib.parse import urlparse

PROJECT_SOURCE_URL_STR = '# Project source code URL:'
FORK_SOURCE_URL_STR = '# Fork source code URL:'


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

def get_roles_files_from_dir(root_dir, active_roles):
    file_paths = []
    for dir_name, _, file_list in os.walk(root_dir):
        if not any(role in dir_name for role in active_roles):
            continue
        for file_name in file_list:
            if dir_name.endswith('defaults') and file_name == 'main.yml':
                file_paths.append(os.path.join(dir_name, file_name))
    return file_paths


def get_roles_files_from_dir_old(root_dir):
    file_paths = []
    for dir_name, _, file_list in os.walk(root_dir):
        for file_name in file_list:
            if dir_name.endswith('defaults') and file_name == 'main.yml':
                file_paths.append(os.path.join(dir_name, file_name))
    return file_paths


def get_git_repos_from_files(file_paths):
    git_repos = {}
    for file in file_paths:
        role_name = file.split('/')[4]
        if role_name == 'defaults':
            role_name = file.split('/')[3]
        role_name = role_name.removeprefix('matrix-bot-').removeprefix('matrix-bridge-').removeprefix('matrix-client-').removeprefix('matrix-').removeprefix('mautrix-')
        role_name = role_name.replace('-', '_').replace('_', ' ').title()
        file_lines = open(file, 'r').readlines()
        found_project_repo = False
        for line in file_lines:
            project_repo_val = ''
            if PROJECT_SOURCE_URL_STR in line:
                # extract the value from a line like this:
                # Project source code URL: https://github.com/mautrix/signal
                project_repo_val = line.split(PROJECT_SOURCE_URL_STR)[1].strip()
                if not validate_url(project_repo_val):
                    print('Invalid url for line ', line)
                    break
            if FORK_SOURCE_URL_STR in line:
                # extract the value from a line like this:
                # Fork source code URL: https://github.com/mautrix/signal
                project_repo_val = line.split(FORK_SOURCE_URL_STR)[1].strip()
                if not validate_url(project_repo_val):
                    print('Invalid url for line ', line)
                    break
            if project_repo_val != '':
                if file not in git_repos:
                    git_repos[role_name] = ''

                git_repos[role_name] = project_repo_val
                found_project_repo = True
    return git_repos


def validate_url(text):
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_version_url(repo_url, version):
    custom = get_version_url_custom(repo_url, version)
    if custom:
        return custom

    if 'github' in repo_url:
        return f"{repo_url}/releases/tag/{version}"
    elif any(substring in repo_url for substring in ['gitlab', 'mau.dev', 'dev.funkwhale.audio']):
        return f"{repo_url}/-/tags/{version}"
    else:
        print(f'Unrecognized git repository: {repo_url}')
        return None


def get_version_url_custom(repo_url, version):
    if 'github.com/nginx/nginx' in repo_url:
        version = version.split('-')[0]
        return f"{repo_url}/releases/tag/release-{version}"

    if 'github.com/coturn/coturn' in repo_url:
        return f"{repo_url}/releases/tag/docker%2F{version}"

    github_repos = ['github.com/matrix-org/rageshake', 'github.com/Snapchat/KeyDB',
                    'github.com/grafana/grafana', 'github.com/Tecnativa/docker-socket-proxy',
                    'github.com/the-draupnir-project/Draupnir', 'github.com/Erikvl87/docker-languagetool',
                    'github.com/sissbruecker/linkding', 'github.com/SchildiChat/schildichat-desktop',
                    'github.com/element-hq/lk-jwt-service', 'github.com/hifi/heisenbridge',
                    'codeberg.org/superseriousbusiness/gotosocial',]

    if not version.startswith('v') and any(repo in repo_url for repo in github_repos):
        return f"{repo_url}/releases/tag/v{version}"

    return None


def parse_version_line(line):
    component, version = line.split(": ", 1)
    return component.strip("* "), version.strip()


def get_version_diff(repo_path, old_branch, new_branch, file_path):
    repo = git.Repo(repo_path)

    old_commit = repo.commit(old_branch)
    new_commit = repo.commit(new_branch)

    old_version = old_commit.tree / file_path
    new_version = new_commit.tree / file_path

    old_content = old_version.data_stream.read().decode().splitlines()
    if new_commit == repo.head.commit:
        new_content = open(file_path, 'r').read().splitlines()
    else:
        new_content = new_version.data_stream.read().decode().splitlines()

    old_versions = {}
    new_versions = {}
    for line in old_content:
        if line.startswith('* '):
            component, version = parse_version_line(line)
            old_versions[component] = version
    for line in new_content:
        if line.startswith('* '):
            component, version = parse_version_line(line)
            new_versions[component] = version

    changes = []
    for component in new_versions.keys():
        if component not in old_versions:
            changes.append((component, None, new_versions[component]))
        elif old_versions[component] != new_versions[component]:
            changes.append((component, old_versions[component], new_versions[component]))

    return changes


if __name__ == "__main__":
    repo_path = "."
    old_branch = "main"
    new_branch = "fresh"
    file_path = "VERSIONS.md"

    roles = get_active_roles_from_play(os.path.join(repo_path, 'play', 'all.yml'))
    role_files = get_roles_files_from_dir(repo_path, roles)
    git_repos = get_git_repos_from_files(role_files)
    added_or_changed_lines = get_version_diff(repo_path, old_branch, new_branch, file_path)

    if not added_or_changed_lines:
        print("No changes detected in VERSIONS.md. Skipping generation of VERSIONS.diff.md")
        exit(0)

    with open(os.path.join(os.getcwd(), 'VERSIONS.diff.md'), 'w') as f:
        f.write("## Weekly Recap\n\n")
        f.write("> The following changes were introduced this week and mentioned in #updates:etke.cc. ")
        f.write("This summary ensures no one missed them.\n\n")
        f.write("---\n\n")
        f.write("### Component Updates\n\n")
        f.write("#### Version Changes\n\n")
        for component, old_version, new_version in added_or_changed_lines:
            if old_version == new_version or new_version is None:
                continue
            if component in git_repos:
                component_link = f"[{component}]({git_repos[component]})"
                if old_version:
                    old_version_url = f"[{old_version}]({get_version_url(git_repos[component], old_version)})"
                else:
                    old_version_url = old_version
                new_version_url = f"[{new_version}]({get_version_url(git_repos[component], new_version)})"
            else:
                component_link = component
                old_version_url = old_version
                new_version_url = new_version
            if old_version is None:
                f.write(f"* {component_link}: {new_version_url} _new_\n")
            else:
                f.write(f"* {component_link}: {old_version_url} ⇾ {new_version_url}\n")

    print("VERSIONS.diff.md generated successfully")
