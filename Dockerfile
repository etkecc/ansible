FROM registry.gitlab.com/etke.cc/base as tools


FROM registry.gitlab.com/etke.cc/ansible/base AS playbook
WORKDIR /playbook
COPY . /playbook
# Note the current commit hash into a file, if we ever need it.
# Then initialize /upstream from submodules, and get rid of the `.git` directory.
# We don't need to carry that extra weight into the final image.
RUN apk --no-cache add git && \
    git rev-parse HEAD > /playbook/source-commit && \
    ANSIBLE_LOG_PATH=" " make dependencies && \
    rm -rf /playbook/.git


FROM registry.gitlab.com/etke.cc/ansible/base
WORKDIR /playbook
ENTRYPOINT ["/bin/sh"]
RUN apk add --no-cache ca-certificates openssh git hugo make
COPY --from=playbook /playbook /playbook
COPY --from=tools /bin/emm /bin/emm
