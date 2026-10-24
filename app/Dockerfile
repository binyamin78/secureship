# ---- build stage: install dependencies into an isolated venv ----
FROM python:3.13-slim AS build
WORKDIR /build
RUN python -m venv /venv
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt \
 # pip/setuptools are only needed to install - drop them so they can't carry CVEs
 && /venv/bin/pip uninstall -y pip setuptools

# ---- runtime stage: minimal image, no build tools, non-root ----
FROM python:3.13-slim
ARG APP_VERSION=dev
ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}
RUN rm -rf /usr/local/lib/python3.13/site-packages/pip* \
           /usr/local/lib/python3.13/site-packages/setuptools* \
           /usr/local/bin/pip* \
 && groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /venv /venv
WORKDIR /app
COPY --chown=root:root devboard ./devboard
COPY --chown=root:root wsgi.py .
USER 10001
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--worker-tmp-dir", "/tmp", "--access-logfile", "-", "wsgi:app"]
