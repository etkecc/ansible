import os

from conftest import FIXTURES

from lib import roles

ROLES = os.path.join(FIXTURES, 'roles')


def _names(files):
    return {roles.role_name_from_path(f) for f in files}


def test_walk_finds_every_role_by_default():
    assert _names(roles.role_default_files(ROLES)) == {
        'matrix-bridge-steam', 'matrix-static-files', 'matrix-bridge-signal',
        'matrix-multi', 'matrix-gitlabby',
    }


def test_active_filter_keeps_only_named_roles():
    files = roles.role_default_files(ROLES, active=['matrix-multi'])
    assert _names(files) == {'matrix-multi'}


def test_exclude_drops_a_subtree():
    # This is the guard that keeps bin/tests fixtures out of releases.opml.
    excluded = os.path.join(ROLES, 'matrix-bridge-steam')
    assert 'matrix-bridge-steam' not in _names(roles.role_default_files(ROLES, exclude=[excluded]))


def test_exclude_is_path_anchored_not_string_prefix():
    # "matrix-mult" is a string-prefix of the real "matrix-multi" dir. A raw
    # startswith would wrongly drop matrix-multi; a path-anchored one leaves it.
    near_miss = os.path.join(ROLES, 'matrix-mult')
    assert 'matrix-multi' in _names(roles.role_default_files(ROLES, exclude=[near_miss]))


def test_version_vars_skips_templated_and_ignored():
    steam = os.path.join(ROLES, 'matrix-bridge-steam', 'defaults', 'main.yml')
    vars_found = dict(roles.version_vars(steam))
    # the real pin is kept, the {{ ... }} self-build repo version is filtered out.
    assert vars_found == {'matrix_bridge_steam_version': '1.2.3'}
