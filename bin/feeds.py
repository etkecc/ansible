#!/usr/bin/env python3

"""Builds releases.opml, the OPML feed list a human can import to watch every
role's upstream for new releases. 'check' just names the roles we couldn't find
a source repo for; 'dump' writes the file. Role discovery, source extraction
and feed-URL shaping all come from lib now, shared with the version scripts.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET

from lib import naming, repos, roles, urls

# Dirs to keep out of the walk (matched as path prefixes, rooted at the '.' the
# justfile passes). bin/tests holds this package's own role fixtures, which are
# not real roles and must never reach releases.opml.
EXCLUDED_PATHS = [
    './bin/tests',
]

# Feeds with no role behind them, or whose upstream lives somewhere the role
# defaults don't point at. Hand-kept.
FEED_SEEDS = {
    'ansible': {
        'text': 'ansible',
        'title': 'ansible',
        'type': 'rss',
        'htmlUrl': 'https://pypi.org/project/ansible/#history',
        'xmlUrl': 'https://pypi.org/rss/project/ansible/releases.xml'
    },
    'ansible-core': {
        'text': 'ansible-core',
        'title': 'ansible-core',
        'type': 'rss',
        'htmlUrl': 'https://pypi.org/project/ansible-core/#history',
        'xmlUrl': 'https://pypi.org/rss/project/ansible-core/releases.xml'
    },
    'alpinelinux': {
        'text': 'alpinelinux',
        'title': 'alpinelinux',
        'type': 'rss',
        'htmlUrl': 'https://github.com/alpinelinux/aports/releases',
        'xmlUrl': 'https://github.com/alpinelinux/aports/releases.atom'
    },
    'borg': {
        'text': 'borg',
        'title': 'borg',
        'type': 'rss',
        'htmlUrl': 'https://github.com/borgbackup/borg/releases',
        'xmlUrl': 'https://github.com/borgbackup/borg/releases.atom'
    },
    'borgmatic': {
        'text': 'borgmatic',
        'title': 'borgmatic',
        'type': 'rss',
        'htmlUrl': 'https://github.com/borgmatic-collective/borgmatic/releases',
        'xmlUrl': 'https://github.com/borgmatic-collective/borgmatic/releases.atom'
    },
    'mautrix-go': {
        'text': 'mautrix-go',
        'title': 'mautrix-go',
        'type': 'rss',
        'htmlUrl': 'https://github.com/mautrix/go/releases',
        'xmlUrl': 'https://github.com/mautrix/go/releases.atom'
    },
}


def collect_repos(role_files, report_missing=False):
    """{defaults-file: [source repo URLs]} for every role that has one. In check
    mode, print the roles that came up empty so someone can add a source.
    """
    repos_by_file = {}
    missing = []
    for file in role_files:
        with open(file, 'r') as handle:
            found = repos.source_urls(handle.readlines())
        if found:
            repos_by_file[file] = found
        else:
            missing.append(file)
    if report_missing and missing:
        print('No source repo found for:\n{0}'.format('\n'.join(missing)))
    return repos_by_file


def build_feeds(repos_by_file):
    """The seed feeds plus one entry per role source repo, keyed by feed slug
    and sorted. A role pointing at two repos gets a '-2' on the second. Repos on
    a host with no feed (radicle) or one we don't recognize are announced and
    skipped rather than faked.
    """
    feeds = dict(FEED_SEEDS)
    for file, repo_urls in repos_by_file.items():
        for idx, repo in enumerate(repo_urls):
            rule = urls.feed_rule_for_host(repos.hostname(repo))
            if rule == 'radicle':
                print('No Atom feed available for Radicle repo, skipping: %s' % repo)
                continue
            feed = urls.feed_url(repo)
            if not feed:
                print('Unrecognized git repository: %s' % repo)
                continue
            slug = naming.role_slug(roles.role_name_from_path(file))
            if idx > 0:
                slug += '-' + str(idx + 1)
            feeds[slug] = {
                'text': slug,
                'title': slug,
                'type': 'rss',
                'htmlUrl': repo,
                'xmlUrl': feed,
            }
    return {key: feeds[key] for key in sorted(feeds)}


def dump_opml(feeds):
    opml = ET.Element('opml', {'version': '1.0'})
    head = ET.SubElement(opml, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'Release feeds for roles'

    body = ET.SubElement(opml, 'body')
    for _, feed_dict in feeds.items():
        ET.SubElement(body, 'outline', feed_dict)

    ET.indent(opml)
    tree = ET.ElementTree()
    tree._setroot(opml)
    file_name = 'releases.opml'
    tree.write(file_name, encoding='UTF-8', xml_declaration=True)
    print('Generated %s' % file_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts release feeds from roles')
    parser.add_argument('root_dir', help='Root dir which to traverse recursively for defaults/main.yml roles files')
    parser.add_argument('action', help='Pass "check" to list roles with missing feeds or "dump" to dump an OPML file')
    args = parser.parse_args()
    if args.action not in ['check', 'dump']:
        sys.exit('Error: possible arguments are "check" or "dump"')

    role_files = roles.role_default_files(args.root_dir, exclude=EXCLUDED_PATHS)
    repos_by_file = collect_repos(role_files, report_missing=args.action == 'check')
    feeds = build_feeds(repos_by_file)

    if args.action == 'dump':
        dump_opml(feeds)
