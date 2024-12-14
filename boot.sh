#!/bin/bash
gunicorn --workers=${WORKERS:-1} --threads ${THREADS:-2} --timeout 0 --bind :${PORT:-8080} --worker-class uvicorn.workers.UvicornWorker main:app