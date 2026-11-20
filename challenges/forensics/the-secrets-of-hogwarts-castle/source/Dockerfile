FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt

COPY app.py ./
COPY templates ./templates
COPY static ./static

RUN chown -R app:app /app
USER app

EXPOSE 10000

CMD ["sh", "-c", "exec python3 -m gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 4 --access-logfile - --error-logfile - app:app"]
