import os

from conftest import FIXTURES, load_script

from lib import roles

diff = load_script('versions.diff.py')


def _repo_map(subtree):
    files = roles.role_default_files(os.path.join(FIXTURES, subtree))
    return diff.build_repo_map(files)


def test_steam_and_signal_recover_their_links():
    repo_map = _repo_map('roles')
    # steam: recovered from its self_build repo, the whole reason for the rewrite.
    assert repo_map['Steam Bridge'] == 'https://github.com/jasonlaguidice/matrix-steam-bridge'
    # signal: the Project-comment case, keyed by the var-derived name.
    assert repo_map['Signal Bridge'] == 'https://github.com/mautrix/signal'


def test_multi_var_role_links_every_var():
    repo_map = _repo_map('roles')
    assert repo_map['Multi Server'] == 'https://github.com/example/multi'
    assert repo_map['Multi Client'] == 'https://github.com/example/multi'


def test_sourceless_role_gets_no_entry():
    repo_map = _repo_map('roles')
    assert 'Static Files' not in repo_map


def test_repo_map_covers_exactly_the_sourced_components():
    # Every role with a source, nothing without one (Static Files has no repo).
    repo_map = _repo_map('roles')
    assert set(repo_map) == {'Steam Bridge', 'Signal Bridge', 'Multi Server', 'Multi Client', 'Gitlabby'}


def test_collision_takes_the_role_listed_last_in_the_play():
    # two roles bridging one service; whoever sits lower in play/all.yml owns the link.
    subtree = os.path.join(FIXTURES, 'collision', 'roles')

    def repo_map(active):
        return diff.build_repo_map(roles.role_default_files(subtree, active=active))

    later = repo_map(['matrix-bridge-collide', 'matrix-collide-a'])
    assert later['Collide'] == 'https://github.com/example/collide-a'

    flipped = repo_map(['matrix-collide-a', 'matrix-bridge-collide'])
    assert flipped['Collide'] == 'https://github.com/example/collide-b'


def test_pick_release_url_first_reachable_wins():
    # the v-spelling that answers 200 is the one we link.
    picked = diff._pick_release_url(['no-v', 'v'], probe=lambda u: 200 if u == 'v' else 404)
    assert picked == ('v', 'ok')


def test_pick_release_url_all_404_is_broken():
    assert diff._pick_release_url(['a', 'b'], probe=lambda u: 404) == (None, 'broken')


def test_pick_release_url_network_blip_is_unverified():
    # forge unreachable (None): keep the first guess, flag it, don't cry broken.
    assert diff._pick_release_url(['a', 'b'], probe=lambda u: None) == ('a', 'unverified')


def test_pick_release_url_rate_limit_is_not_broken():
    # a 429 on a busy week must NOT condemn every link (the bleeding regression).
    assert diff._pick_release_url(['a', 'b'], probe=lambda u: 429) == ('a', 'unverified')


def test_pick_release_url_dead_first_keeps_the_uncertain_one():
    # cand a is a real 404, cand b a timeout: link b, never the proven-dead a.
    assert diff._pick_release_url(['a', 'b'], probe=lambda u: 404 if u == 'a' else None) == ('b', 'unverified')


def test_pick_release_url_no_candidates_is_broken():
    assert diff._pick_release_url([], probe=lambda u: 200) == (None, 'broken')
