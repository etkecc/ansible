from lib import naming


def test_component_name_golden():
    assert naming.component_name('matrix_synapse_version') == 'Synapse'
    assert naming.component_name('matrix_bot_honoroit_version') == 'Honoroit'
    assert naming.component_name('matrix_bridge_mautrix_signal_version') == 'Signal Bridge'
    assert naming.component_name('matrix_bridge_steam_version') == 'Steam Bridge'


def test_component_name_prefix_order_is_load_bearing():
    # matrix_ must strip before bridge_, or the bridge_ never comes off and you
    # get "Bridge Steam Bridge" instead of "Steam Bridge" (#5813).
    assert naming.component_name('matrix_bridge_steam_version') == 'Steam Bridge'


def test_bridges_get_a_bridge_suffix():
    assert naming.component_name('matrix_bridge_mautrix_whatsapp_version') == 'WhatsApp Bridge'
    assert naming.component_name('matrix_bridge_telegram_version') == 'Telegram Bridge'


def test_a_component_already_named_bridge_is_not_doubled():
    assert naming.component_name('matrix_bridge_heisenbridge_version') == 'Heisenbridge'


def test_brand_casing_and_expansion():
    assert naming.component_name('matrix_bridge_beeper_linkedin_version') == 'LinkedIn Bridge'
    assert naming.component_name('matrix_bridge_mautrix_gmessages_version') == 'Google Messages Bridge'
    assert naming.component_name('matrix_bridge_mautrix_gvoice_version') == 'Google Voice Bridge'
    assert naming.component_name('matrix_bridge_mautrix_googlechat_version') == 'Google Chat Bridge'


def test_non_bridge_gets_no_suffix():
    assert naming.component_name('matrix_synapse_version') == 'Synapse'
    assert naming.component_name('matrix_client_element_version') == 'Element'


def test_acronyms_get_their_capitals_back():
    assert naming.component_name('matrix_livekit_jwt_service_version') == 'Livekit JWT Service'
    assert naming.component_name('matrix_jitsi_ldap_version') == 'Jitsi LDAP'


def test_trailing_noise_word_is_dropped():
    assert naming.component_name('matrix_synapse_http_antispam_git_version') == 'Synapse HTTP Antispam'


def test_alias_overrides_a_mangled_name():
    assert naming.component_name(
        'matrix_jitsi_prosody_auth_matrix_user_verification_repo_version'
    ) == 'Jitsi User Verification'


def test_role_slug_keeps_mautrix():
    assert naming.role_slug('matrix-bridge-signal') == 'signal'
    assert naming.role_slug('matrix-bridge-mautrix-signal') == 'mautrix-signal'
    assert naming.role_slug('matrix-bot-honoroit') == 'honoroit'
    assert naming.role_slug('matrix-static-files') == 'static-files'


def test_two_vars_can_collide_to_one_name():
    # These two distinct vars both reduce to "Collide" (neither is a matrix_bridge_
    # var, so no suffix saves them). versions.diff.py turns that into a hard stop;
    # here we just prove the collision the assert guards against is real.
    assert naming.component_name('matrix_collide_version') == 'Collide'
    assert naming.component_name('bridge_collide_version') == 'Collide'
