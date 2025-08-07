from pathlib import Path

PROMPT_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(agent_name: str) -> str:
    prompt_path = PROMPT_DIR / f"{agent_name}.prompt.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file {prompt_path} does not exist.")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    if not prompt:
        raise ValueError(f"Prompt file {prompt_path} is empty.")
    return prompt
