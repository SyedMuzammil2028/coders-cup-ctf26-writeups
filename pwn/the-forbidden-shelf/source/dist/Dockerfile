FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends socat \
    && useradd --create-home --shell /usr/sbin/nologin ctf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/ctf/challenge
COPY dist/forbidden_shelf ./forbidden_shelf
COPY dist/forbidden_shelf.c ./forbidden_shelf.c
COPY dist/flag.txt ./flag.txt
RUN chown -R root:ctf /home/ctf/challenge && chmod 0755 ./forbidden_shelf && chmod 0440 ./flag.txt

USER ctf
EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./forbidden_shelf,stderr"]
