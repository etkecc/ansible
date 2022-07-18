* appservice_discord: v1.0.0
* appservice_irc: 0.34.0
* appservice_irc_docker_repo: '{{ ''master'' if matrix_appservice_irc_version == ''latest'' else matrix_appservice_irc_version }}'
* appservice_slack: 1.11.0
* appservice_slack_docker_repo: '{{ ''master'' if matrix_appservice_slack_version == ''latest'' else matrix_appservice_slack_version }}'
* appservice_webhooks_container_image_self_build_repo: '{{ ''master'' if matrix_appservice_webhooks_version == ''latest'' else matrix_appservice_webhooks_version }}'
* appservice_webhooks: v1.0.3-01
* backup_borg: ""
* backup_borg_docker_repo: main
* beeper_linkedin: v0.5.2
* buscarron_docker_repo: '{{ matrix_bot_buscarron_version }}'
* buscarron: v1.2.0
* cinny: v2.0.4
* corporal: 2.3.0
* coturn: 4.5.2-r12
* coturn_container_image_self_build_repo: docker/{{ matrix_coturn_version }}
* dimension: latest
* dnsmasq: latest
* dynamic_dns: v3.9.1-ls92
* element_themes_repository: master
* element: v1.11.0
* email2matrix: 1.0.3
* etherpad: 1.8.18
* facebook: v0.4.0
* go_neb: latest
* googlechat_container_image_self_build_repo: '{{ ''master'' if matrix_mautrix_googlechat_version == ''latest'' else matrix_mautrix_googlechat_version }}'
* googlechat: v0.3.3
* go_skype_bridge: latest
* grafana: 9.0.3
* hangouts_container_image_self_build_repo: '{{ ''master'' if matrix_mautrix_hangouts_version == ''latest'' else matrix_mautrix_googlechat_version }}'
* hangouts: latest
* heisenbridge: 1.13.0
* honoroit_docker_repo: '{{ matrix_bot_honoroit_version }}'
* honoroit: v0.9.9
* hookshot: 1.8.0
* hydrogen: v0.2.33
* instagram_container_image_self_build_repo: '{{ ''master'' if matrix_mautrix_instagram_version == ''latest'' else matrix_mautrix_instagram_version }}'
* instagram: v0.1.3
* jitsi_ldap: "3"
* jitsi: stable-7439-2
* kuma: 1.17.1-alpine
* languagetool: 5.8
* ma1sd: 2.5.0
* mailer: 4.95-r0-4
* matrix_registration_bot_docker_repo: '{{ matrix_bot_matrix_registration_bot_version if matrix_bot_matrix_registration_bot_version != ''latest'' else ''main'' }}'
* matrix_registration_bot: latest
* matrix_reminder_bot_docker_repo: '{{ matrix_bot_matrix_reminder_bot_version }}'
* matrix_reminder_bot: release-v0.2.1
* miniflux: 2.0.37
* miounne: v2.2.1
* mjolnir: v1.5.0
* mx_puppet_discord_container_image_self_build: '{{ ''main'' if matrix_mx_puppet_discord_version == ''latest'' else matrix_mx_puppet_discord_version }}'
* mx_puppet_discord: v0.1.1
* mx_puppet_groupme_container_image_self_build_repo: '{{ ''main'' if matrix_mx_puppet_groupme_version == ''latest'' else matrix_mx_puppet_groupme_version }}'
* mx_puppet_groupme: latest
* mx_puppet_instagram_container_image_self_build_repo: '{{ ''master'' if matrix_mx_puppet_instagram_version == ''latest'' else matrix_mx_puppet_instagram_version }}'
* mx_puppet_instagram: latest
* mx_puppet_slack_container_image_self_build: '{{ ''main'' if matrix_mx_puppet_slack_version == ''latest'' else matrix_mx_puppet_slack_version }}'
* mx_puppet_slack: v0.1.2
* mx_puppet_steam_container_image_self_build_repo: '{{ ''master'' if matrix_mx_puppet_steam_version == ''latest'' else matrix_mx_puppet_steam_version }}'
* mx_puppet_steam: latest
* mx_puppet_twitter: latest
* nginx_proxy: 1.23.0-alpine
* ntfy: v1.27.2
* prometheus_blackbox_exporter: v0.21.1
* prometheus_node_exporter: v1.3.1
* prometheus_postgres_exporter: v0.10.1
* prometheus: v2.37.0
* radicale: 3.1.7.0
* redis: 7.0.3-alpine
* registration: v0.7.2
* room_purger: latest
* scheduler: latest
* signal_daemon: 0.20.0
* signal_daemon_docker_repo: '{{ ''master'' if matrix_mautrix_signal_daemon_version == ''latest'' else matrix_mautrix_signal_daemon_version }}'
* signal_docker_repo: '{{ ''master'' if matrix_mautrix_signal_version == ''latest'' else matrix_mautrix_signal_version }}'
* signal: v0.3.0
* sms_bridge: 0.5.7
* softserve: v0.3.2
* sygnal: v0.12.0
* synapse_admin: 0.8.5
* synapse: v1.62.0
* telegram_docker_repo: '{{ ''master'' if matrix_mautrix_telegram_version == ''latest'' else matrix_mautrix_telegram_version }}'
* telegram_lottieconverter_docker_repo: master
* telegram: v0.11.3
* twitter_container_image_self_build_repo: '{{ ''master'' if matrix_mautrix_twitter_version == ''latest'' else matrix_mautrix_twitter_version }}'
* twitter: v0.1.4
* whatsapp: v0.6.0
