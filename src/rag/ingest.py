# src/rag/ingest.py
import json
import pickle
import faiss
from pathlib import Path
from docling.document_converter import DocumentConverter
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import regex as re


def tokenizar(texto):
    return re.findall(r"\w+", texto.lower())


def ingest_all_documents(data_dir: str = "./data", output_dir: str = "./database"):
    data_path = Path(data_dir)
    # Encontra todos os arquivos .pdf no diretório
    pdf_files = list(data_path.glob("*.pdf"))

    if len(pdf_files) == 0:
        print(f"Nenhum arquivo PDF encontrado na pasta: {data_dir}")
        return

    converter = DocumentConverter()
    all_chunks = []
    global_chunk_index = 0

    print(f"Iniciando varredura de {len(pdf_files)} arquivos...")

    # Itera sobre o array de arquivos
    for i in range(len(pdf_files)):
        pdf_path = pdf_files[i]
        print(f"[{i}] Processando: {pdf_path.name}")

        # 1. Converter PDF para Markdown
        resultado = converter.convert(str(pdf_path))
        texto_markdown = resultado.document.export_to_markdown()

        # 2. Chunking (Estratégia: Parágrafo)
        paragrafos = [p.strip() for p in texto_markdown.split("\n\n")]
        chunks_filtrados = [p for p in paragrafos if len(p) >= 100]

        # 3. Adicionar aos chunks globais com indexação contínua
        for j in range(len(chunks_filtrados)):
            all_chunks.append({
                "id": f"chunk_{global_chunk_index:04d}",
                "texto": chunks_filtrados[j],
                "fonte": pdf_path.name  # Metadado crucial para o RAG saber a origem
            })
            global_chunk_index += 1

    print(f"\nTotal de {len(all_chunks)} chunks extraídos. Gerando índices...")

    # 4. Criar e salvar Índice BM25
    corpus_tokenizado = [tokenizar(c["texto"]) for c in all_chunks]
    indice_bm25 = BM25Okapi(corpus_tokenizado)

    # 5. Criar e Salvar Índice FAISS (Embeddings)
    print("Calculando embeddings semânticos (isso pode levar alguns minutos)...")
    modelo_embed = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in all_chunks]
    matriz_emb = modelo_embed.encode(textos, normalize_embeddings=True).astype("float32")

    dim = matriz_emb.shape[1]
    indice_faiss = faiss.IndexFlatIP(dim)
    indice_faiss.add(matriz_emb)

    # 6. Salvar artefatos no disco
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open(f"{output_dir}/chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False)

    with open(f"{output_dir}/bm25_index.pkl", "wb") as f:
        pickle.dump(indice_bm25, f)

    faiss.write_index(indice_faiss, f"{output_dir}/faiss_index.bin")

    with open(f"{output_dir}/embeddings_matrix.pkl", "wb") as f:
        pickle.dump(matriz_emb, f)

    print("\nIngestão concluída e índices salvos no disco com sucesso.")


if __name__ == "__main__":
    ingest_all_documents()