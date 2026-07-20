import os

from conftest import FIXTURES

from lib import repos

ROLES = os.path.join(FIXTURES, 'roles')


def _lines(role):
    with open(os.path.join(ROLES, role, 'defaults', 'main.yml')) as f:
        return f.readlines()


def test_project_comment_url():
    assert repos.source_urls(_lines('matrix-bridge-signal')) == ['https://github.com/mautrix/signal']


def test_fork_comment_url():
    lines = ['# Fork source code URL: https://github.com/etkecc/synapse\n', 'x_version: "1"\n']
    assert repos.source_urls(lines) == ['https://github.com/etkecc/synapse']


def test_self_build_fallback_strips_git_suffix():
    # steam has no source comment; the repo comes from its _self_build_repo var.
    assert repos.source_urls(_lines('matrix-bridge-steam')) == [
        'https://github.com/jasonlaguidice/matrix-steam-bridge'
    ]


def test_see_comment_is_not_a_source():
    # "# See:" is documentation, not a source URL, and must yield nothing.
    assert repos.source_urls(_lines('matrix-static-files')) == []


def test_validate_url():
    assert repos.validate_url('https://github.com/a/b')
    assert not repos.validate_url('')
    assert not repos.validate_url('not-a-url')


def test_hostname_lowercased():
    assert repos.hostname('https://GitHub.com/a/b') == 'github.com'
    assert repos.hostname('garbage') == ''


def test_normalize_repo_url():
    assert repos.normalize_repo_url('https://github.com/a/b.git') == 'https://github.com/a/b'
    assert repos.normalize_repo_url('https://github.com/a/b/') == 'https://github.com/a/b'
