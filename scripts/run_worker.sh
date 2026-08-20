#!/usr/bin/env bash
# Start Celery Worker for Opportunity Finder Async Queue

export PYTHONPATH=.
./venv/bin/celery -A src.tasks.celery_app worker --loglevel=INFO -c 4
