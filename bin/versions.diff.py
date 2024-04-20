#!/usr/bin/env python3

import difflib
import git
import os
from urllib.parse import urlparse

project_source_url_str = '# Project source code URL:'

def get_roles_files_from_dir(root_dir):
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
            if project_source_url_str in line:
                # extract the value from a line like this:
                # Project source code URL: https://github.com/mautrix/signal
                project_repo_val = line.split(project_source_url_str)[1].strip()
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
    new_content = new_version.data_stream.read().decode().splitlines()

    differ = difflib.Differ()
    diff = list(differ.compare(old_content, new_content))

    added_or_changed_lines = []
    for line in diff:
        if line.startswith('- * '):
            component, old_version = parse_version_line(line[2:])
            added_or_changed_lines.append((component, old_version, None))
        elif line.startswith('+ * '):
            component, new_version = parse_version_line(line[2:])
            added_or_changed_lines[-1] = (component, added_or_changed_lines[-1][1], new_version)

    return added_or_changed_lines

if __name__ == "__main__":
    repo_path = "."
    old_branch = "master"
    new_branch = "fresh"
    file_path = "VERSIONS.md"

    role_files = get_roles_files_from_dir(repo_path)
    git_repos = get_git_repos_from_files(role_files)
    added_or_changed_lines = get_version_diff(repo_path, old_branch, new_branch, file_path)

    if len(added_or_changed_lines) == 0:
        print("no changes detected in VERSIONS.md, skipping generation of VERSIONS.diff.md")
        exit(0)

    with open(os.path.join(os.getcwd(), 'VERSIONS.diff.md'), 'w') as f:
        f.write("**Stable Updates Published**\n\n")
        for component, old_version, new_version in added_or_changed_lines:
            if component in git_repos:
                component_link = f"[{component}]({git_repos[component]})"
            else:
                component_link = component
            f.write(f"* {component_link}: {old_version} -> {new_version}\n")

    print("VERSIONS.diff.md generated successfully")
