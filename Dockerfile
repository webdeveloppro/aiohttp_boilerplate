FROM python:3.12-alpine3.19@sha256:ae1f508f01ac1806e84c68b43ee0983b586426dfa39f5d21eced0dd7f5e230f4 as build

RUN apk update && apk upgrade
RUN apk add --no-cache build-base \
    musl-dev \
    libffi-dev \
    python3-dev \
    openssl-dev \
    openssh-client \
    git \
    gcc \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /aiohttp_bolierplate.git
WORKDIR /aiohttp_bolierplate.git
COPY . /aiohttp_bolierplate.git
RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh"]
