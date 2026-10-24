"""Prometheus instrumentation for every request."""
import time

from flask import Flask, Response, g, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUESTS = Counter(
    "devboard_http_requests_total", "HTTP requests", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "devboard_http_request_duration_seconds", "HTTP request latency", ["endpoint"]
)
WORK = Counter("devboard_work_requests_total", "Requests to the CPU-heavy /api/work endpoint")


def init_metrics(app: Flask) -> None:
    @app.before_request
    def _start_timer():
        g.start = time.perf_counter()

    @app.after_request
    def _record(response):
        endpoint = request.url_rule.rule if request.url_rule else "unmatched"
        if endpoint != "/metrics":
            REQUESTS.labels(request.method, endpoint, response.status_code).inc()
            LATENCY.labels(endpoint).observe(time.perf_counter() - g.get("start", time.perf_counter()))
        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
