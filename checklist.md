# etke.cc | New customer checklist

## Setup

* Add base domain and contact details into `inventory/data.md`
* _customer's own server_: Add connection details into the `[setup]` section of the `inventory/hosts`
* _etke.cc hosting_: Add connection details into the `[turnkey]` section of the `inventory/hosts`
* Add base domain dir into the `inventory/host_vars`
* Add `vars.yml` into the `inventory/host_vars/DOMAIN/`
* Add `onboarding.md` into the `inventory/host_vars/DOMAIN/`

## After setup

* Invite fresh admin user into the `etke.cc` space and `etke.cc | announcements` room
* Add `DOMAIN | delegation` / `https://DOMAIN/.well-known/matrix/server` into monitoring (interval: 300, retries: 2, redirects: 1)
* Add `DOMAIN | federation` / `https://matrix.DOMAIN:8448/_matrix/federation/v1/version` into monitoring (interval: 300, retries: 2, redirects: 0)
* Add `DOMAIN | homeserver` / `https://matrix.DOMAIN/_matrix/client/versions` into monitoring (interval: 300, retries: 2, redirects: 0)
* Add new status page group `DOMAIN` and include all related monitors in it
* Send the onboarding list to the customer
* Increment client counter on website
* Remove original order message
* Remove onboarding list from `inventory/host_vars/DOMAIN/`

## After maintenance confirmation

### If customer declined the maintenance service

* Remove connection details from `inventory/hosts`
* Remove base domain dir and all files inside it from `inventory/host_vars`
* Remove `DOMAIN | delegation`, `DOMAIN | federation`, `DOMAIN | homeserver` from monitoring
* Remove `DOMAIN` group from status page
* Remove contact details from the `inventory/data.md`
* Move base domain to `Done` section of `inventory/data.md`

### If customer subscribed to the maintenance service

* Move connection details from the `[setup]` to the `[subscription]` section of `inventory/hosts`
* Move base domain and contact details to `Subscription` section of `inventory/data.md`
