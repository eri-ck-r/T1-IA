# src/agent/main.py
import json
import os
import sys
import re
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.rag_tool import buscar_material_rag
from tools.tasks_tool import adicionar_tarefa, listar_tarefas, concluir_tarefa  # Atualizado
from tools.learning_tool import iniciar_quiz
from tools.rag_tool import buscar_material_rag
from tools.tasks_tool import adicionar_tarefa, listar_tarefas
from tools.learning_tool import iniciar_quiz


available_functions = {
    "buscar_material_rag": buscar_material_rag,
    "listar_tarefas": listar_tarefas,
    "adicionar_tarefa": adicionar_tarefa,
    "iniciar_quiz": iniciar_quiz,
    "concluir_tarefa": concluir_tarefa,   # Adicionado
}


load_dotenv()
LIA_BASE_URL = os.getenv("LIA_BASE_URL")
JARVIS_API_KEY = os.getenv("JARVIS_API_KEY")

client = OpenAI(base_url=LIA_BASE_URL, api_key=JARVIS_API_KEY)

def run_agent():
    print("Iniciando JARVIS... (Modo Prompt-Based)")

    # We embed the tool definitions directly into the system prompt
    system_instruction = """Você é o JARVIS, um assistente acadêmico. 
    Você tem acesso às seguintes ferramentas:
    0: {"tool_call": "buscar_material_rag", "args": {"query": "pergunta"}}
    1: {"tool_call": "listar_tarefas", "args": {}}
    2: {"tool_call": "adicionar_tarefa", "args": {"descricao": "texto da tarefa"}}
    3: {"tool_call": "iniciar_quiz", "args": {}}
    4: {"tool_call": "concluir_tarefa", "args": {"id_tarefa": id_numerico}}

    Regras de ativação:
    - Se o usuário indicar que terminou, concluiu ou finalizou uma tarefa específica, use concluir_tarefa passando o ID numérico correspondente.
    - Se você precisar usar uma ferramenta para responder ao usuário, você DEVE responder APENAS com o formato JSON da ferramenta escolhida e nenhum outro texto. Se não precisar de ferramentas, responda normalmente em português."""

    messages = [{"role": "system", "content": system_instruction}]

    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            break

        messages.append({"role": "user", "content": user_input})

        try:
            # Loop interno para lidar com múltiplas chamadas de ferramentas em sequência
            while True:
                response = client.chat.completions.create(
                    model='google/gemma-3-12b-it',
                    messages=messages
                )

                response_text = response.choices[0].message.content.strip()

                # Procura por um bloco JSON na resposta
                json_match = re.search(r'\{.*"tool_call".*\}', response_text, re.DOTALL)

                if json_match:
                    # 1. Parse the JSON
                    try:
                        tool_data = json.loads(json_match.group(0))
                        func_name = tool_data.get("tool_call")
                        args = tool_data.get("args", {})

                        print(f"\n[JARVIS ativando ferramenta: {func_name}...]")

                        # 2. Execute the matched Python function
                        func_to_call = available_functions.get(func_name)
                        if func_to_call:
                            tool_output = func_to_call(**args)
                        else:
                            tool_output = "Erro: Ferramenta não encontrada."
                    except json.JSONDecodeError:
                        tool_output = "Erro: Formato JSON inválido."

                    # 3. Add the interaction to history and prompt again
                    # We tell it: if you need another tool, do it now.
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": f"Resultado da ferramenta: {tool_output}\nSe precisar usar mais uma ferramenta, envie apenas o novo JSON. Se já terminou todas as ações, dê a resposta final em português."
                    })

                else:
                    # Se não houver JSON, é a resposta final em texto natural
                    print(f"\nJARVIS: {response_text}")
                    messages.append({"role": "assistant", "content": response_text})
                    break  # Sai do loop interno e aguarda o próximo input do usuário

        except Exception as e:
            print(f"\n[ERRO DE SISTEMA]: {e}")


if __name__ == "__main__":
    run_agent()