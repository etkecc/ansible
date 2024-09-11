#!/bin/sh

# This script waits for certificate files for the given domain to become available.
#
# We only wait a fixed number of iterations and then give up,
# because waiting indefinitely provides a worse UX when used in a playbook which starts services.
# We want services to be able to depend on `devture-traefik-certs-dumper-wait-for-domain@DOMAIN.service` (After=..; Requires=..) and:
# - for these services to not get stuck infinitely waiting, if a certificate doesn't become available. We want them to fail relatively quickly
# - for these services to be stoppable (`systemctl start some-service && systemctl stop some-service`) without the waiter remaining to loop forever in the background
# - for waiters to never remain looping forever in the background, regardless of how else it may happen

domain=$1

/certs-dumper-bin/wait-for-file.sh {{ devture_traefik_certs_dumper_dumped_certificates_dir_path }}/$domain/certificate.crt {{ devture_traefik_certs_dumper_waiter_max_iterations }} \
&& \
/certs-dumper-bin/wait-for-file.sh {{ devture_traefik_certs_dumper_dumped_certificates_dir_path }}/$domain/privatekey.key {{ devture_traefik_certs_dumper_waiter_max_iterations }}
