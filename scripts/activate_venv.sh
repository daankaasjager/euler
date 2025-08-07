#!/bin/bash

module purge
module load Python/3.11.3-GCCcore-12.3.0
module load poetry/1.7.1-GCCcore-12.3.0
echo "venv, python is: $(which python)"

SCRATCH=/scratch/s3905845
export TMPDIR="$SCRATCH/tmp"
export POETRY_CACHE_DIR="$SCRATCH/poetry/cache"
export POETRY_HOME="$SCRATCH/poetry/home"
export POETRY_VIRTUALENVS_PATH="$SCRATCH/poetry/venvs"

mkdir -p "$TMPDIR" "$POETRY_CACHE_DIR" "$POETRY_HOME" "$POETRY_VIRTUALENVS_PATH"

echo "Python interpreter: $(which python)"
echo "Poetry executable: $(which poetry)"
echo "Temp dir:         $TMPDIR"
echo "Poetry cache:     $POETRY_CACHE_DIR"
echo "Poetry venvs:     $POETRY_VIRTUALENVS_PATH"

poetry init \
  --name euler \
  --description "Agentic math tutor" \
  --author "Daan Kaasjager <daankaasjager@hotmail.com>" \
  --no-interaction


xargs poetry add < requirements.txt

poetry add --dev pytest black flake8 mypy


poetry lock
poetry install


echo "Virtualenv location:"
poetry env info --path
echo
echo "Installed packages:"
poetry show --no-dev

echo
echo "🎉 Migration to Poetry complete! 🎉"