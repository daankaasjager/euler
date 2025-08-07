#!/bin/bash

# Stop Ollama if running
pkill -f "ollama serve"
pkill -f "ollama run"

# Remove existing models from both locations
rm -rf /home2/$USER/.ollama/models
rm -rf /scratch/$USER/ollama_home/models

# Create new directory structure
mkdir -p /scratch/$USER/ollama_home/models

# Set permissions
chmod 755 /scratch/$USER/ollama_home/models

# Export the environment variable
export OLLAMA_HOME=/scratch/$USER/ollama_home

# Clean up any remaining Ollama processes
pkill -f "ollama serve"
pkill -f "ollama run"

# Wait a moment to ensure all processes are gone
sleep 2

echo "Ollama cleanup completed. You can now run the setup script again."
