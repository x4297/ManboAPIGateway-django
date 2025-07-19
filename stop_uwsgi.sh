#!/bin/bash
source ./.venv/bin/activate
uwsgi --stop ManboAPIGateway.pid
deactivate