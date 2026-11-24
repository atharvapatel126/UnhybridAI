# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.13.14-slim@sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6
FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/state LOGS_DIR=/app/logs MODEL_CACHE=/app/model-cache \
    HF_HOME=/app/model-cache HF_HUB_DISABLE_TELEMETRY=1 ANONYMIZED_TELEMETRY=False
WORKDIR /app
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app \
    && mkdir -p /app/state /app/logs /app/model-cache \
    && chown -R app:app /app
COPY requirements.txt ./
# CPU wheels avoid downloading CUDA libraries for this local demo.
RUN python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 \
    && python -m pip install -r requirements.txt

FROM base AS test
COPY requirements-dev.txt ./
RUN python -m pip install -r requirements-dev.txt
COPY --chown=app:app . .
USER app
CMD ["python", "-m", "pytest", "-q"]

FROM base AS runtime
COPY --chown=app:app config.py ./
COPY --chown=app:app src ./src
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app data/raw_docs ./data/raw_docs
COPY --chown=app:app app.py ./
COPY --chown=app:app .streamlit ./.streamlit
COPY --chown=app:app tests/eval_set.json ./evaluation/eval_set.json
USER app
EXPOSE 8501
HEALTHCHECK --interval=15s --timeout=3s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=2)"
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
