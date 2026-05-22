# src/tools/agenda_tool.py
import sqlite3
from datetime import datetime, timedelta
from utils.interceptor import log_tool_call

DB_PATH = "database/jarvis.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


@log_tool_call
def adicionar_evento_agenda(titulo: str, data_hora: str, tipo: str, descricao: str = "") -> str:
    """
    Adiciona um evento (aula ou prova) na agenda.
    Formato obrigatório para data_hora: 'YYYY-MM-DD HH:MM'
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Valida e converte a string de data para um objeto datetime
    try:
        dt_inicial = datetime.strptime(data_hora, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Erro: Formato de data_hora inválido. O LLM deve usar 'YYYY-MM-DD HH:MM'."

    eventos_inseridos = 0

    # 2. Lógica de repetição baseada no tipo
    if tipo.lower() == 'aula':
        # Indexação baseada em 0: i=0 é a aula atual, até i=17 (próximas 17 semanas)
        for i in range(18):
            dt_atual = dt_inicial + timedelta(weeks=i)
            dt_str = dt_atual.strftime("%Y-%m-%d %H:%M")

            cursor.execute(
                "INSERT INTO agenda (titulo, data_hora, tipo, descricao) VALUES (?, ?, ?, ?)",
                (titulo, dt_str, tipo, descricao)
            )
            eventos_inseridos += 1

        mensagem_retorno = f"Sucesso: {eventos_inseridos} aulas de '{titulo}' cadastradas semanalmente a partir de {data_hora}."

    else:
        # Se for prova, evento único
        cursor.execute(
            "INSERT INTO agenda (titulo, data_hora, tipo, descricao) VALUES (?, ?, ?, ?)",
            (titulo, data_hora, tipo, descricao)
        )
        mensagem_retorno = f"Sucesso: Prova '{titulo}' agendada para {data_hora}."

    conn.commit()
    conn.close()
    return mensagem_retorno


@log_tool_call
def consultar_agenda(dias: int = 7) -> str:
    """
    Consulta a agenda para os próximos N dias.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Pega a data atual e a data limite
    hoje = datetime.now()
    limite = hoje + timedelta(days=dias)

    hoje_str = hoje.strftime("%Y-%m-%d %H:%M")
    limite_str = limite.strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        "SELECT id, titulo, data_hora, tipo FROM agenda WHERE data_hora BETWEEN ? AND ? ORDER BY data_hora ASC",
        (hoje_str, limite_str)
    )
    rows = cursor.fetchall()
    conn.close()

    if len(rows) == 0:
        return f"Nenhum evento programado para os próximos {dias} dias."

    linhas_formatadas = []
    # Indexação baseada em 0 para acessar a tupla do SQLite
    for i in range(len(rows)):
        evento = rows[i]
        linhas_formatadas.append(f"[{evento[2]}] {evento[3].upper()}: {evento[1]} (ID {evento[0]})")

    return "\n".join(linhas_formatadas)


# Adicione isso ao final do arquivo src/tools/agenda_tool.py

@log_tool_call
def remover_evento_agenda(evento_id: int) -> str:
    """Remove um evento específico da agenda (aula ou prova) usando o ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agenda WHERE id = ?", (evento_id,))
    linhas_afetadas = cursor.rowcount

    conn.commit()
    conn.close()

    if linhas_afetadas == 0:
        return f"Erro: Nenhum evento encontrado na agenda com o ID {evento_id}."

    return f"Evento {evento_id} removido da agenda com sucesso."


@log_tool_call
def editar_evento_agenda(
        evento_id: int,
        novo_titulo: str = None,
        nova_data_hora: str = None,
        novo_tipo: str = None,
        nova_descricao: str = None
) -> str:
    """
    Modifica os detalhes de um evento existente na agenda.
    Formatos aceitos para novo_tipo: 'aula' ou 'prova'.
    Formato obrigatório para nova_data_hora: 'YYYY-MM-DD HH:MM'.
    """
    if not any([novo_titulo, nova_data_hora, novo_tipo, nova_descricao]):
        return "Erro: Nenhuma alteração fornecida. Informe ao menos um campo para atualizar."

    # Validação estrita de data caso o LLM queira alterar o horário
    if nova_data_hora:
        try:
            datetime.strptime(nova_data_hora, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Erro: Formato de nova_data_hora inválido. Use 'YYYY-MM-DD HH:MM'."

    conn = get_connection()
    cursor = conn.cursor()

    campos = []
    valores = []

    if novo_titulo:
        campos.append("titulo = ?")
        valores.append(novo_titulo)
    if nova_data_hora:
        campos.append("data_hora = ?")
        valores.append(nova_data_hora)
    if novo_tipo:
        campos.append("tipo = ?")
        valores.append(novo_tipo.lower())
    if nova_descricao:
        campos.append("descricao = ?")
        valores.append(nova_descricao)

    valores.append(evento_id)
    query = f"UPDATE agenda SET {', '.join(campos)} WHERE id = ?"

    cursor.execute(query, tuple(valores))
    linhas_afetadas = cursor.rowcount

    conn.commit()
    conn.close()

    if linhas_afetadas == 0:
        return f"Erro: Nenhum evento encontrado na agenda com o ID {evento_id}."

    return f"Evento {evento_id} atualizado na agenda com sucesso."