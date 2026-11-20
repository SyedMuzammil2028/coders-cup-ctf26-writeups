FROM python:3.12.8-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libimage-exiftool-perl \
        steghide \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /run/challenge /opt/challenge \
    && chown app:app /run/challenge

COPY src/ /app/src/
COPY public/ /app/public/
COPY entrypoint.sh start.sh /app/
COPY assets/castle_original.jpg /opt/challenge/castle_original.jpg

RUN chmod 0555 /app/entrypoint.sh /app/start.sh /app/src/*.py \
    && chmod 0444 /opt/challenge/castle_original.jpg \
    && chown -R app:app /app

USER app
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/start.sh"]

