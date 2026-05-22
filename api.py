# api.py — JARVIS FastAPI Backend
# Place this file at the root of the jarvis/ project directory.
# Run with: uvicorn api:app --reload

import json
import os
import re
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path setup — makes src/ importable from the project root
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "src"))

from tools.rag_tool import buscar_material_rag
from tools.tasks_tool import adicionar_tarefa, listar_tarefas
from tools.learning_tool import iniciar_quiz

# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------
load_dotenv()
LIA_BASE_URL = os.getenv("LIA_BASE_URL")
JARVIS_API_KEY = os.getenv("JARVIS_API_KEY")

client = OpenAI(base_url=LIA_BASE_URL, api_key=JARVIS_API_KEY)

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------
available_functions = {
    "buscar_material_rag": buscar_material_rag,
    "listar_tarefas": listar_tarefas,
    "adicionar_tarefa": adicionar_tarefa,
    "iniciar_quiz": iniciar_quiz,
}

SYSTEM_PROMPT = """Você é o JARVIS, um assistente acadêmico inteligente.
Você tem acesso às seguintes ferramentas:
0: {"tool_call": "buscar_material_rag", "args": {"query": "pergunta"}}
1: {"tool_call": "listar_tarefas", "args": {}}
2: {"tool_call": "adicionar_tarefa", "args": {"descricao": "texto da tarefa"}}
3: {"tool_call": "iniciar_quiz", "args": {}}

Se o usuário pedir para ser testado, revisar matéria ou fazer uma pergunta de estudo, use iniciar_quiz.
Se precisar usar uma ferramenta, responda APENAS com o JSON correspondente e nenhum outro texto.
Se não precisar de ferramentas, responda normalmente em português."""

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="JARVIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Fine for local use
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the chat UI at /chat if the folder exists
chat_dir = BASE_DIR / "chat"
if chat_dir.exists():
    app.mount("/chat", StaticFiles(directory=str(chat_dir), html=True), name="chat")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class Message(BaseModel):
    role: str       # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    tool_calls_made: List[str] = []  # Names of tools that were called, for the UI


# ---------------------------------------------------------------------------
# Core agent logic (extracted from main.py)
# ---------------------------------------------------------------------------
def run_agent_turn(user_message: str, history: List[Message]) -> dict:
    """
    Processes one user turn through the JARVIS agent loop.
    Returns the final text response and a list of tool names that were called.
    """
    # Build the message list: system + history + new user message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    tools_used = []
    MAX_TOOL_ITERATIONS = 5  # Safety cap to prevent infinite loops

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model="google/gemma-3-12b-it",
            messages=messages,
        )
        response_text = response.choices[0].message.content.strip()

        # Check if the model wants to call a tool
        json_match = re.search(r'\{.*"tool_call".*\}', response_text, re.DOTALL)

        if json_match:
            try:
                tool_data = json.loads(json_match.group(0))
                func_name = tool_data.get("tool_call")
                args = tool_data.get("args", {})

                func_to_call = available_functions.get(func_name)
                if func_to_call:
                    tool_output = func_to_call(**args)
                    tools_used.append(func_name)
                else:
                    tool_output = f"Erro: ferramenta '{func_name}' não encontrada."

            except json.JSONDecodeError:
                tool_output = "Erro: formato JSON inválido na chamada de ferramenta."

            # Feed the tool result back into the conversation
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    f"Resultado da ferramenta: {tool_output}\n"
                    "Se precisar usar mais uma ferramenta, envie apenas o novo JSON. "
                    "Se já terminou todas as ações, dê a resposta final em português."
                ),
            })

        else:
            # No tool call — this is the final natural language response
            return {"response": response_text, "tool_calls_made": tools_used}

    # Fallback if we hit the iteration cap
    return {
        "response": "Desculpe, não consegui processar sua solicitação. Tente novamente.",
        "tool_calls_made": tools_used,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "JARVIS online", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_agent_turn(request.message, request.history)
    return ChatResponse(
        response=result["response"],
        tool_calls_made=result["tool_calls_made"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}
