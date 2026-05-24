# src/tools/rag_tool.py
from utils.interceptor import log_tool_call
from rag.retriever import recuperar_hibrido

@log_tool_call
def buscar_material_rag(query: str) -> str:
    """Procura material acadêmico no banco de dados."""
    return recuperar_hibrido(pergunta=query, k=3)