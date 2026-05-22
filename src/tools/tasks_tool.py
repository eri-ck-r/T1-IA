# src/tools/tasks_tool.py
import sqlite3
from utils.interceptor import log_tool_call
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "jarvis.db"

def get_connection():
    # Helper to keep connections clean
    return sqlite3.connect(str(DB_PATH))

@log_tool_call
def listar_tarefas() -> str:
    """Retorna uma lista de todas as tarefas e seus IDs."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, descricao, status FROM tarefas")
    rows = cursor.fetchall()
    conn.close()
    
    # 0-based array check to ensure we have data
    if len(rows) == 0:
        return "Nenhuma tarefa registrada no momento."
        
    # Format the rows into a clean string for the LLM to read
    linhas_formatadas = []
    for i in range(len(rows)):
        tarefa = rows[i]
        # tarefa[0] = id, tarefa[1] = descricao, tarefa[2] = status
        linhas_formatadas.append(f"ID {tarefa[0]}: {tarefa[1]} [{tarefa[2]}]")
        
    return "\n".join(linhas_formatadas)

@log_tool_call
def adicionar_tarefa(descricao: str) -> str:
    """Adiciona uma nova tarefa ao banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tarefas (descricao) VALUES (?)", 
        (descricao,)
    )
    
    conn.commit()
    conn.close()
    
    return f"Tarefa adicionada com sucesso: '{descricao}'."

# Adicione isso ao final do arquivo src/tools/tasks_tool.py

@log_tool_call
def remover_tarefa(task_id: int) -> str:
    """Remove uma tarefa do banco de dados com base no seu ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tarefas WHERE id = ?", (task_id,))
    linhas_afetadas = cursor.rowcount

    conn.commit()
    conn.close()

    if linhas_afetadas == 0:
        return f"Erro: Nenhuma tarefa encontrada com o ID {task_id}."

    return f"Tarefa {task_id} removida com sucesso."


@log_tool_call
def editar_tarefa(task_id: int, nova_descricao: str = None, novo_status: str = None) -> str:
    """
    Edita a descrição e/ou o status de uma tarefa existente.
    Pode ser usado para marcar uma tarefa como 'concluída'.
    """
    if not nova_descricao and not novo_status:
        return "Erro: Nenhuma alteração fornecida. Informe uma nova descrição ou status."

    conn = get_connection()
    cursor = conn.cursor()

    # Constrói a query SQL dinamicamente com base no que foi fornecido
    campos = []
    valores = []

    if nova_descricao:
        campos.append("descricao = ?")
        valores.append(nova_descricao)

    if novo_status:
        campos.append("status = ?")
        valores.append(novo_status)

    # Adiciona o ID ao final dos valores para a cláusula WHERE
    valores.append(task_id)

    query = f"UPDATE tarefas SET {', '.join(campos)} WHERE id = ?"

    cursor.execute(query, tuple(valores))
    linhas_afetadas = cursor.rowcount

    conn.commit()
    conn.close()

    if linhas_afetadas == 0:
        return f"Erro: Nenhuma tarefa encontrada com o ID {task_id}."

    return f"Tarefa {task_id} atualizada com sucesso."