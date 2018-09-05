FROM python:3-alpine as builder

WORKDIR /
RUN apk add curl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod a+rx /kubectl

FROM python:3-alpine

RUN apk --no-cache add docker
RUN pip install docker kubepy
COPY --from=builder /kubectl /usr/bin/kubectl
WORKDIR /root/
