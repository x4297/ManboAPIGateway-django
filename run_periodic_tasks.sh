#!/bin/bash
source .venv/bin/activate
nohup celery -A ManboAPIGateway worker --concurrency=1 --loglevel=INFO -B >> celery.log 2>&1 &
deactivate