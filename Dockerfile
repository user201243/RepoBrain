# syntax=docker/dockerfile:1

FROM node:22-slim AS web-build

WORKDIR /app/webapp
COPY webapp/package.json webapp/package-lock.json ./
RUN npm ci
COPY webapp/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REPOBRAIN_REPO=/workspace \
    REPOBRAIN_WEB_HOST=0.0.0.0 \
    REPOBRAIN_WEB_PORT=8765

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY --from=web-build /app/webapp/dist ./webapp/dist
COPY docker/entrypoint.sh /usr/local/bin/repobrain-docker

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir ".[providers,tree-sitter,mcp]" \
    && chmod +x /usr/local/bin/repobrain-docker

VOLUME ["/workspace"]
EXPOSE 8765

ENTRYPOINT ["repobrain-docker"]
CMD ["web"]
