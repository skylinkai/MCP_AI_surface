FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY packages/ packages/
COPY apps/ apps/
COPY config/ config/
COPY data/ data/

RUN pip install --no-cache-dir -e .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/entrypoint.sh"]
