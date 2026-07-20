"""Turn ansible variable and role-directory names into the display names
the version tooling agrees on. The whole reason this module exists: two
scripts used to each grow their own name-derivation and quietly disagree,
and when they disagreed a version link vanished with no error. One function,
one answer, no drift.
"""

# Vars that end in _version but aren't a component release we track.
IGNORED = [
    'matrix_synapse_default_room_version',
    'matrix_playbook_migration_validated_version',
    'matrix_playbook_migration_expected_version',
]

# Stripped off variable names in this exact order, one pass each. Order is
# load-bearing: matrix_ must go before bridge_, or matrix_bridge_steam_version
# never sheds its bridge_ and you get "Bridge Steam" instead of "Steam" (#5813).
PREFIXES = [
    'matrix_',
    'bridge_',
    'custom_',
    'int_',
    'synapse_default_',
    'synapse_ext_',
    'mailer_container_',
    'bot_',
    'client_',
    'mautrix_',
    'devture_',
    'beeper_',
    'backup_borg_',
]

SUFFIXES = [
    '_version',
]

# Stripped off role-DIRECTORY names for the OPML feed slugs. Deliberately does
# NOT include 'mautrix-': releases.opml keys those bridges as "mautrix-signal",
# not "signal", and that spelling is the committed contract. Same idea as
# PREFIXES, different alphabet (dirs use dashes), different answer on purpose.
ROLE_DIR_PREFIXES = [
    'matrix-bot-',
    'matrix-bridge-',
    'matrix-client-',
    'matrix-',
]


# .title() flattens these into "Tcp"/"Jwt"/"Ldap" like they're ordinary words;
# hand them their capitals back. Add one when a new component turns up shouting
# its acronym in lowercase.
ACRONYMS = {
    'api', 'dns', 'http', 'https', 'imap', 'jwt', 'ldap', 'oidc',
    's3', 'sms', 'smtp', 'sso', 'ssl', 'tcp', 'url', 'xmpp',
}

# The real name .title() can't reach: a casing it won't guess (whatsapp ->
# WhatsApp) or a short expansion of a mashed-together token (gmessages -> Google
# Messages). Kept tight; add one only when a live component wears the name, not
# as a catalogue of every product with a capital in the middle.
BRANDS = {
    'whatsapp': 'WhatsApp',
    'linkedin': 'LinkedIn',
    'gmessages': 'Google Messages',
    'gvoice': 'Google Voice',
    'googlechat': 'Google Chat',
}

# Tails that ride in from a var's _git / _repo / _container_image suffix and
# describe the packaging, not the thing: "Synapse HTTP Antispam Git" is a spam
# checker, not a git. Lop them off the end.
NOISE_TAIL = ['Container Image', 'Git', 'Repo']

# The handful of names the derivation mangles past saving: keyed on the raw
# derived name (what you'd see in VERSIONS.md before this map), full override.
# This is the escape hatch for the irreducibly-weird, not the default path.
ALIASES = {
    'Synapse Rust Synapse Compress State Container Image': 'Synapse Compress State',
    'Traefik Config Tcp Servertransports Default Proxyprotocol': 'Traefik Proxy Protocol',
    'Jitsi Prosody Auth Matrix User Verification Repo': 'Jitsi User Verification',
}


def component_name(var):
    """The display name a *_version variable gets in VERSIONS.md, e.g.
    matrix_bridge_steam_version -> "Steam Bridge", matrix_synapse_version ->
    "Synapse". versions.py and versions.diff.py both call this, so a component's
    VERSIONS.md line and its changelog link are spelled by the same hand: that
    agreement, not any particular spelling, is what keeps links from vanishing.
    Change the output and you MUST regenerate VERSIONS.md in the same breath, or
    the next diff reads every renamed component as removed-then-added.
    """
    name = _derive(var)
    if name in ALIASES:
        return ALIASES[name]
    name = _prettify(name)
    # A bridge should say what it is: Steam -> Steam Bridge, Signal -> Signal
    # Bridge. Leave the ones already ending in "bridge" alone, or Heisenbridge
    # turns into "Heisenbridge Bridge" and the changelog stutters.
    if var.startswith('matrix_bridge_') and not name.lower().endswith('bridge'):
        name += ' Bridge'
    return name


def _derive(var):
    """Peel the ansible clutter off a var down to the bare component. The
    prefixes come off in order and it matters (PREFIXES tells that story), the
    _version tail goes, underscores become spaces, Title Case on top. Out walks
    "Steam", or "Bridge Steam" if you fumbled the prefix order.
    """
    for prefix in PREFIXES:
        var = var.removeprefix(prefix)
    for suffix in SUFFIXES:
        var = var.removesuffix(suffix)
    return var.replace('_', ' ').title()


def _prettify(name):
    """Tidy a derived name the algorithm CAN fix on its own: drop a trailing
    noise word, then hand every acronym back its capital letters. Anything too
    far gone for this lives in ALIASES instead.
    """
    for tail in NOISE_TAIL:
        if name != tail and name.endswith(' ' + tail):
            name = name[:-len(tail)].rstrip()
    out = []
    for token in name.split(' '):
        low = token.lower()
        if low in BRANDS:
            out.append(BRANDS[low])
        elif low in ACRONYMS:
            out.append(token.upper())
        else:
            out.append(token)
    return ' '.join(out)


def role_slug(dir_name):
    """The OPML feed slug for a role directory, e.g.
    matrix-bridge-signal -> "signal", matrix-bridge-mautrix-signal ->
    "mautrix-signal". Lowercase, dashes intact; the caller adds the -2 suffix
    when a role points at more than one repo.

    This is for feed slugs ONLY. Do not reach for it to match components in
    VERSIONS.md: those are keyed by component_name (Title Case, mautrix_
    stripped), and role_slug's dash form will never match them. Keying the
    weekly diff off this instead of component_name is precisely the drift bug
    this module was written to end.
    """
    for prefix in ROLE_DIR_PREFIXES:
        dir_name = dir_name.removeprefix(prefix)
    return dir_name
