<!--
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2020-2024 MDAD project contributors
SPDX-FileCopyrightText: 2020-2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Nikita Chernyi
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 Tiz
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Prometheus

This is an [Ansible](https://www.ansible.com/) role which installs [Prometheus](https://prometheus.io/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Prometheus is a metrics collection and alerting monitoring solution.

See the project's [documentation](https://prometheus.io/docs/introduction/overview/) to learn what Prometheus does and why it might be useful to you.

## Adjusting the playbook configuration

To enable Prometheus with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# prometheus                                                           #
#                                                                      #
########################################################################

prometheus_enabled: true

########################################################################
#                                                                      #
# /prometheus                                                          #
#                                                                      #
########################################################################
```

### Integrating with Prometheus Node Exporter

>[!NOTE]
> The configuration below presupposes that Prometheus Node Exporter is set up with the [ansible-role-prometheus-node-exporter](https://github.com/mother-of-all-self-hosting/ansible-role-prometheus-node-exporter) Ansible role on the MASH Ansible playbook. Adapt to your needs if it is set up otherwise.

If you've installed [Prometheus Node Exporter](https://github.com/prometheus/node_exporter) on the same host, you can make Prometheus scrape its metrics by adding the following configuration to your `vars.yml` file:

```yaml
prometheus_self_node_scraper_enabled: true
prometheus_self_node_scraper_static_configs_target: "{{ prometheus_node_exporter_identifier }}:9100"
```

>[!NOTE]
> To scrape a *remote* Prometheus Node Exporter instance, add the configuration to `prometheus_config_scrape_configs_additional` described below.

### Scraping other exporter services

To make Prometheus useful, you'll need to get it scrape one or more hosts by adjusting the configuration. You can add your own scrape configuration to `prometheus_config_scrape_configs_additional` as below (adapt to your needs):

```yaml
prometheus_config_scrape_configs_additional:
  - job_name: some_job
    metrics_path: /metrics
    scrape_interval: 120s
    scrape_timeout: 120s
    static_configs:
      - targets:
          - some-host:8080

  - job_name: another_job
    metrics_path: /metrics
    scrape_interval: 120s
    scrape_timeout: 120s
    static_configs:
      - targets:
          - another-host:8080
```

### Disabling scraping from own process

By default, Prometheus is configured to scrape (collect metrics from) its own process. You can disable this behavior by adding the following configuration to your `vars.yml` file:

```yaml
prometheus_self_process_scraper_enabled: false
```

### Exposing the web interface (optional)

To expose the Prometheus web interface publicly, add the following configuration to your `vars.yml` file (adapt to your needs).

```yaml
prometheus_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

When exposing it, you should consider to set up [HTTP Basic Authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication) **or anyone would be able to read your metrics**. To enable the HTTP Basic authentication, add the following configuration to your `vars.yml` file:

```yaml
prometheus_container_labels_metrics_middleware_basic_auth_enabled: true

# See https://doc.traefik.io/traefik/middlewares/http/basicauth/#users for details.
prometheus_container_labels_metrics_middleware_basic_auth_users: ""
```

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `prometheus_environment_variables_additional_variables` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Prometheus becomes available.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu prometheus` (or how you/your playbook named the service, e.g. `mash-prometheus`).
