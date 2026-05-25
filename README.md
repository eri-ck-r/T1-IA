# Autores: Erick Rodrigues e Maryana Silva

# Link do video: https://youtu.be/SzmRGVDuyzs
# Como rodar o código:

### Crie um ambiente virtual para o python: 
```bash
python -m venv .venv
```
### Ative o ambiente virtual

Windows:
```bash
.venv/Scripts/activate
```
Linux/Mac:
```bash
source .venv/bin/activate
```
### Instale as dependências
```bash
pip install -r requirements.txt
```

### Na primeira vez rodando o código, é necessário criar o database, e construir os índices do RAG:
```bash
python database/setup_db.py
python src/rag/ingest.py
```

### Criando o arquivo .env
O projeto requer o URL do LIA e a chave da API para acessar o modelo Gemma 3 12B. Essas credenciais devem ser armazenadas em um arquivo `.env` na raiz do projeto.

Na raiz do projeto (`T1-IA/`), crie um arquivo chamado `.env` com o seguinte conteúdo, fornecido no AVA:

```env
LIA_URL={url do lia}
GEMMA_API_KEY={chave do gemma}
```
### Inicie a API do Jarvis:
```bash
uvicorn api:app --reload
```

## Agora, é só abrir o arquivo `/chat/chatJarvis.html` no seu navegador, e pronto!

# IAs utilizadas:
Gemini para auxiliar no desenvolvimento, documentação e design da arquitetura;

Claude para fazer a parte da API para a interface web, e a interface web.

    
# Dataset
O dataset foi composto principalmente por slides de aulas, artigos científicos e livros de programação competitiva.

As limitações dos datasets foram, principalmente, predominância de imagens e fórmulas, no qual o Docling têm dificuldades em converter de forma 100% estruturada

| Nome do PDF                 | Tipo de Documento | Limitações Identificadas                                                                                | Chunking Aplicado |
|-----------------------------|-------------------|---------------------------------------------------------------------------------------------------------|-------------------|
| Artigo_RUP                  | Artigo            | Parágrafos curtos, muita teoria                                                                         | Parágrafo         |
| aula-knn                    | Slides de Aula    | Paragrafos curtos                                                                                       | Parágrafo         |
| bfs-notes                   | Livro             | Muito código inline e figuras                                                                           | Parágrafo         |
| floyd_warshall              | Livro             | Paragrafos curtos e muito LaTEX                                                                         | Parágrafo         |
| IoT                         | Livro             | Ideias extensas para a classificação dos chunks                                                         | Parágrafo         |
| modular                     | Livro             | Notação matemática densa                                                                                | Parágrafo         |
| progparalela                | Artigo            | Esse até que foi ok, mas ele teve dificuldade com o código                                              | Parágrafo         |
| Sieve                       | Livro             | LaTEX                                                                                                   | Parágrafo         |
| Software-Defined Networking | Artigo            | Arquivo grande comparado com os outros, e imagens grandes, que o RapidOCR teve dificuldade em converter | Parágrafo         |
| VNS                         | Artigo            | Figuras e Tabelas                                                                                       | Parágrafo         |    

# Melhorias para a parte 2 do trabalho:
Uma forma de adicionar dinâmicamente as fontes de dados, e alterar a estratégia de chunking para cada uma, já que são diferentes, e nesse trabalho foi utilizada só a estratégia de chunking por parágrafo.
