FROM registry.gitlab.com/etke.cc/base/build AS builder
RUN git clone --depth 1 https://gitlab.com/etke.cc/int/agru.git && \
    cd agru && just build && mv agru /bin/agru && cd .. && rm -rf agru

FROM registry.gitlab.com/etke.cc/ansible/base AS playbook
WORKDIR /playbook
COPY . /playbook
COPY --from=builder /bin/agru /bin/agru
# Note the current commit hash into a file, if we ever need it.
# Then initialize /upstream from submodules, and get rid of the `.git` directory.
# We don't need to carry that extra weight into the final image.
RUN apk --no-cache add git just && \
    git rev-parse HEAD > /playbook/source-commit && \
    ANSIBLE_LOG_PATH=" " just dependencies && \
    rm -rf /playbook/.git && \
    rm -rf /playbook/upstream/.git


FROM registry.gitlab.com/etke.cc/ansible/base
WORKDIR /playbook
ENTRYPOINT ["/bin/sh"]
COPY --from=playbook /playbook /playbook
