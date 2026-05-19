# OBJETIVO


Desenvolver um assistente pessoal acadêmico (JARVIS) capaz de ajudar estudantes a organizar e melhorar seu desempenho utilizando técnicas modernas de Inteligência Artificial.

O sistema deverá integrar:

-   RAG (Retrieval-Augmented Generation)
    
-   Tool Calling (chamada de ferramentas)
    
-   Um modelo de linguagem (LLM)
    

A LLM obrigatória será o Gemma 12B, acessado por meio do token fornecido pelo professor.

O objetivo não é apenas construir um sistema funcional, mas desenvolver um sistema que:

-   apoie o aprendizado do usuário
    
-   integre múltiplas fontes de informação
    
-   permita avaliação crítica do seu comportamento

# FUNCIONALIDADES OBRIGATÓRIAS

1.1 Consulta a materiais de estudo (RAG)

O usuário deve conseguir fazer perguntas sobre materiais (PDFs, textos, anotações), por exemplo:

-   “Explique regressão logística”
    
-   “Resuma o conteúdo sobre embeddings”
    
-   “Quais são os principais pontos do material X?”
    

O sistema deve:

-   carregar documentos
    
-   dividir em chunks
    
-   gerar embeddings
    
-   recuperar trechos relevantes
    
-   gerar respostas baseadas nesses trechos

1.2 Agenda acadêmica

O sistema deve permitir consultas como:

-   “O que tenho hoje?”
    
-   “Quais são minhas aulas esta semana?”
    
-   “Tenho prova amanhã?”
    

A agenda pode ser armazenada localmente (JSON, CSV ou SQLite).

1.3 Lista de tarefas

O sistema deve permitir:

-   adicionar tarefa
    
-   listar tarefas
    
-   marcar tarefa como concluída

## TOOL CALLING

O sistema deve implementar pelo menos 5 ferramentas, por exemplo:

-   consultar_agenda
    
-   listar_tarefas
    
-   adicionar_tarefa
    
-   concluir_tarefa
    
-   buscar_material_rag
    

Requisitos:

-   A decisão de chamada deve ser feita pela LLM (não apenas lógica fixa)
    
-   O sistema deve registrar logs com:
    
    -   ferramenta chamada
        
    -   entrada
        
    -   saída

## MELHORIAS DE APRENDIZADO

O sistema deve implementar pelo menos 2 funcionalidades voltadas ao aprendizado.

Exemplos:

-   geração de exercícios
    
-   perguntas ao usuário (active recall)
    
-   identificação de dificuldades
    
-   recomendação de revisão
    

Requisito mínimo:

-   pelo menos uma funcionalidade deve ser interativa (o sistema pergunta e avalia)
- 
## AVALIAÇÃO DO SISTEMA

O grupo deve avaliar o sistema com pelo menos 10 perguntas.

Para cada pergunta:

-   pergunta
    
-   documentos recuperados
    
-   resposta
    
-   classificação:
    
    -   correta
        
    -   parcialmente correta
        
    -   incorreta

## ANÁLISE DE ERROS

Identificar pelo menos 3 falhas.

Para cada falha:

-   tipo (recuperação, geração, ambiguidade, etc.)
    
-   causa
    
-   possível solução

## DATASET

Requisitos:

-   mínimo de 10 documentos
    
-   conteúdo acadêmico
    
-   qualidade suficiente para perguntas
    

Deve incluir:

-   origem dos dados
    
-   tipo de conteúdo
    
-   limitações
    

Entrega:

-   pasta /data no repositório ou link externo
    

Explicar:

-   estratégia de chunking
    
-   impacto no RAG


## QUALIDADE DE ENGENHARIA DE SOFTWARE


O projeto deve demonstrar:

-   organização do código
    
-   separação de responsabilidades
    
-   testes básicos
    
-   tratamento de erros
    
-   logs


Uso de IA para:

-   revisão
    
-   sugestão de melhorias
    
-   identificação de bugs
    

O aluno deve conseguir explicar o código.

# TECNOLOGIAS E RESTRIÇÕES
O trabalho deve ser desenvolvido de modo que o grupo tenha controle sobre o sistema implementado.

Diretrizes:

-   ferramentas gratuitas são permitidas
    
-   o grupo deve implementar explicitamente:
    
    -   RAG
        
    -   integração com LLM
        
    -   tool calling
        

LLM obrigatória:

-   Gemma 12B
    

Regras:

-   não utilizar ferramentas que gerem o sistema completo automaticamente (ver seção 13)
    
-   ferramentas de apoio ao desenvolvimento são permitidas
    

O acesso a LLM pode ser feita pela API

```
from openai import OpenAI

client = OpenAI(base_url='LINK Q TA NO AVA', api_key='CHAVE Q TA NO AVA')
resp = client.chat.completions.create(
    model='google/gemma-3-12b-it',
    messages=[{'role': 'user', 'content': 'Hi'}],
)
print(resp.choices[0].message.content)
```

----------

# USO DE IA PARA DESENVOLVIMENTO
Permitido e incentivado.

Requisitos:

-   entender o código
    
-   listar ferramentas usadas no README
    
-   estar preparado para explicar o sistema

# ENTREGA

12.1 Código

-   repositório GitHub
    
-   README com instruções
    
-   lista de IAs utilizadas
    

12.2 Dataset

-   mínimo 10 documentos
    
-   pasta /data ou link
    
-   documentação com:
    
    -   origem
        
    -   tipo
        
    -   limitações
        
    -   chunking
        

Não entregar itens obrigatórios = nota zero

# CRITERIOS DE AVALIAÇÃO

Funcionalidade: 20%  
RAG: 20%  
Tool calling: 15%  
Avaliação + erros: 20%  
Aprendizado: 15%  
Engenharia: 10%

Cada dia de atraso na entrega, incorre na perda de 1 ponto por dia.

----------

# DIFERENCIAL
    

-   interface gráfica
    
-   melhor qualidade
    
-   melhorias avançadas
    
-   integração mais inteligenteCaso o professor entenda que houve diferenciais do grupo, ou que o grupo fez algo além do pedido, o grupo poderá receber bônus de até 2 pontos.
