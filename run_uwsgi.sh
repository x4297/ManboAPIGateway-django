#!/bin/bash
source ./.venv/bin/activate
uwsgi uwsgi.ini
deactivate