#!/bin/bash

module load ollama/0.6.0-GCCcore-12.3.0-CUDA-12.1.1
export OLLAMA_HOME=/scratch/$USER/ollama_home
export OLLAMA_MODELS=$OLLAMA_HOME/models

# Run the model
ollama run qwen2.5:14b
