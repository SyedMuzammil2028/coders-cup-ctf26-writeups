FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup -S archive && adduser -S -G archive archive
COPY app.py generate.py ./
COPY static/ ./static/
USER archive

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "from urllib.request import urlopen; assert urlopen('http://127.0.0.1:8000/healthz', timeout=2).read() == b'ok\\n'"]
CMD ["python", "app.py"]
