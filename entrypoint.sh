#!/bin/bash

if [[ "$@" == *"celery"* ]]; then
    echo "Running entrypoint from celery"
else
    echo "Running entrypoint from main app"
fi

echo "entry point done...echoing2"
python -c "import os;print(os.environ)" > out1.out
echo "ENV"
echo $ENVFILE
echo "copyied"
echo "$@"
exec "$@"
