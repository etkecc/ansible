FROM registry.gitlab.com/etke.cc/base as emmbuilder

RUN git clone https://gitlab.com/etke.cc/emm.git && \
		cd emm && \
		make build

FROM alpine:edge

WORKDIR /playbook

ENTRYPOINT ["/bin/sh"]

RUN apk add --no-cache ca-certificates openssh git ansible py3-dnspython hugo openring make

COPY --from=emmbuilder /go/emm/emm /bin
COPY . /playbook

RUN git submodule update --init --recursive
