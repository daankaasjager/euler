import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from parse_pdf import process_and_store_document



# OpenAI Model
ollama_gemma_model = OpenAIModel(model_name="bramvanroy/fietje-2b-instruct:f16", 
                                 provider=OpenAIProvider(base_url='http://localhost:11434/v1'))

def run():
    model = ollama_gemma_model
    agent = Agent(
        model=model,
        system_prompt="Je bent een expert in wiskunde op het vmbo-tl 4 niveau. Je helpt leerlingen op een informele en behulpzame wijze en legt elke stap uit."
    )
    result = agent.run_sync(
        "In 2018 heeft een kasteel 65.000 bezoekers meer dan in 2017. Dat is een toename van 7,6%. " +
        "Hoeveel bezoekers waren er in 2017? Gebruik de procententabel."
    )
    print(result.data)
    print(result.usage())  

if __name__ == "__main__":
    parse = False
    pdf_path = "./getal&ruimte/leerboek_kgt_1.pdf"
    
    if parse:
        asyncio.run(process_and_store_document(pdf_path))
    run()
