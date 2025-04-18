#!/bin/bash

OTEL_RESOURCE_ATTRIBUTES=service.name=contact-form,service.version=1.0.0 \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true \
OTEL_EXPORTER_OTLP_INSECURE=true \
opentelemetry-instrument --logs_exporter otlp \
uvicorn app:app --host 0.0.0.0 --port 8001
