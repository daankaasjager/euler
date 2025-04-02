#!/bin/bash
module purge
module load Python/3.11.3-GCCcore-12.3.0
source $HOME/venvs/euler/bin/activate

# (B) Print out which python just to check
echo "venv, python is: $(which python)"


module load ollama/0.6.0-GCCcore-12.3.0-CUDA-12.1.1
ollama serve


module load ollama/0.6.0-GCCcore-12.3.0-CUDA-12.1.1
export OLLAMA_MODELS=/scratch/$USER/ollama_home/models
ollama run gemma3:12b
# (D) Optional: Export environment variables your code might need
#pip install "wandb<0.15.9"
