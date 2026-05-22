# src/tools/learning_tool.py
import json
import random
from utils.interceptor import log_tool_call
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "chunks.json"



@log_tool_call
def iniciar_quiz() -> str:
    """Busca um trecho aleatório do banco de dados para iniciar o active recall."""
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except FileNotFoundError:
        return "Erro: Banco de dados de texto não encontrado. Execute o ingest.py primeiro."

    if len(chunks) == 0:
        return "Nenhum material disponível para revisão no momento."

    # Seleção aleatória mantendo a indexação baseada em 0
    random_idx = random.randrange(0, len(chunks))
    chunk_selecionado = chunks[random_idx]

    texto = chunk_selecionado["texto"]
    fonte = chunk_selecionado.get("fonte", "Desconhecida")

    # Retorna uma instrução interna (invisível para o usuário) que guiará o LLM
    instrucao_llm = (
        f"Material base selecionado (Fonte: {fonte}):\n"
        f"'{texto}'\n\n"
        "INSTRUÇÃO DE SISTEMA: Assuma a persona de um tutor acadêmico. Formule UMA "
        "pergunta desafiadora baseada EXCLUSIVAMENTE no texto acima para testar o usuário. "
        "NÃO dê a resposta. Apenas faça a pergunta e aguarde o usuário responder no próximo turno. "
        "Após ele responder, use este mesmo material base para avaliar se a resposta dele está "
        "Correta, Parcialmente Correta ou Incorreta, e explique o porquê."
    )

    return instrucao_llm