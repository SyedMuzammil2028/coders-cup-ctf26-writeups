# Python 3.8 is deliberately selected because its bytecode has reliable support
# in common CTF decompilers such as uncompyle6 and decompyle3.
FROM python@sha256:e191a71397fd61fbddb6712cd43ef9a2c17df0b5e7ba67607128554cd6bff267

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN addgroup --system ctf && adduser --system --ingroup ctf --no-create-home ctf

COPY --chown=ctf:ctf src/ /app/src/
COPY --chown=ctf:ctf public/ /app/public/
COPY --chown=ctf:ctf entrypoint.sh /app/entrypoint.sh

RUN mkdir -p /app/generated \
    && chown ctf:ctf /app/generated \
    && chmod 0555 /app/entrypoint.sh

USER ctf

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]

