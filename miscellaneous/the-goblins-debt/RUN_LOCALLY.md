# Run locally — The Goblin’s Debt

Start with `CHALLENGE.md`, then try the challenge before reading `WRITEUP.md`.

## Build the local service

A Dockerfile is available in `source`. Build it there with:

```sh
docker build -t challenge-local .
```

Run the resulting image with a local port mapping. Where needed, provide `FLAG=ACM{local_demo_flag}`.
