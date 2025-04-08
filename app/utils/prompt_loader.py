from pathlib import Path

PROMPT_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(agent_name: str) -> str:
    prompt_path = PROMPT_DIR / f"{agent_name}.prompt.txt"
    return prompt_path.read_text(encoding="utf-8")
