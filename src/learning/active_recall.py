# src/learning/active_recall.py
import json
import os
import random
from openai import OpenAI

# Set up paths for Windows environment compatibility
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "database", "chunks.json")

# Initialize the LLM client
client = OpenAI(base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A')

def iniciar_quiz_active_recall():
    print("\n[Iniciando Módulo de Active Recall...]")

    # 1. Load the knowledge base
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except FileNotFoundError:
        return "Erro: Banco de dados de texto não encontrado. Execute o ingest.py primeiro."

    if len(chunks) == 0:
        return "Nenhum material disponível para revisão."

    # 2. Select a random chunk (Strictly 0-based index)
    random_idx = random.randrange(0, len(chunks))
    selected_chunk = chunks[random_idx]["texto"]

    # 3. Phase 1: Generate the Question
    prompt_geracao = f"""Você é um professor universitário testando um aluno de Ciência da Computação.
Com base EXCLUSIVAMENTE no trecho abaixo, formule UMA pergunta desafiadora para testar o conhecimento do aluno.
Não inclua a resposta, apenas a pergunta.

Trecho:
{selected_chunk}"""

    try:
        response = client.chat.completions.create(
            model='google/gemma-3-12b-it',
            messages=[{"role": "user", "content": prompt_geracao}]
        )
        pergunta = response.choices[0].message.content.strip()

        print(f"\nJARVIS (Tutor): {pergunta}")

        # 4. Wait for user input
        resposta_aluno = input("\nSua Resposta: ")

        if resposta_aluno.lower() in ['sair', 'cancelar', 'quit']:
            return "Sessão de estudos cancelada."

        # 5. Phase 2: Evaluate the Answer
        prompt_avaliacao = f"""Você é um professor universitário. Você fez a seguinte pergunta ao aluno:
"{pergunta}"

O texto base correto é:
"{selected_chunk}"

A resposta do aluno foi:
"{resposta_aluno}"

Avalie a resposta do aluno. Diga se está Correta, Parcialmente Correta ou Incorreta. 
Em seguida, explique o porquê de forma breve e construtiva."""

        avaliacao_response = client.chat.completions.create(
            model='google/gemma-3-12b-it',
            messages=[{"role": "user", "content": prompt_avaliacao}]
        )

        avaliacao_final = avaliacao_response.choices[0].message.content.strip()
        print(f"\nJARVIS (Avaliação):\n{avaliacao_final}")

        return "\n[Fim do Quiz]"

    except Exception as e:
        return f"Erro na comunicação com a LLM: {e}"

if __name__ == "__main__":
    # Permite testar o módulo diretamente do terminal
    iniciar_quiz_active_recall()