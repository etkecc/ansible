FROM registry.gitlab.com/etke.cc/ansible/base AS playbook
ENV AGRU_CLEANUP="-c=false"
ENV ANSIBLE_LOG_PATH=" "
WORKDIR /playbook
COPY . /playbook
RUN apk --no-cache add hugo
# Note the current commit hash into a file, if we ever need it.
# Then initialize /upstream from submodules, and get rid of the `.git` directory.
# We don't need to carry that extra weight into the final image.
RUN git rev-parse HEAD > /playbook/source-commit && \
    just dependencies && \
    rm -rf /playbook/.git && \
    rm -rf /playbook/upstream/.git


FROM registry.gitlab.com/etke.cc/ansible/base
WORKDIR /playbook
ENTRYPOINT ["/bin/sh"]
COPY --from=playbook /playbook /playbook
