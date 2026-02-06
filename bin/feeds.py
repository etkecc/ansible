import os
import sys
import argparse
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Extracts release feeds from roles')
parser.add_argument('root_dir', help='Root dir which to traverse recursively for defaults/main.yml roles files')
parser.add_argument('action', help='Pass "check" to list roles with missing feeds or "dump" to dump an OPML file')
args = parser.parse_args()
if args.action not in ['check', 'dump']:
    sys.exit('Error: possible arguments are "check" or "dump"')

excluded_paths = [
    # appservice-kakaotalk defines a Project URL, but that Gitea repository does not have an Atom/RSS feed.
    # It doesn't have any tags anyway.
    './upstream/roles/custom/matrix-bridge-appservice-kakaotalk/defaults',
]
project_source_url_str = '# Project source code URL:'

HOST_FEED_RULES = {
    # host: rule
    # rule options:
    #   "github"
    #   "gitlab"
    #   "cgit"
    #   "gitea"
    #   "forgejo"
    'github.com': 'github',
    'gitlab.com': 'gitlab',
    'mau.dev': 'gitlab',
    'framagit.org': 'gitlab',
    'dev.funkwhale.audio': 'gitlab',
    'codeberg.org': 'forgejo',
    'git.zx2c4.com': 'cgit',
    'git.osgeo.org': 'gitea',
    'forgejo.ellis.link': 'forgejo',
    'app.radicle.xyz': 'radicle',
}

HOST_FEED_TEMPLATES = {
    # host: url template override
    # template variables:
    #   {repo} - repository url without trailing slash or .git
    'forgejo.ellis.link': '{repo}/atom/',
}

RULE_TEMPLATES = {
    'github': '{repo}/releases.atom',
    'gitlab': '{repo}/-/tags?format=atom',
    'cgit': '{repo}/atom/',
    'gitea': '{repo}.atom',
    'forgejo': '{repo}/releases.atom',
}

def get_roles_files_from_dir(root_dir):
    file_paths = []
    for dir_name, sub_dur_list, file_list in os.walk(root_dir):
        for file_name in file_list:
            if not dir_name.endswith('defaults') or file_name != 'main.yml':
                continue
            if dir_name in excluded_paths:
                continue
            file_paths.append(os.path.join(dir_name, file_name))
    return file_paths

def get_git_repos_from_files(file_paths, break_on_missing_repos=False):
    git_repos = {}
    missing_repos = []

    for file in file_paths:
        with open(file, 'r') as handle:
            file_lines = handle.readlines()
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
                    git_repos[file] = []

                git_repos[file].append(project_repo_val)
                found_project_repo = True

        if not found_project_repo:
            missing_repos.append(file)

    if break_on_missing_repos and len(missing_repos) > 0:
        print('Missing `{0}` comment for:\n{1}'.format(project_source_url_str, '\n'.join(missing_repos)))

    return git_repos

def validate_url(text):
    if text == '':
        return False
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_hostname(text):
    try:
        result = urlparse(text)
        if not result.hostname:
            return ''
        return result.hostname.lower()
    except:
        return ''

def get_feed_rule_for_host(host):
    if not host:
        return ''
    if host in HOST_FEED_RULES:
        return HOST_FEED_RULES[host]
    if host.endswith('.github.com'):
        return 'github'
    return ''

def normalize_repo_url(url):
    repo_url = url
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    return repo_url.rstrip('/')

def build_feed_url(repo_url, rule, host):
    if rule == 'radicle':
        return ''
    repo_base = normalize_repo_url(repo_url)
    template = HOST_FEED_TEMPLATES.get(host) or RULE_TEMPLATES.get(rule, '')
    if not template:
        return ''
    return template.format(repo=repo_base)

def format_feeds_from_git_repos(git_repos):
    feeds = {
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
    for role, git_repos in git_repos.items():
        for idx, git_repo in enumerate(git_repos):
            host = get_hostname(git_repo)
            rule = get_feed_rule_for_host(host)
            if rule == 'radicle':
                print('No Atom feed available for Radicle repo, skipping: %s' % git_repo)
                continue
            atomFilePath = build_feed_url(git_repo, rule, host)
            if not atomFilePath:
                print('Unrecognized git repository: %s' % git_repo)
                continue

            role_name = role.split('/')[4]
            if role_name == 'defaults':
                role_name = role.split('/')[3]
            role_name = role_name.removeprefix('matrix-bot-').removeprefix('matrix-bridge-').removeprefix('matrix-client-').removeprefix('matrix-')
            if idx > 0:
                # there is more than 1 project source code for this role
                role_name += '-' + str(idx+1)

            feeds[role_name] = {
                'text': role_name,
                'title': role_name,
                'type': 'rss',
                'htmlUrl': git_repo,
                'xmlUrl': atomFilePath
            }

    feeds = {key: val for key, val in sorted(feeds.items(), key = lambda item: item[0])}
    return feeds

def dump_opml_file_from_feeds(feeds):
    tree = ET.ElementTree()

    opml = ET.Element('opml', {'version': '1.0'})
    head = ET.SubElement(opml, 'head')

    title = ET.SubElement(head, 'title')
    title.text = 'Release feeds for roles'

    body = ET.SubElement(opml, 'body')
    for role, feed_dict in feeds.items():
        ET.SubElement(body, 'outline', feed_dict)

    ET.indent(opml)
    tree._setroot(opml)
    file_name = 'releases.opml'
    tree.write(file_name, encoding = 'UTF-8', xml_declaration = True)
    print('Generated %s' % file_name)

if __name__ == '__main__':
    file_paths = get_roles_files_from_dir(root_dir=args.root_dir)
    break_on_missing = args.action == 'check'
    git_repos = get_git_repos_from_files(file_paths=file_paths, break_on_missing_repos=break_on_missing)
    feeds = format_feeds_from_git_repos(git_repos)

    if args.action == 'dump':
        dump_opml_file_from_feeds(feeds)
