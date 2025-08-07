#!/bin/bash

# run the ollama server
module load ollama/0.6.0-GCCcore-12.3.0-CUDA-12.1.1
ollama serve

# (D) Optional: Export environment variables your code might need
#pip install "wandb<0.15.9"
