#!/bin/bash

module purge
module load Python/3.11.3-GCCcore-12.3.0
source /scratch/s3905845/venvs/euler/bin/activate
echo "venv, python is: $(which python)"