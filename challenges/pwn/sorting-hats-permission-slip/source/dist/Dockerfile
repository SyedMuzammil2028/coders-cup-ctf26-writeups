FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends socat \
    && useradd --create-home --shell /usr/sbin/nologin ctf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/ctf/challenge
COPY dist/sorting_hat ./sorting_hat
COPY dist/sorting_hat.c ./sorting_hat.c
COPY dist/flag.txt ./flag.txt
RUN chown -R root:ctf /home/ctf/challenge && chmod 0755 ./sorting_hat && chmod 0440 ./flag.txt

USER ctf
EXPOSE 1337
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./sorting_hat,stderr"]
