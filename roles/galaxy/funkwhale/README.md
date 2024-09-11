# Funkwhale Ansible Role

Funkwhale is a community-driven project that lets you listen and share music and audio within a decentralized, open network. This role helps you to set up Funkwhale:

- with everything run in [Docker](https://www.docker.com/) containers
- powered by [the official Funkwhale container images](https://hub.docker.com/r/funkwhale/)


## Installing

To configure and install Funkwhale on your own server(s), you should use a playbook like [Mother of all self-hosting](https://github.com/mother-of-all-self-hosting/mash-playbook) or write your own.

# Tuning

Have a look at `defaults/main.yml` for configuration options. If you want to boost the perfomance of your pod you might want to tune:
* `funkwhale_frontend_web_workers`: Number of web workers to start in parallel, increase to allow more parallel connections
* `funkwhale_celery_worker_concurrency`: Number of worker processes to execute that process background tasks. You might want to increase this if e.g. file imports are slow
