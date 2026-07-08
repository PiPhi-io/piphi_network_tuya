FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PIPHI_RUNTIME_PORT=4191

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir . \
    && adduser --disabled-password --gecos "" --uid 10001 piphi \
    && chown -R piphi:piphi /app

USER piphi

EXPOSE 4191

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, sys, urllib.request; port = os.getenv('PIPHI_RUNTIME_PORT', '4191'); urllib.request.urlopen('http://127.0.0.1:' + port + '/health', timeout=3); sys.exit(0)"

CMD ["python", "-m", "piphi_network_tuya.main"]
