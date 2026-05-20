# src/agent/main.py
import json
import os
import sys
from openai import OpenAI

# Ensure Python can find the src directory imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your tools
from tools.rag_tool import buscar_material_rag
from tools.tasks_tool import adicionar_tarefa, listar_tarefas

# 1. Define the Tool Schemas (The instructions for Gemma)
jarvis_tools = [
    {
        "type": "function",
        "function": {
            "name": "buscar_material_rag",
            "description": "Busca material acadêmico no banco de dados vetorial para responder perguntas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "A pergunta detalhada ou termo de busca."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_tarefas",
            "description": "Lista todas as tarefas atuais no banco de dados.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adicionar_tarefa",
            "description": "Adiciona uma nova tarefa à lista de tarefas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "descricao": {
                        "type": "string", 
                        "description": "A descrição da tarefa a ser adicionada."
                    }
                },
                "required": ["descricao"]
            }
        }
    }
]

# 2. Map the JSON names to your actual Python functions
available_functions = {
    "buscar_material_rag": buscar_material_rag,
    "listar_tarefas": listar_tarefas,
    "adicionar_tarefa": adicionar_tarefa
}

# 3. Initialize the Client
# Using the base_url from your Colab notebook
client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', 
    api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A'
)

def run_agent():
    print("Iniciando JARVIS... (Digite 'sair' para encerrar)")
    
    # 0-based index for our initial system message
    messages = [
        {
            "role": "system", 
            "content": "Você é o JARVIS, um assistente acadêmico. Use as ferramentas disponíveis para gerenciar tarefas e buscar informações nos documentos do usuário. Responda de forma clara, direta e em português."
        }
    ]
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("JARVIS: Encerrando sistemas. Até logo!")
            break
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            # First API Call: Ask Gemma to evaluate the prompt
            response = client.chat.completions.create(
                model='google/gemma-3-12b-it',
                messages=messages,
                tools=jarvis_tools
            )
            
            # Using 0-based indexing to access the first choice
            response_msg = response.choices[0].message
            
            # Check if Gemma decided a tool call is necessary
            if response_msg.tool_calls:
                messages.append(response_msg)
                
                # Process all requested tool calls
                for i in range(len(response_msg.tool_calls)):
                    tool_call = response_msg.tool_calls[i]
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    print(f"\n[JARVIS acessando: {func_name}...]")
                    
                    # Execute the matched Python function dynamically
                    func_to_call = available_functions.get(func_name)
                    if func_to_call:
                        tool_output = func_to_call(**args)
                    else:
                        tool_output = f"Erro: Ferramenta {func_name} não encontrada."
                        
                    # Append the tool's result to the message history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(tool_output)
                    })
                
                # Second API Call: Generate final answer with the new context
                final_response = client.chat.completions.create(
                    model='google/gemma-3-12b-it',
                    messages=messages
                )
                
                final_text = final_response.choices[0].message.content
                print(f"\nJARVIS: {final_text}")
                messages.append({"role": "assistant", "content": final_text})
                
            else:
                # Direct standard response (No tools triggered)
                print(f"\nJARVIS: {response_msg.content}")
                messages.append({"role": "assistant", "content": response_msg.content})
                
        except Exception as e:
            print(f"\n[ERRO DE SISTEMA]: {e}")

if __name__ == "__main__":
    run_agent()