FROM alpine as kubectl-builder
WORKDIR /
RUN apk add curl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod a+rx /kubectl


FROM alpine as skopeo-builder
WORKDIR /
RUN apk add git make go bash libc-dev linux-headers
ENV GOPATH=/go
RUN git clone https://github.com/containers/skopeo $GOPATH/src/github.com/containers/skopeo
WORKDIR $GOPATH/src/github.com/containers/skopeo
RUN make binary-local DISABLE_CGO=1
RUN mv ./skopeo /skopeo


FROM alpine
RUN apk add --no-cache ca-certificates jq python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
RUN pip install kubepy
COPY --from=kubectl-builder /kubectl /usr/bin/kubectl
COPY --from=skopeo-builder /skopeo /usr/bin/skopeo
WORKDIR /root/
CMD ["ash"]
