FROM fedora:latest

RUN dnf install -y ansible-core python3-passlib python3-resolvelib \
    ansible-collection-community-general ansible-collection-community-docker \
    ansible-collection-ansible-posix ansible-collection-ansible-utils \
    git openssh-clients \
    && dnf clean all

WORKDIR /playbook
COPY . /playbook

RUN git rev-parse HEAD > /playbook/source-commit && \
    git submodule update --init --recursive && \
    rm -rf /playbook/.git && \
    rm -rf /playbook/upstream/.git

ENTRYPOINT ["/bin/sh"]
