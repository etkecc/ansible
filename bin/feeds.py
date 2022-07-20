import os
import sys
import argparse
from datetime import date
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Extracts release feeds from roles')
parser.add_argument('root_dir', help='Root dir which to traverse recursively for defaults/main.yml roles files')
parser.add_argument('action', help='Pass "check" to list roles with missing feeds or "dump" to dump an OPML file')
args = parser.parse_args()
if args.action not in ['check', 'dump']:
    sys.exit('Error: possible arguments are "check" or "dump"')

# full path is expected for excluded_roles, ex. '/ansible/roles/matrix/room-purger/defaults/main.yml'
excluded_roles = []
project_source_url_str = '# Project source code URL:'

def get_roles_files_from_dir(root_dir):
    file_paths = []
    for dir_name, sub_dur_list, file_list in os.walk(root_dir):
        for file_name in file_list:
            if not dir_name.endswith('defaults') or file_name != 'main.yml':
                continue
            if dir_name in excluded_roles:
                continue
            file_paths.append(os.path.join(dir_name, file_name))
    return file_paths

def get_git_repos_from_files(file_paths, break_on_missing_repos=False):
    git_repos = {}
    missing_repos = []

    for file in file_paths:
        docker_repo_val = ''
        file_lines = open(file, 'r').readlines()
        for line in file_lines:
            if 'docker_repo' in line:
                # extract the value from a line like this:
                # something_docker_repo: 'https://github.com/repository/here'
                text = line.split(': ')[1].strip().replace('\"', '')
                if validate_url(text):
                    docker_repo_val = text
                    break
            elif project_source_url_str in line:
                text = line.split(project_source_url_str)[1].strip()
                if validate_url(text):
                    docker_repo_val = text
                    break

        if docker_repo_val == '':
            missing_repos.append(file)
        else:
            git_repos[file] = docker_repo_val

    if break_on_missing_repos:
        print('Missing docker_repo var or {0} comment for:\n{1}'.format(project_source_url_str, '\n'.join(missing_repos)))

    return git_repos

def validate_url(text):
    if text == '':
        return False
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False


def format_feeds_from_git_repos(git_repos):
    feeds = {}
    for role, git_repo in git_repos.items():
        if 'github' in git_repo:
            atomFilePath = git_repo.replace('.git', '') + '/tags.atom'
        elif ('gitlab' in git_repo or 'mau.dev' in git_repo):
            atomFilePath = git_repo.replace('.git', '') + '/-/tags?format=atom'
        else:
            print('Unrecognized git repository: %s' % git_repo)
            continue

        role_name = role.split('/')[3].removeprefix('matrix-bot-').removeprefix('matrix-bridge-').removeprefix('matrix-client-').removeprefix('matrix-')
        feeds[role_name] = {
            'text': role_name,
            'title': role_name,
            'type': 'rss',
            'htmlUrl': git_repo,
            'xmlUrl': atomFilePath
        }
    return feeds

todays_date = date.today().strftime('%Y-%m-%d')

def dump_opml_file_from_feeds(feeds):
    tree = ET.ElementTree('tree')

    opml = ET.Element('opml', {'version': '1.0'})
    head = ET.SubElement(opml, 'head')

    title = ET.SubElement(head, 'title')
    title.text = 'Release feeds for roles'

    dateCreated = ET.SubElement(head, 'dateCreated')
    dateCreated.text = todays_date

    body = ET.SubElement(opml, 'body')
    for role, feed_dict in feeds.items():
        outline = ET.SubElement(body, 'outline', feed_dict)

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
