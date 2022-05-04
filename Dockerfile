FROM alpine:edge

WORKDIR /playbook

ENTRYPOINT ["/bin/sh"]

RUN apk add --no-cache ca-certificates openssh git ansible py3-dnspython hugo openring make

COPY . /playbook

RUN git submodule update --init --recursive
