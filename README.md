# Euler Project

## Project Structure

```
euler/
├── scripts/              # Contains all executable scripts
│   ├── environment_setup.sh   # Sets up environment modules
│   ├── activate_venv.sh      # Activates Python virtual environment
│   └── start_model.sh        # Starts the Ollama model
├── frontend/             # Streamlit UI application
│   └── streamlit_app.py     # Main Streamlit application
├── main.py              # Main application code
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
└── run_all.sh          # Script to run all components
```

## Project Configuration

### pyproject.toml
The project uses `pyproject.toml` for configuration:
- Project name and version management
- Package definitions
- Build system configuration

### Environment Management
- All environment setup is handled through `scripts/environment_setup.sh`
- Python virtual environment is managed through `scripts/activate_venv.sh`
- Dependencies are tracked in `requirements.txt`

### Model Management
- Model operations are handled through `scripts/start_model.sh`
- Environment variables for Ollama are properly set
- Model paths are configurable through environment variables

### Frontend
The project includes a Streamlit-based UI that is integrated into the main application:
- Main application: `frontend/streamlit_app.py`
- Used for debugging and visualization
- Configured through the main application's mode

### Running the Project

#### Environment Setup
To set up the environment:

```bash
./run_all.sh
```

This will:
1. Set up the environment
2. Activate the virtual environment
3. Start the model

Each component runs in its own tmux pane for easy monitoring.

#### Running the Application
After environment setup, run the main application with different modes:

```bash
# Run the Streamlit UI (serves the frontend)
python main.py --mode serve_api

# Run the main application in different modes
python main.py --mode split_pdf
python main.py --mode test_agent
python main.py --mode delete_data
```