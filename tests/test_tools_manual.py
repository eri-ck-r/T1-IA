# tests/test_tools_manual.py
import sys
import os

# Ensure Python can find your src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tools.rag_tool import buscar_material_rag
from tools.tasks_tool import adicionar_tarefa, listar_tarefas

def run_tests():
    print("=== TEST 0: ADDING A TASK ===")
    add_msg = adicionar_tarefa(descricao="Configurar o Agent LLM do JARVIS")
    print(add_msg)
    
    print("\n=== TEST 1: LISTING TASKS ===")
    tasks_list = listar_tarefas()
    print(tasks_list)
    
    print("\n=== TEST 2: RAG SEARCH ===")
    # Replace this string with something actually relevant to your VNS.pdf
    rag_context = buscar_material_rag(query="quais os componentes do VNS?") 
    print(rag_context)
    
    print("\n=== TEST 3: CHECK YOUR LOGS ===")
    print("Now, open the file at: logs/tool_calls.log")
    print("If the interceptor worked, you should see exactly 3 entries there!")

if __name__ == "__main__":
    # Note: Make sure you ran 'python database/setup_db.py' 
    # and 'python src/rag/ingest.py' before running this!
    run_tests()