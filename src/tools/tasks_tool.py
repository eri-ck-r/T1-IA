# src/tools/tasks_tool.py
import sqlite3
from utils.interceptor import log_tool_call

DB_PATH = "database/jarvis.db"

def get_connection():
    # Helper to keep connections clean
    return sqlite3.connect(DB_PATH)

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


# Adicione esta função ao final do seu src/tools/tasks_tool.py

@log_tool_call
def concluir_tarefa(id_tarefa: int) -> str:
    """Modifica o status de uma tarefa para 'concluída' com base no seu ID numérico."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verificação de segurança para ver se a tarefa existe
    cursor.execute("SELECT id FROM tarefas WHERE id = ?", (id_tarefa,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return f"Erro: Nenhuma tarefa encontrada com o ID {id_tarefa}."

    # Executa a atualização do estado
    cursor.execute(
        "UPDATE tarefas SET status = 'concluída' WHERE id = ?",
        (id_tarefa,)
    )
    conn.commit()
    conn.close()

    return f"Tarefa com ID {id_tarefa} foi marcada como concluída com sucesso."