#!/usr/bin/env python3

"""Writes VERSIONS.diff.md, the weekly "what changed" digest for
#updates:etke.cc. Diffs VERSIONS.md between two branches and, for every bumped
component, links its name and both versions to the upstream repo.

The repo map is keyed by naming.component_name(var), the exact same name
versions.py writes into VERSIONS.md. That is the whole point of this rewrite:
the old version derived the key from the role DIRECTORY instead, and whenever a
directory and its variable disagreed the link quietly vanished. Same function,
same source, no disagreement possible.
"""

import os
import subprocess
import sys
import urllib.error
import urllib.request

from lib import naming, repos, roles, urls, versions_md

OLD_BRANCH = "main"
NEW_BRANCH = "fresh"
VERSIONS_FILE = "VERSIONS.md"


def build_repo_map(role_files):
    """component name -> upstream repo URL. A role's single source repo covers
    every *_version it pins, so every one of those vars gets its own link.

    Two roles can bridge the same service and derive to one component name
    (beeper-linkedin and mautrix-linkedin both land on "LinkedIn Bridge"). The
    last role wins, and role_files arrives in play/all.yml order, so put the
    superseding role below the one it replaces in the play and its repo is the
    one that gets linked.
    """
    repo_map = {}
    for file in role_files:
        with open(file, 'r') as handle:
            urls_found = repos.source_urls(handle.readlines())
        if not urls_found:
            continue
        if len(urls_found) > 1:
            print(f'Warning: {file} declares {len(urls_found)} source repos; '
                  f'diff links use the first ({urls_found[0]}).')
        repo = urls_found[0]
        for var, _ in roles.version_vars(file):
            repo_map[naming.component_name(var)] = repo
    return repo_map


def _file_at_branch(branch, file_path):
    return subprocess.check_output(['git', 'show', f'{branch}:{file_path}']).decode()


def version_changes(old_branch, new_branch, file_path):
    """(component, old, new) for every component that changed between the two
    branches; old is None for a brand-new one. When new_branch is the current
    HEAD we read the working tree instead of the committed blob, so an
    uncommitted regenerate still diffs.
    """
    old_versions = versions_md.parse(_file_at_branch(old_branch, file_path))

    head = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    new_ref = subprocess.check_output(['git', 'rev-parse', new_branch]).decode().strip()
    if new_ref == head:
        with open(file_path, 'r') as handle:
            new_versions = versions_md.parse(handle.read())
    else:
        new_versions = versions_md.parse(_file_at_branch(new_branch, file_path))

    changes = []
    for component, new_version in new_versions.items():
        old_version = old_versions.get(component)
        if old_version is None:
            changes.append((component, None, new_version))
        elif old_version != new_version:
            changes.append((component, old_version, new_version))
    return changes


def _http_status(url):
    """The HTTP status for url, or None if the forge couldn't be reached at all.
    A real 404 comes back as 404; a timeout or DNS failure comes back as None so
    the caller can tell "the tag doesn't exist" from "github didn't answer".
    """
    request = urllib.request.Request(url, headers={'User-Agent': 'etke-versions-diff'})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status
    except urllib.error.HTTPError as err:
        code = err.code
        err.close()
        return code
    except Exception:
        return None


def _pick_release_url(candidates, probe=_http_status):
    """Pick the tag URL to link and say how sure we are, as (url, status):
      'ok'         a candidate answered 2xx/3xx, link it, done.
      'broken'     every candidate answered a flat 404, the tag is genuinely
                   gone: link nothing, render plain text.
      'unverified' the forge stonewalled us (timeout, or a 429/5xx that is NOT
                   a 404): keep the best guess and link it, but say we couldn't
                   confirm. Only a real 404 condemns a URL; a rate-limit must
                   not, or a busy week drops every link at once.
    """
    unverified = None
    for url in candidates:
        code = probe(url)
        if code is not None and 200 <= code < 400:
            return url, 'ok'
        if code != 404 and unverified is None:
            unverified = url
    if unverified is not None:
        return unverified, 'unverified'
    return None, 'broken'


def _version_link(version, repo, dropped, unverified):
    """The version linked to a tag URL that exists, or bare text when it doesn't.
    A dead tag goes in dropped (rendered plain, no "[1.2.3](404)" ever ships); a
    tag we couldn't check goes in unverified (still linked, just flagged).
    """
    url, status = _pick_release_url(urls.release_url_candidates(repo, version))
    if status == 'broken':
        dropped.append((repo, version))
        return version
    if status == 'unverified':
        unverified.append((repo, version))
    return f"[{version}]({url})"


def write_diff(changes, repo_map):
    """Write VERSIONS.diff.md and return (dropped, unverified): the (repo,
    version) pairs whose tag URL was a dead 404, and the ones the forge wouldn't
    confirm, so the caller can report both.
    """
    dropped, unverified = [], []
    with open(os.path.join(os.getcwd(), 'VERSIONS.diff.md'), 'w') as f:
        f.write("## Weekly Recap\n\n")
        f.write("> These updates were originally shared in #updates:etke.cc and are collected here in a weekly digest for convenience.\n\n")
        f.write("---\n\n")
        f.write("### Component Updates\n\n")
        for component, old_version, new_version in changes:
            if old_version == new_version or new_version is None:
                continue
            if component in repo_map:
                repo = repo_map[component]
                component_link = f"[{component}]({repo})"
                old_version_url = _version_link(old_version, repo, dropped, unverified) if old_version else old_version
                new_version_url = _version_link(new_version, repo, dropped, unverified)
            else:
                component_link = component
                old_version_url = old_version
                new_version_url = new_version
            if old_version is None:
                f.write(f"* {component_link}: {new_version_url} _new_\n")
            else:
                f.write(f"* {component_link}: {old_version_url} ⇾ {new_version_url}\n")
    return dropped, unverified


if __name__ == "__main__":
    active = roles.active_roles(os.path.join('.', 'play', 'all.yml'))
    role_files = roles.role_default_files('.', active=active)
    repo_map = build_repo_map(role_files)
    changes = version_changes(OLD_BRANCH, NEW_BRANCH, VERSIONS_FILE)

    if not changes:
        print("No changes detected in VERSIONS.md. Skipping generation of VERSIONS.diff.md")
        exit(0)

    dropped, unverified = write_diff(changes, repo_map)
    print("VERSIONS.diff.md generated successfully")

    if dropped:
        print(f'\n{len(dropped)} release link(s) had no working tag URL and '
              f'shipped as plain text. Worth a look, the pin or the source URL '
              f'is probably off:', file=sys.stderr)
        for repo, version in dropped:
            print(f'  {version}  {repo}', file=sys.stderr)

    if unverified:
        print(f'\n{len(unverified)} release link(s) went out unverified, the '
              f'forge would not answer (rate limit, timeout). Kept the link, but '
              f'no promise it resolves:', file=sys.stderr)
        for repo, version in unverified:
            print(f'  {version}  {repo}', file=sys.stderr)
