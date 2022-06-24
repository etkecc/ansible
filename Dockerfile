FROM registry.gitlab.com/etke.cc/base as tools

FROM registry.gitlab.com/etke.cc/ansible/base

WORKDIR /playbook

ENTRYPOINT ["/bin/sh"]

RUN apk add --no-cache ca-certificates openssh git hugo make

COPY --from=tools /bin/emm /bin/emm
COPY . /playbook

RUN git submodule update --init --recursive
