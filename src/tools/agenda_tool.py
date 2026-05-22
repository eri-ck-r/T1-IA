# src/tools/agenda_tool.py
import sqlite3
from utils.interceptor import log_tool_call

DB_PATH = "database/jarvis.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@log_tool_call
def consultar_agenda() -> str:
    """Retorna todos os compromissos agendados no banco de dados ordenados por data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, titulo, data_hora, descricao FROM agenda ORDER BY data_hora ASC")
    rows = cursor.fetchall()
    conn.close()

    # Verificação baseada em 0 para array vazio
    if len(rows) == 0:
        return "Nenhum compromisso agendado no momento."

    # Formatação dos resultados utilizando iteração explícita baseada em 0
    linhas_formatadas = []
    for i in range(len(rows)):
        compromisso = rows[i]
        # compromisso[0] = id, compromisso[1] = titulo, compromisso[2] = data_hora, compromisso[3] = descricao
        linhas_formatadas.append(
            f"ID {compromisso[0]}: {compromisso[1]} - Data/Hora: {compromisso[2]} | Obs: {compromisso[3]}"
        )

    return "\n".join(linhas_formatadas)