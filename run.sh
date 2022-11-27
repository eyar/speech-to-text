#!/bin/bash
cd /app/src
exec uvicorn --host 0.0.0.0 api:app --reload &
exec celery -A tasks worker -l info