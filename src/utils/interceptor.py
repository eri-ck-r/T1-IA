# src/utils/interceptor.py
import functools
import logging
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "tool_calls.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def log_tool_call(func):
    """
    A decorator that intercepts a tool execution to log its metadata.
    Matches the strict requirement: Tool Name, Input Parameters, and Output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Pegar nome da função
        tool_name = func.__name__
        
        # 2. Capturar parâmetros de entrada (mesclando argumentos posicionais e nomeados)
        inputs = kwargs if kwargs else args
        if not inputs:
            inputs = "None"
            
        try:
            # Executar a função da ferramenta real
            output = func(*args, **kwargs)
            
            # 3. Capturar saída e construir a mensagem de log final
            log_message = f"Tool Name: {tool_name} | Input Parameters: {inputs} | Output: {output}"
            
            # Escrever no arquivo .log
            logging.info(log_message)
            
            # Para printar no terminal
            print(f"\n[INTERCEPTOR] {log_message}")
            
            return output
            
        except Exception as e:
            # Se a ferramenta falhar, registra o erro para o agente não falhar semd izer nada
            error_message = f"Tool Name: {tool_name} | Input Parameters: {inputs} | ERROR: {str(e)}"
            logging.error(error_message)
            print(f"\n[INTERCEPTOR ERROR] {error_message}")
            raise e
            
    return wrapper