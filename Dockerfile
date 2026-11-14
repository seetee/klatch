FROM python:3-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . /src
RUN pip install --no-cache-dir /src

# The folder holding docker-compose.yml is mounted here.
WORKDIR /work
ENTRYPOINT ["klatch"]
