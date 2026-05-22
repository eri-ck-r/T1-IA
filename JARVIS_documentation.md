# JARVIS — Documentação Técnica
**Assistente Pessoal Acadêmico com IA**
Desenvolvido por Erick e Mayara — Ciência da Computação, UFMS

---

## Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Stack Tecnológica](#2-stack-tecnológica)
3. [Estrutura do Repositório](#3-estrutura-do-repositório)
4. [Convenções de Código](#4-convenções-de-código)
5. [Módulos Implementados](#5-módulos-implementados)
   - [5.1 Banco de Dados — `setup_db.py`](#51-banco-de-dados--setup_dbpy)
   - [5.2 Ingestão de Documentos — `ingest.py`](#52-ingestão-de-documentos--ingestpy)
   - [5.3 Recuperação Híbrida — `retriever.py`](#53-recuperação-híbrida--retrieverpy)
   - [5.4 Interceptor de Ferramentas — `interceptor.py`](#54-interceptor-de-ferramentas--interceptorpy)
   - [5.5 Ferramentas do Agente — `src/tools/`](#55-ferramentas-do-agente--srctools)
   - [5.6 Active Recall — `active_recall.py`](#56-active-recall--active_recallpy)
   - [5.7 Loop do Agente — `main.py`](#57-loop-do-agente--mainpy)
6. [Fluxo de Execução do Sistema](#6-fluxo-de-execução-do-sistema)
7. [Estratégia de Chunking e Impacto no RAG](#7-estratégia-de-chunking-e-impacto-no-rag)
8. [Status de Implementação](#8-status-de-implementação)
9. [Roadmap — Pendências](#9-roadmap--pendências)
10. [Configuração e Execução](#10-configuração-e-execução)

---

## 1. Visão Geral do Projeto

O JARVIS é um assistente pessoal acadêmico com IA, projetado para organizar a vida universitária e potencializar o aprendizado. O sistema integra três pilares tecnológicos principais:

- **RAG (Retrieval-Augmented Generation):** respostas fundamentadas exclusivamente no material acadêmico do usuário.
- **Tool Calling:** o LLM decide autonomamente quais ferramentas acionar (agenda, tarefas, busca semântica, quiz).
- **Active Recall:** módulo de aprendizado interativo que formula perguntas com base no conteúdo estudado e avalia as respostas do aluno.

O sistema é acessado via terminal e se comunica com o modelo `gemma-3-12b-it` através do endpoint LIA da UFMS, utilizando o SDK OpenAI com `base_url` customizada.

---

## 2. Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| LLM | `google/gemma-3-12b-it` via LIA UFMS (OpenAI SDK) |
| Busca Semântica | FAISS (`IndexFlatIP`) + `sentence-transformers` |
| Busca Lexical | BM25 (`rank_bm25`) |
| Conversão de PDF | Docling (`DocumentConverter`) |
| Banco de Dados | SQLite (`jarvis.db`) |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` |
| Variáveis de Ambiente | `python-dotenv` |
| Logging | `logging` (stdlib) com decorator personalizado |

---

## 3. Estrutura do Repositório

```text
jarvis/
├── data/                        # Mínimo 10 documentos acadêmicos em PDF
├── database/
│   ├── setup_db.py              # Inicialização do SQLite
│   ├── jarvis.db                # Banco de dados gerado (tarefas + agenda)
│   ├── chunks.json              # Chunks extraídos dos PDFs
│   ├── bm25_index.pkl           # Índice BM25 serializado
│   ├── faiss_index.bin          # Índice FAISS serializado
│   └── embeddings_matrix.pkl   # Matriz de embeddings serializada
├── src/
│   ├── agent/
│   │   └── main.py              # Loop principal do agente
│   ├── rag/
│   │   ├── ingest.py            # Pipeline de ingestão de documentos
│   │   └── retriever.py        # Recuperação híbrida BM25 + FAISS
│   ├── tools/
│   │   ├── rag_tool.py          # Ferramenta: busca RAG
│   │   ├── tasks_tool.py        # Ferramentas: tarefas (listar, adicionar)
│   │   └── learning_tool.py    # Ferramenta: iniciar quiz
│   ├── learning/
│   │   └── active_recall.py    # Módulo standalone de active recall
│   └── utils/
│       └── interceptor.py      # Decorator de logging de ferramentas
├── logs/
│   └── tool_calls.log           # Log automático de todas as chamadas
├── tests/                       # Pipeline de avaliação (a implementar)
├── .env                         # LIA_BASE_URL e JARVIS_API_KEY
├── requirements.txt
└── README.md
```

---

## 4. Convenções de Código

O projeto adota um conjunto rigoroso de convenções para garantir manutenibilidade e alinhamento com o ambiente de execução autônoma do LLM.

### Indexação 0-based estrita
Toda lógica computacional usa índice base zero sem exceção: contadores de loop (`for i in range(len(...))`), geração de IDs de chunks (`chunk_0000`, `chunk_0001`...`chunk_NNNN`), acesso a linhas do SQLite (`rows[i]`), e numeração das ferramentas no system prompt do agente.

### Separação de responsabilidades
As funções de ferramentas (`src/tools/`) são completamente **stateless**: recebem argumentos explícitos, executam uma única tarefa e retornam uma string. A infraestrutura pesada (ingestão, criação de índices) nunca interage com o runtime do agente.

### Padrão Interceptor
O logging de ferramentas **nunca é hardcoded** dentro da lógica de negócio. O decorator `@log_tool_call` intercepta as execuções de forma transparente, capturando `Tool Name`, `Input Parameters` e `Output`.

### Tratamento de erros recursivo
O loop do agente usa `try/except` não apenas para evitar crashes, mas para **realimentar estados de erro ao LLM**, permitindo autocorreção autônoma.

### Type hints e nomenclatura descritiva
Todas as assinaturas de função usam type hints (`query: str -> str`). Nomes são descritivos e explícitos (ex: `iniciar_quiz_active_recall` em vez de `quiz()`).

### Documentação bilíngue
Docstrings, prints de terminal e system prompts do LLM estão em **português**. Código Python (variáveis, funções, lógica) segue nomenclatura neutra/inglesa.

---

## 5. Módulos Implementados

### 5.1 Banco de Dados — `setup_db.py`

**Localização:** `database/setup_db.py`

Script de inicialização standalone que cria o arquivo `jarvis.db` com as tabelas necessárias. Deve ser executado uma única vez antes de iniciar o agente.

**Tabelas criadas:**

```sql
-- Tabela de tarefas
CREATE TABLE IF NOT EXISTS tarefas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao   TEXT NOT NULL,
    status      TEXT DEFAULT 'pendente',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de agenda
CREATE TABLE IF NOT EXISTS agenda (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo    TEXT NOT NULL,
    data_hora DATETIME NOT NULL,
    descricao TEXT
);
```

**Decisão de design:** o uso de SQLite (em substituição ao JSON inicial) garante integridade dos dados, prevenção de corrupção em acessos concorrentes e aplicação de schema estrito.

---

### 5.2 Ingestão de Documentos — `ingest.py`

**Localização:** `src/rag/ingest.py`

Pipeline responsável por converter PDFs em uma base de conhecimento consultável. Deve ser executado após popular o diretório `/data` e antes de iniciar o agente.

**Pipeline de execução:**

```
/data/*.pdf
    │
    ▼
[1] Docling: PDF → Markdown
    │
    ▼
[2] Chunking por parágrafo (split em "\n\n", mínimo 100 caracteres)
    │
    ▼
[3] Geração de chunks com ID global contínuo (chunk_0000...)
    + metadado "fonte" (nome do arquivo de origem)
    │
    ├──▶ [4] BM25Okapi → bm25_index.pkl
    │
    └──▶ [5] SentenceTransformer → FAISS IndexFlatIP
              → faiss_index.bin
              → embeddings_matrix.pkl
              → chunks.json
```

**Funções:**

| Função | Descrição |
|---|---|
| `tokenizar(texto)` | Tokenização por regex `\w+` em lowercase para o BM25 |
| `ingest_all_documents(data_dir, output_dir)` | Executa o pipeline completo sobre todos os PDFs do diretório |

**Artefatos gerados em `./database`:**

| Arquivo | Conteúdo |
|---|---|
| `chunks.json` | Lista de objetos `{id, texto, fonte}` |
| `bm25_index.pkl` | Índice BM25 serializado (pickle) |
| `faiss_index.bin` | Índice FAISS de produto interno |
| `embeddings_matrix.pkl` | Matriz numpy de embeddings normalizados |

---

### 5.3 Recuperação Híbrida — `retriever.py`

**Localização:** `src/rag/retriever.py`

Módulo stateless de busca que combina recuperação lexical (BM25) e semântica (FAISS) para retornar os chunks mais relevantes para uma consulta.

**Carregamento na inicialização do módulo:**
Os índices são carregados uma única vez no escopo global do módulo ao ser importado, evitando leituras repetidas de disco durante a execução do agente.

**Função principal:**

```python
def recuperar_hibrido(pergunta: str, k: int = 3, alpha: float = 0.6) -> str
```

**Algoritmo de fusão de scores:**

```
score_final = alpha * score_semantico + (1 - alpha) * score_bm25
```

Com `alpha = 0.6`, o sistema privilegia levemente a similaridade semântica sobre a correspondência lexical. Ambos os scores são normalizados com min-max antes da fusão.

**Saída:** string formatada com os `k` trechos mais relevantes, incluindo o índice 0-based e o nome do arquivo de origem (`fonte`), pronta para ser injetada no contexto do LLM.

**Funções auxiliares:**

| Função | Descrição |
|---|---|
| `tokenizar(texto)` | Tokenização para o BM25 (idêntica à do ingest) |
| `normalizar(v)` | Normalização min-max de vetores numpy |

---

### 5.4 Interceptor de Ferramentas — `interceptor.py`

**Localização:** `src/utils/interceptor.py`

Implementa o padrão **Decorator** para logging automático e transparente de toda chamada de ferramenta, sem inserir lógica de observabilidade dentro das próprias funções.

**Como usar:**

```python
from utils.interceptor import log_tool_call

@log_tool_call
def minha_ferramenta(argumento: str) -> str:
    ...
```

**O que é capturado em cada chamada:**

| Campo | Descrição |
|---|---|
| `Tool Name` | Nome da função decorada |
| `Input Parameters` | Args e kwargs recebidos |
| `Output` | Valor de retorno da função |
| Timestamp | Adicionado automaticamente pelo `logging` |

**Destino do log:** `logs/tool_calls.log` (criado automaticamente na raiz do projeto).

**Comportamento em erro:** se a ferramenta lançar uma exceção, o interceptor loga o erro com nível `ERROR` e re-lança a exceção, preservando o traceback original para o loop do agente tratar.

---

### 5.5 Ferramentas do Agente — `src/tools/`

#### `rag_tool.py` — `buscar_material_rag`

Wrapper stateless que expõe a recuperação híbrida do RAG como uma ferramenta chamável pelo agente.

```python
@log_tool_call
def buscar_material_rag(query: str) -> str
```

Chama `recuperar_hibrido(pergunta=query, k=3)` e retorna o contexto formatado.

---

#### `tasks_tool.py` — `listar_tarefas` e `adicionar_tarefa`

Ferramentas de gerenciamento de tarefas com persistência em SQLite.

```python
@log_tool_call
def listar_tarefas() -> str
```
Retorna todas as tarefas no formato `ID N: descrição [status]`, com verificação 0-based do array de resultados.

```python
@log_tool_call
def adicionar_tarefa(descricao: str) -> str
```
Insere uma nova tarefa com status padrão `pendente` e retorna confirmação textual.

Ambas usam um helper `get_connection()` para manter conexões SQLite limpas e isoladas por chamada.

---

#### `learning_tool.py` — `iniciar_quiz`

Ferramenta que seleciona um chunk aleatório e gera uma instrução de sistema para o LLM assumir a persona de tutor acadêmico.

```python
@log_tool_call
def iniciar_quiz() -> str
```

**Fluxo interno:**
1. Carrega `chunks.json`
2. Seleciona um chunk via `random.randrange(0, len(chunks))` (0-based)
3. Retorna uma instrução estruturada ao LLM com o texto base e diretrizes para formular uma pergunta, aguardar a resposta do usuário e avaliá-la

**Nota:** esta ferramenta não realiza chamadas ao LLM diretamente — ela injeta o contexto e as instruções no histórico de mensagens, deixando o agente principal conduzir a interação.

---

### 5.6 Active Recall — `active_recall.py`

**Localização:** `src/learning/active_recall.py`

Módulo standalone de aprendizado interativo. Pode ser executado diretamente pelo terminal (`python active_recall.py`) ou integrado ao agente. Realiza suas próprias chamadas ao LLM em duas fases distintas.

**Fluxo de execução:**

```
[1] Carrega chunks.json
[2] Seleciona chunk aleatório (índice 0-based)
    │
    ▼
[3] Fase 1 — Geração da Pergunta
    LLM recebe o trecho e gera UMA pergunta desafiadora
    (sem revelar a resposta)
    │
    ▼
[4] Input do usuário via terminal
    (comandos 'sair'/'cancelar'/'quit' encerram a sessão)
    │
    ▼
[5] Fase 2 — Avaliação da Resposta
    LLM recebe: pergunta original + trecho base + resposta do aluno
    Classifica como: Correta / Parcialmente Correta / Incorreta
    Fornece explicação construtiva
```

**Configuração:** utiliza `LIA_BASE_URL` e `JARVIS_API_KEY` via variáveis de ambiente (`.env`).

---

### 5.7 Loop do Agente — `main.py`

**Localização:** `src/agent/main.py`

Núcleo do sistema. Implementa um loop autônomo de raciocínio e ação baseado em **prompt-engineering**, contornando a restrição do servidor vLLM que bloqueia chamadas nativas de ferramentas (`400 BadRequestError`).

**Solução implementada (Prompt-Based Tool Calling):**

As definições de ferramentas são embutidas diretamente no system prompt como exemplos JSON numerados (0-based). O LLM é instruído a responder **exclusivamente** com o JSON da ferramenta quando precisar usá-la:

```
0: {"tool_call": "buscar_material_rag", "args": {"query": "..."}}
1: {"tool_call": "listar_tarefas", "args": {}}
2: {"tool_call": "adicionar_tarefa", "args": {"descricao": "..."}}
3: {"tool_call": "iniciar_quiz", "args": {}}
```

**Algoritmo do loop interno:**

```
enquanto True:
    │
    ▼
  Envia histórico de mensagens ao LLM
    │
    ▼
  Resposta contém JSON com "tool_call"?
    │
    ├── SIM ──▶ Extrai nome e args via regex
    │           Executa função Python correspondente
    │           Appenda resultado ao histórico
    │           Solicita: "resposta final ou próxima ferramenta"
    │           (volta ao início do loop interno)
    │
    └── NÃO ──▶ Exibe resposta em linguagem natural
                Appenda ao histórico
                Quebra loop interno (aguarda próximo input)
```

**Tratamento de erros:** falhas de `json.JSONDecodeError` são capturadas, transformadas em mensagem de erro e injetadas no histórico para que o agente possa tentar se autocorrigir.

**Ferramentas registradas:**

```python
available_functions = {
    "buscar_material_rag": buscar_material_rag,
    "listar_tarefas":      listar_tarefas,
    "adicionar_tarefa":    adicionar_tarefa,
    "iniciar_quiz":        iniciar_quiz,
}
```

---

## 6. Fluxo de Execução do Sistema

### Setup (uma vez)
```
python database/setup_db.py    # Cria jarvis.db com tabelas
python src/rag/ingest.py       # Processa PDFs e gera índices
```

### Runtime
```
python src/agent/main.py
```

```
Usuário digita input
        │
        ▼
Mensagem adicionada ao histórico
        │
        ▼
LLM processa histórico completo
        │
        ├── JSON detectado? ──▶ Ferramenta executada ──▶ Resultado ao histórico ──┐
        │                                                                          │
        │◀─────────────────────────────────────────────────────────────────────────┘
        │
        └── Texto natural? ──▶ Exibido ao usuário ──▶ Aguarda próximo input
```

---

## 7. Estratégia de Chunking e Impacto no RAG

### Estratégia adotada: Chunking por Parágrafo

O pipeline de ingestão divide os documentos usando `"\n\n"` como separador, que corresponde às quebras de parágrafo geradas pelo Docling ao converter PDFs para Markdown. Chunks com menos de 100 caracteres são descartados.

### Vantagens

- **Coerência semântica:** cada chunk preserva uma unidade temática completa, reduzindo a fragmentação de ideias entre trechos.
- **Compatibilidade com o modelo de embeddings:** o modelo `paraphrase-multilingual-MiniLM-L12-v2` tem melhor desempenho com textos de tamanho médio (50–300 tokens), alinhando-se bem ao tamanho típico de parágrafos acadêmicos.
- **Rastreabilidade:** o metadado `fonte` (nome do arquivo PDF) é preservado por chunk, permitindo ao LLM citar a origem exata do trecho recuperado.
- **Simplicidade e reprodutibilidade:** a estratégia é determinística e não requer bibliotecas adicionais de segmentação.

### Limitações e considerações

- **Parágrafos muito longos** (ex: listas densas ou blocos de código) podem exceder o contexto ideal para embeddings, diluindo a precisão da busca semântica.
- **Parágrafos muito curtos** que passam pelo filtro de 100 caracteres podem carregar contexto insuficiente para gerar respostas úteis.
- **Ausência de overlap:** a estratégia não implementa sobreposição entre chunks adjacentes, o que pode causar perda de contexto em conceitos que cruzam quebras de parágrafo.

### Possível evolução

Para maior robustez, uma estratégia de **chunking por janela deslizante** (ex: 512 tokens com 128 de overlap) poderia mitigar as limitações de parágrafos no limite. Isso se tornaria relevante especialmente se os documentos incluírem apostilas com formatação irregular.

---

## 8. Status de Implementação

| Componente | Status |
|---|---|
| Integração com LLM (LIA UFMS) | ✅ Concluído |
| Loop autônomo do agente (`main.py`) | ✅ Concluído |
| Workaround prompt-based tool calling | ✅ Concluído |
| Interceptor de logging (`@log_tool_call`) | ✅ Concluído |
| Banco de dados SQLite (`setup_db.py`) | ✅ Concluído |
| Pipeline de ingestão RAG (`ingest.py`) | ✅ Concluído |
| Recuperação híbrida BM25 + FAISS (`retriever.py`) | ✅ Concluído |
| `buscar_material_rag` | ✅ Concluído |
| `listar_tarefas` | ✅ Concluído |
| `adicionar_tarefa` | ✅ Concluído |
| `iniciar_quiz` (via agente) | ✅ Concluído |
| Active Recall standalone (`active_recall.py`) | ✅ Concluído |
| `consultar_agenda` | ⏳ Pendente |
| `concluir_tarefa(task_id)` | ⏳ Pendente |
| Feature de aprendizado secundária | ⏳ Pendente |
| Pipeline de avaliação (`tests/evaluate_rag.py`) | ⏳ Pendente |
| Framework de análise de erros | ⏳ Pendente |

---

## 9. Roadmap — Pendências

### Ferramentas restantes (2/5)

**`consultar_agenda()`**
Consultar eventos da tabela `agenda` no SQLite. Estrutura análoga à `listar_tarefas()`, retornando `título`, `data_hora` e `descrição` dos registros.

**`concluir_tarefa(task_id: int)`**
Atualizar o campo `status` de uma tarefa para `'concluída'` com base no `id` fornecido. Deve retornar erro descritivo se o ID não existir.

### Feature de aprendizado secundária

Sugestão: **gerador de recomendações de revisão** baseado em dificuldade. O sistema poderia rastrear quais chunks geraram respostas `Incorretas` ou `Parcialmente Corretas` no active recall e sugerir revisão proativa desses tópicos.

### Pipeline de avaliação — `tests/evaluate_rag.py`

Script que executa 10 perguntas acadêmicas predefinidas contra o RAG e loga para cada uma:
- Query enviada
- Chunks recuperados (com `fonte`)
- Resposta gerada pelo LLM
- Classificação manual: `correto` / `parcialmente correto` / `incorreto`

### Framework de análise de erros

Documentar em markdown (ex: `docs/error_analysis.md`) ao menos 3 falhas orgânicas do sistema, incluindo:
- `vLLM 400 BadRequestError` em chamadas nativas de ferramentas (causa + solução implementada)
- Falha de execução single-turn (agente responde sem aguardar resultado da ferramenta)
- Casos de alucinação ou resposta fora do contexto RAG

---

## 10. Configuração e Execução

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Variáveis de ambiente

Criar arquivo `.env` na raiz do projeto:

```env
LIA_BASE_URL=https://<endpoint-lia-ufms>
JARVIS_API_KEY=<sua-chave>
```

### Sequência de inicialização

```bash
# 1. Inicializar banco de dados
python database/setup_db.py

# 2. Popular /data com PDFs e executar ingestão
python src/rag/ingest.py

# 3. Iniciar o agente
python src/agent/main.py
```

### Executar active recall standalone

```bash
python src/learning/active_recall.py
```

### Comandos de saída do agente

Durante a conversa, os seguintes inputs encerram a sessão:

```
sair | exit | quit
```
