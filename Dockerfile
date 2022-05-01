FROM registry.gitlab.com/etke.cc/base

WORKDIR /playbook

ENTRYPOINT ["/bin/sh"]

RUN apk add --no-cache ca-certificates openssh git ansible py3-dnspython

COPY . /playbook

RUN git submodule update --init --recursive
