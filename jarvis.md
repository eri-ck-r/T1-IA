# JARVIS - Academic Personal Assistant: System Prompt & Requirements

## 0. Project Overview
You are assisting Erick and Mayara, Computer Science students at the Federal University of Mato Grosso do Sul (UFMS), in developing **JARVIS**, an AI-powered academic personal assistant. The system aims to organize academic life and enhance learning through Retrieval-Augmented Generation (RAG), Tool Calling, and Active Recall.

## 1. Core Tech Stack & Constraints
* **Language**: Python
* **LLM**: Gemma 3 12B IT (accessed via OpenAI API SDK with a custom `base_url`).
* **Data Storage**: SQLite(for agenda and tasks), `/data` directory for documents.
* **Code Conventions**: Strict separation of concerns, comprehensive logging, basic testing, and robust error handling.
* **Indexing Preference**: **Strictly use 0-based indexing** for all arrays, document chunking sequences, and loop counters.
  
## 2. Coding Conventions & Style Guide

The codebase for JARVIS strictly adheres to the following programming paradigms and stylistic choices to ensure maintainability, readability, and robust execution within an autonomous LLM loop.

### A. Core Logic & Indexing
* **Strict 0-Based Indexing:** All computational logic, loop counters, and array accesses fundamentally operate on a 0-based index. This applies universally across the architecture:
    * **RAG Chunking:** Document chunks are sequentially generated starting at `chunk_0000`.
    * **Database Fetching:** Arrays returned from SQLite queries (e.g., `fetchall()`) are accessed via `row[i]` where the initial iteration is explicitly index `0`.
    * **Prompt Engineering:** Tool options and system instructions provided to the LLM are numbered starting from `0`.

### B. Modularity & Separation of Concerns
* **Stateless Tooling:** Functions intended for the LLM agent to call (within `src/tools/`) must remain entirely stateless. They take explicit arguments, execute a single task, and return a string. They do not hold global variables or active memory.
* **Decoupled Infrastructure:** Heavy data processing (like vector embeddings or database creation) is completely isolated from the runtime agent. Code that builds the environment (`setup_db.py`, `ingest.py`) never interacts with code that queries the environment (`main.py`).

### C. Logging & Execution Flow
* **Interceptor Pattern:** Tool logging is never hardcoded inside the tool's business logic. Instead, Python decorators (`@log_tool_call`) are utilized to intercept and handle operational metadata (Tool Name, Inputs, Output) gracefully in the background.
* **Recursive Error Handling:** The main agent loop utilizes `try/except` blocks not just to prevent crashes, but to feed error states back to the LLM. If a JSON parse fails or a tool crashes, the error message is appended to the message history so the autonomous agent can attempt to self-correct.

### D. Readability & Pythonic Standards
* **Type Hinting:** Function signatures employ standard Python type hinting for inputs and return types (e.g., `def buscar_material_rag(query: str) -> str:`) to explicitly define the expected data contracts.
* **Descriptive Naming:** Variables and functions use explicit, descriptive naming conventions (e.g., `iniciar_quiz_active_recall` instead of `quiz()`). 
* **Bilingual Documentation:** While the core Python syntax and variables lean towards standard English/agnostic naming, the docstrings, terminal print statements, and LLM system prompts strictly use Portuguese to maintain alignment with the project's target language.
  
## 3. Mandatory Modules to Implement

### A. RAG System (Retrieval-Augmented Generation)
* **Input**: Academic PDFs, texts, and notes (minimum 10 documents stored in `/data`).
* **Pipeline**: Load documents -> Chunking -> Embeddings -> Vector Store -> Semantic Search -> LLM Generation.
* **Output**: Context-aware answers based *only* on the retrieved chunks.
* *Note*: The code must include documentation explaining the chosen chunking strategy and its impact on the RAG performance.

### B. Tool Calling Agent
* The Gemma LLM must dynamically decide when to call tools (no fixed hardcoded logic).
* **Required Tools (Min 5)**:
    1.  `consultar_agenda()`: Retrieve schedule.
    2.  `listar_tarefas()`: List current tasks.
    3.  `adicionar_tarefa(task)`: Add a new task.
    4.  `concluir_tarefa(task_id)`: Mark a task as done.
    5.  `buscar_material_rag(query)`: Query the vector database.
* **Requirement**: Must implement an interceptor to log every tool call explicitly capturing: `Tool Name`, `Input Parameters`, and `Output`.

### C. Interactive Learning Modules
* Must implement at least 2 learning features.
* **Feature 1 (Mandatory Interactive)**: Active Recall / Interactive Quiz. The system must formulate a question based on the academic material, wait for the user's input, and then evaluate the correctness of the answer.
* **Feature 2**: Recommendations for review, identification of difficulties, or exercise generation.

## 4. Evaluation & Error Analysis
* **System Evaluation Pipeline**: Create a test script that evaluates 10 predefined academic questions against the RAG system. It must log: The query, the retrieved documents, the LLM answer, and a classification mapping (`correct`, `partially correct`, `incorrect`).
* **Error Analysis Framework**: Setup a logging/markdown structure to document at least 3 system failures detailing: `Type` (e.g., retrieval failure, hallucination, ambiguity), `Cause`, and `Proposed Solution`.

## 5. Proposed Repository Structure
```text
jarvis/
├── data/                  # Minimum 10 academic documents + dataset documentation
├── src/
│   ├── rag/               # Document loaders, chunking logic, vector store management
│   ├── tools/             # Tool definitions (agenda, tasks, etc.)
│   ├── agent/             # LLM API integration and tool calling loop
│   ├── learning/          # Active recall and educational logic
│   └── utils/             # Logging and 0-indexed helper functions
├── tests/                 # System evaluation (10 Q&A tests) and unit tests
├── database/              # SQLite/JSON persistence for agenda/tasks
├── requirements.txt
└── README.md              # Setup instructions and list of AI tools used
```

## 6. Progress Report: Phase 1 Achievements

### A. Core System & Agent Architecture
* **LLM Integration:** Connected to the `gemma-3-12b-it` model via the LIA UFMS endpoint using the OpenAI SDK.
* **Autonomous Agent Loop (`src/agent/main.py`):** Implemented a custom, recursive tool-calling loop. Due to server-side vLLM restrictions (`400 BadRequestError` on native tool calls), engineered a prompt-based workaround where JARVIS outputs JSON objects. The loop recursively checks for these JSONs, executes tools locally, and feeds data back until ready for a final natural language response.
* **The Interceptor (`src/utils/interceptor.py`):** Fulfilled the mandatory requirement to log every tool call. The `@log_tool_call` decorator invisibly intercepts executions and logs `Tool Name`, `Input Parameters`, and `Output` to `logs/tool_calls.log`.
* **Strict 0-Based Indexing:** Consistently applied across array formatting, database row parsing, global chunk ID generation (`chunk_0000`), and system prompt instructions.

### B. Storage & Database (`database/`)
* **SQLite Architecture:** Upgraded from JSON to a robust SQLite implementation to prevent data corruption, handle concurrent access, and enforce strict schema rules.
* **Database Initialization (`setup_db.py`):** Created a standalone script to automatically generate `jarvis.db` with the required `tarefas` and `agenda` tables.

### C. RAG System (`src/rag/`)
* **Modular Ingestion (`ingest.py`):** Transitioned from Jupyter Notebook to a clean, reusable script. Dynamically sweeps the `/data` directory, processes multiple PDFs via Docling, chunks by paragraphs, and saves BM25 and FAISS (embeddings) indexes to disk.
* **Metadata Tracking:** Injected a `"fonte"` (source file) tag to every chunk, allowing the LLM to cite specific PDFs.
* **The Retriever (`retriever.py`):** Built a stateless function that loads global indexes and executes a hybrid search, returning a formatted, 0-indexed string of text chunks.

### D. Tool Calling Module (`src/tools/`)
* Implemented **3 out of 5** mandatory tools:
    1. `buscar_material_rag(query)`: Executes the hybrid RAG search.
    2. `listar_tarefas()`: Queries SQLite and returns formatted active tasks.
    3. `adicionar_tarefa(descricao)`: Inserts new task rows into the database.
       
### E. Interactive Learning (`src/learning/`)
* **Active Recall Prototype (`active_recall.py`):** Built the standalone logic for Mandatory Feature 1. It loads RAG chunks, selects a text block using a random 0-based index, prompts the LLM to generate a contextual question, waits for terminal input, and evaluates the user's answer against the ground truth.
---

## 7. Remaining Roadmap (To-Do)
* **Remaining Tools (2/5):** * `consultar_agenda()`
    * `concluir_tarefa(task_id)`
* **Learning Feature 1:** Implement the secondary educational feature (e.g., generating review recommendations based on task difficulty).
* **Evaluation Pipeline (`tests/evaluate_rag.py`):** Build the script to test 10 predefined academic questions against the RAG system and log the `correct / partially correct / incorrect` mapping.
* **Error Analysis Framework:** Document the 3 required system failures (utilizing organic examples encountered, such as the vLLM server block and single-turn execution failure).
