FROM registry.gitlab.com/etke.cc/base as emmbuilder

RUN git clone https://gitlab.com/etke.cc/emm.git && \
		cd emm && \
		make build

FROM registry.gitlab.com/etke.cc/ansible/base

WORKDIR /playbook

ENTRYPOINT ["/bin/sh"]

RUN apk add --no-cache ca-certificates openssh git hugo openring make

COPY --from=emmbuilder /go/emm/emm /bin
COPY . /playbook

RUN git submodule update --init --recursive
