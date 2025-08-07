import aiohttp
import os
import logging
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
logger = logging.getLogger(__name__)

async def call_ollama(model:str, system_prompt: str, chunk:str, max_tokens=1024, temperature=0.3) -> str:

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_URL}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": f"{system_prompt}\n\n{chunk[:1000]}"}
                    ],
                    "temperature": temperature,
                    "stream": False
                }   
            ) as resp:
                # Debugging: Check if an error status code is returned
                if resp.status != 200:
                    text = await resp.text()
                    print(f"❌ Ollama server returned status {resp.status} with body:\n{text} and model {model}")
                    return {"thema": "Fout", "omschrijving": "Fout"}

                # Then parse the JSON from the server
                data = await resp.json()

                # Debugging: print the entire JSON object from Ollama
                print("Raw JSON returned by Ollama:", data)

                # Next, check what the model’s content actually is
                raw_content = data["choices"][0]["message"]["content"]

                return raw_content
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return {"thema": "Fout", "omschrijving": "Fout"}
