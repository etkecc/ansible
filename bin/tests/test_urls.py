from lib import urls


def test_release_url_github():
    assert urls.release_url('https://github.com/mautrix/signal', '0.7.5') == \
        'https://github.com/mautrix/signal/releases/tag/0.7.5'


def test_release_url_gitlab():
    assert urls.release_url('https://gitlab.com/example/gitlabby', '3.1.4') == \
        'https://gitlab.com/example/gitlabby/-/tags/3.1.4'


def test_release_url_nginx_drops_suffix():
    assert urls.release_url('https://github.com/nginx/nginx', '1.27.0-1') == \
        'https://github.com/nginx/nginx/releases/tag/release-1.27.0'


def test_release_url_coturn_escapes_slash():
    assert urls.release_url('https://github.com/coturn/coturn', '4.6.2') == \
        'https://github.com/coturn/coturn/releases/tag/docker%2F4.6.2'


def test_candidates_offer_both_v_spellings():
    # No v: try the bare tag first, then the v form. The generator probes both.
    assert urls.release_url_candidates('https://github.com/grafana/grafana', '10.0.0') == [
        'https://github.com/grafana/grafana/releases/tag/10.0.0',
        'https://github.com/grafana/grafana/releases/tag/v10.0.0',
    ]
    # Already has v: try it first, then the stripped form.
    assert urls.release_url_candidates('https://github.com/grafana/grafana', 'v10.0.0') == [
        'https://github.com/grafana/grafana/releases/tag/v10.0.0',
        'https://github.com/grafana/grafana/releases/tag/10.0.0',
    ]


def test_candidates_gitlab_and_custom():
    assert urls.release_url_candidates('https://gitlab.com/x/y', '1.0')[0] == \
        'https://gitlab.com/x/y/-/tags/1.0'
    # nginx/coturn have one true form, no v-toggling.
    assert urls.release_url_candidates('https://github.com/coturn/coturn', '4.6.2') == [
        'https://github.com/coturn/coturn/releases/tag/docker%2F4.6.2'
    ]


def test_candidates_empty_for_unknown_forge():
    assert urls.release_url_candidates('https://app.radicle.xyz/z/thing', '1.0') == []
    assert urls.release_url('https://app.radicle.xyz/z/thing', '1.0') is None


def test_candidates_reject_host_spoofed_by_path():
    # 'github' in the path must not make a non-forge host look addressable, or
    # versions.diff.py fetches whatever host an upstream comment points at.
    assert urls.release_url_candidates('http://169.254.169.254/?x=github', '1.0') == []
    assert urls.release_url_candidates('http://evil.example/gitlab/x', '1.0') == []


def test_feed_url_by_host():
    assert urls.feed_url('https://github.com/mautrix/signal') == \
        'https://github.com/mautrix/signal/releases.atom'
    assert urls.feed_url('https://gitlab.com/example/gitlabby') == \
        'https://gitlab.com/example/gitlabby/-/tags?format=atom'
    assert urls.feed_url('https://codeberg.org/a/b') == 'https://codeberg.org/a/b/releases.atom'


def test_feed_url_host_template_override():
    assert urls.feed_url('https://forgejo.ellis.link/x/y') == 'https://forgejo.ellis.link/x/y/atom/'


def test_feed_url_radicle_and_unknown_are_empty():
    assert urls.feed_url('https://app.radicle.xyz/z') == ''
    assert urls.feed_url('https://example.com/nope') == ''


def test_feed_url_normalizes_git_suffix():
    assert urls.feed_url('https://github.com/a/b.git') == 'https://github.com/a/b/releases.atom'


def test_feed_rule_for_github_subdomain():
    assert urls.feed_rule_for_host('pages.github.com') == 'github'
    assert urls.feed_rule_for_host('') == ''
