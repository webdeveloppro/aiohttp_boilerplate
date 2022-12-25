FROM python:3.10-alpine3.17

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
RUN pip install -r --no-cache-dir requirements.txt

CMD ["sh"]
