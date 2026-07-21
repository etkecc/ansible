"""Building the two kinds of upstream URL from a repo: the release-tag page a
version points at (for the weekly diff) and the Atom feed to subscribe to (for
the OPML). Every forge spells these differently, so the per-host quirks live
here in one place instead of scattered across two scripts.
"""

from lib import repos

# host -> how its feed URL is shaped. Anything not listed has no feed we know.
HOST_FEED_RULES = {
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

# host -> feed template that overrides the rule default (a forge configured
# oddly). {repo} is the normalized base URL.
HOST_FEED_TEMPLATES = {
    'forgejo.ellis.link': '{repo}/atom/',
}

RULE_TEMPLATES = {
    'github': '{repo}/releases.atom',
    'gitlab': '{repo}/-/tags?format=atom',
    'cgit': '{repo}/atom/',
    'gitea': '{repo}.atom',
    'forgejo': '{repo}/releases.atom',
}

GITLAB_RELEASE_HOSTS = ('gitlab.com', 'mau.dev', 'dev.funkwhale.audio')


def _release_host_kind(repo):
    """'github', 'gitlab', or '' for repo's host. Hostname match, not substring,
    so a path like .../?x=github can't walk an SSRF into versions.diff's fetch.
    """
    host = repos.hostname(repo)
    if host == 'github.com' or host.endswith('.github.com'):
        return 'github'
    if host in GITLAB_RELEASE_HOSTS:
        return 'gitlab'
    return ''


def release_url_candidates(repo, version):
    """The tag URLs worth trying for one release, best guess first. Upstreams
    can't agree whether a tag wears a 'v' (the *_version vars drop it, half the
    repos keep it), so instead of a hand-kept list of who-prepends-v we hand the
    caller both spellings and let it probe which one actually exists. Empty list
    for a forge we can't address at all. Pure: builds strings, touches nothing.
    """
    kind = _release_host_kind(repo)
    if not kind:
        return []
    custom = _custom_release_url(repo, version)
    if custom:
        return [custom]
    if kind == 'github':
        base = f"{repo}/releases/tag/"
    else:
        base = f"{repo}/-/tags/"
    return list(dict.fromkeys([base + version, base + _toggle_v(version)]))


def release_url(repo, version):
    """The single best-guess tag URL, no probing. release_url_candidates is the
    real entry point now; this is the "I'll take the first guess" shortcut for
    callers that can't reach the network.
    """
    candidates = release_url_candidates(repo, version)
    return candidates[0] if candidates else None


def _toggle_v(version):
    """Flip the leading v: 1.2.3 <-> v1.2.3. The other spelling to try when the
    first tag URL turns up nothing.
    """
    return version[1:] if version.startswith('v') else 'v' + version


def _custom_release_url(repo, version):
    """The two forges that tag their own weird way: nginx ships release-1.2.3,
    coturn buries its tag behind docker%2F. Returns None when neither applies so
    the caller falls through to the ordinary github/gitlab tag URLs.
    """
    if 'github.com/nginx/nginx' in repo:
        version = version.split('-')[0]
        return f"{repo}/releases/tag/release-{version}"
    if 'github.com/coturn/coturn' in repo:
        return f"{repo}/releases/tag/docker%2F{version}"
    return None


def feed_rule_for_host(host):
    """Which feed shape a host uses, or '' if we don't syndicate it. Any
    *.github.com subdomain counts as github.
    """
    if not host:
        return ''
    if host in HOST_FEED_RULES:
        return HOST_FEED_RULES[host]
    if host.endswith('.github.com'):
        return 'github'
    return ''


def feed_url(repo):
    """The Atom feed URL for a repo, or '' if it hasn't got a subscribable one.
    Radicle genuinely has no feed; an unknown host is the other empty case, and
    the caller tells the two apart with feed_rule_for_host if it cares.
    """
    host = repos.hostname(repo)
    rule = feed_rule_for_host(host)
    if not rule or rule == 'radicle':
        return ''
    template = HOST_FEED_TEMPLATES.get(host) or RULE_TEMPLATES.get(rule, '')
    if not template:
        return ''
    return template.format(repo=repos.normalize_repo_url(repo))
