ARG ALPINE
ARG ANSIBLE
ARG ANSIBLE_CORE
FROM registry.gitlab.com/etke.cc/ansible/base:${ALPINE}-${ANSIBLE_CORE}-${ANSIBLE}

ENV AGRU_CLEANUP="-c=false"
ENV ANSIBLE_LOG_PATH=" "
WORKDIR /playbook
ENTRYPOINT ["/bin/sh"]
COPY . /playbook
# Note the current commit hash into a file, if we ever need it.
# Then initialize /upstream from submodules, and get rid of the `.git` directory.
# We don't need to carry that extra weight into the final image.
RUN git rev-parse HEAD > /playbook/source-commit && \
    just dependencies && \
    rm -rf /playbook/.git && \
    rm -rf /playbook/upstream/.git
