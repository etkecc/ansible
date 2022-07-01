FROM registry.gitlab.com/etke.cc/base as tools


FROM registry.gitlab.com/etke.cc/ansible/base AS playbook_build
WORKDIR /playbook
COPY . /playbook
# Note the current commit hash into a file, if we ever need it.
# Then initialize /upstream from submodules, and get rid of the `.git` directory.
# We don't need to carry that extra weight into the final image.
RUN git rev-parse HEAD > /playbook/source-commit && \
    ANSIBLE_LOG_PATH=" " make pull-dependencies && \
    rm -rf /playbook/.git


FROM registry.gitlab.com/etke.cc/ansible/base
WORKDIR /playbook
ENTRYPOINT ["/bin/sh"]
RUN apk add --no-cache ca-certificates openssh git hugo make
COPY --from=playbook_build /playbook /playbook
COPY --from=tools /bin/emm /bin/emm
