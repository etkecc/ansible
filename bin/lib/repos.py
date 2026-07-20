"""Digging the upstream source repo out of a role's defaults file, plus the
small URL helpers everyone needs. A role names its repo in a comment; a
self-built role hides it in a *_self_build_repo var instead. We check both.
"""

from urllib.parse import urlparse

import yaml

PROJECT_SOURCE_URL_STR = '# Project source code URL:'
FORK_SOURCE_URL_STR = '# Fork source code URL:'


def validate_url(text):
    """True only if text is a real absolute URL, scheme and host both present.
    Empty string is an easy no; a malformed one urlparse chokes on is also a no.
    """
    if text == '':
        return False
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def hostname(text):
    """Lowercased host of a URL, or '' if it hasn't got one. Feed rules key off
    this, so 'GitHub.com' and 'github.com' had better land in the same bucket.
    """
    try:
        result = urlparse(text)
        if not result.hostname:
            return ''
        return result.hostname.lower()
    except Exception:
        return ''


def normalize_repo_url(url):
    """Strip the .git and any trailing slash so a repo URL is the plain base a
    feed/release template can build on. github.com/foo/bar.git -> .../bar.
    """
    repo_url = url
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    return repo_url.rstrip('/')


def source_urls(file_lines):
    """Every upstream source URL declared in one defaults file, in the order it
    appears. Reads the Project and Fork comment lines first; if a role declares
    neither (the self-built bridges, e.g. steam), falls back to its
    *_self_build_repo var so those don't silently drop off the map. Returns a
    list, possibly empty. Invalid URLs are complained about and skipped.
    """
    urls = []
    for line in file_lines:
        marker = None
        if PROJECT_SOURCE_URL_STR in line:
            marker = PROJECT_SOURCE_URL_STR
        elif FORK_SOURCE_URL_STR in line:
            marker = FORK_SOURCE_URL_STR
        if marker is None:
            continue
        value = line.split(marker)[1].strip()
        if validate_url(value):
            urls.append(value)
        else:
            print('Invalid url for line ', line)

    if urls:
        return urls

    data = yaml.safe_load(''.join(file_lines)) or {}
    for key, val in data.items():
        if key.endswith('_self_build_repo') and isinstance(val, str):
            repo_url = normalize_repo_url(val)
            if validate_url(repo_url):
                urls.append(repo_url)
            break
    return urls
