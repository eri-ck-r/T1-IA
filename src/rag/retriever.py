# src/rag/retriever.py
import json
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import regex as re
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[2] / "database"

# Esses arquivos agora contêm a base de conhecimento global (todos os PDFs)
with open(DB_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(DB_DIR / "bm25_index.pkl", "rb") as f:
    indice_bm25 = pickle.load(f)

with open(DB_DIR / "embeddings_matrix.pkl", "rb") as f:
    matriz_emb = pickle.load(f)

indice_faiss = faiss.read_index(str(DB_DIR / "faiss_index.bin"))
modelo_embed = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


def tokenizar(texto):
    return re.findall(r"\w+", texto.lower())


def normalizar(v):
    v = np.array(v, dtype="float32")
    delta = float(v.max() - v.min())
    if delta < 1e-9: return np.zeros_like(v)
    return (v - v.min()) / delta


def recuperar_hibrido(pergunta: str, k: int = 3, alpha: float = 0.6) -> str:
    """Combina BM25 e Semântico, retornando uma string formatada para o LLM."""
    sb = normalizar(indice_bm25.get_scores(tokenizar(pergunta)))
    q = modelo_embed.encode([pergunta], normalize_embeddings=True).astype("float32")
    sd = normalizar(np.dot(matriz_emb, q[0]))

    score_final = alpha * sd + (1.0 - alpha) * sb
    idx = np.argsort(score_final)[::-1][:k]

    docs_recuperados = [chunks[i] for i in idx]

    # Formatação atualizada: Mantendo a indexação 0-based e expondo a FONTE
    contexto = "\n\n".join(
        [f"Trecho {i} (Fonte: {d['fonte']}):\n{d['texto']}" for i, d in enumerate(docs_recuperados)]
    )

    return contexto