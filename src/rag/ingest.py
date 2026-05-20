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

def ingest_documents(pdf_path: str, output_dir: str = "./database"):
    print(f"Processando: {pdf_path}")
    
    # 1. Converter PDF para Markdown
    converter = DocumentConverter()
    resultado = converter.convert(pdf_path)
    texto_markdown = resultado.document.export_to_markdown()
    
    # 2. Chunking (Estratégia: Parágrafo)
    paragrafos = [p.strip() for p in texto_markdown.split("\n\n")]
    chunks_filtrados = [p for p in paragrafos if len(p) >= 100]
    
    # Mantendo estritamente a indexação baseada em 0
    chunks = [{"id": f"chunk_{i:04d}", "texto": texto} for i, texto in enumerate(chunks_filtrados)]
    
    # 3. Criar e Salvar Índice BM25
    corpus_tokenizado = [tokenizar(c["texto"]) for c in chunks]
    indice_bm25 = BM25Okapi(corpus_tokenizado)
    
    # 4. Criar e Salvar Índice FAISS (Embeddings)
    modelo_embed = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in chunks]
    matriz_emb = modelo_embed.encode(textos, normalize_embeddings=True).astype("float32")
    
    dim = matriz_emb.shape[1]
    indice_faiss = faiss.IndexFlatIP(dim)
    indice_faiss.add(matriz_emb)
    
    # 5. Salvar artefatos no disco
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(f"{output_dir}/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
        
    with open(f"{output_dir}/bm25_index.pkl", "wb") as f:
        pickle.dump(indice_bm25, f)
        
    faiss.write_index(indice_faiss, f"{output_dir}/faiss_index.bin")
    
    # Salvar a matriz de embeddings para a busca híbrida
    with open(f"{output_dir}/embeddings_matrix.pkl", "wb") as f:
        pickle.dump(matriz_emb, f)

    print("Ingestão concluída e índices salvos no disco.")

if __name__ == "__main__":
    ingest_documents("./data/VNS.pdf")