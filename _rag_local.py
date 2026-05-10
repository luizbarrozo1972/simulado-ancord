# Índice RAG local em disco: chunks de texto + embeddings (opcional via OpenAI).
# Saída em .rag/ — não versionar (ver .gitignore).
import argparse
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RAG_DIR = ROOT / ".rag"

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass
MANIFEST_NAME = "manifest.json"
CHUNKS_NAME = "chunks.json"
EMB_NAME = "embeddings.npz"


def extract_pages_text(pdf_path: Path, page_from: int, page_to: int) -> list[tuple[int, str]]:
    """Extrai texto por página. page_from/page_to são 1-based (como no PDF)."""
    import pdfplumber

    out: list[tuple[int, str]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        n = len(pdf.pages)
        for p1 in range(page_from, page_to + 1):
            idx = p1 - 1
            if idx < 0 or idx >= n:
                continue
            t = pdf.pages[idx].extract_text() or ""
            out.append((p1, t.strip()))
    return out


def chunk_pages(
    pages: list[tuple[int, str]],
    max_chars: int = 1200,
    overlap: int = 200,
) -> list[dict]:
    """Fatia o texto por página; páginas longas são divididas com sobreposição."""
    chunks: list[dict] = []
    cid = 0
    ov = min(overlap, max_chars // 2) if max_chars > 2 else 0
    step = max(1, max_chars - ov)
    for page_num, text in pages:
        if not text:
            continue
        if len(text) <= max_chars:
            chunks.append({"id": cid, "page": page_num, "text": text})
            cid += 1
            continue
        start = 0
        while start < len(text):
            piece = text[start : start + max_chars]
            chunks.append({"id": cid, "page": page_num, "text": piece})
            cid += 1
            start += step
    return chunks


def _normalize_rows(a: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(a, axis=1, keepdims=True)
    n = np.maximum(n, 1e-12)
    return a / n


def embed_texts_openai(texts: list[str], model: str = "text-embedding-3-small") -> np.ndarray:
    """Embeddings via API OpenAI (requer OPENAI_API_KEY no ambiente)."""
    from openai import OpenAI

    client = OpenAI()
    out_vecs: list[list[float]] = []
    batch = 64
    for i in range(0, len(texts), batch):
        sub = texts[i : i + batch]
        r = client.embeddings.create(model=model, input=sub)
        # API devolve na mesma ordem dos inputs
        data = sorted(r.data, key=lambda d: d.index)
        for row in data:
            out_vecs.append(row.embedding)
    return np.array(out_vecs, dtype=np.float32)


def build_index(
    pdf_path: Path,
    page_from: int,
    page_to: int,
    max_chars: int = 1200,
    overlap: int = 200,
    embedding_model: str = "text-embedding-3-small",
    skip_embeddings: bool = False,
) -> dict:
    """Constrói chunks.json (+ embeddings.npz se houver API key e não skip)."""
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    pages = extract_pages_text(pdf_path, page_from, page_to)
    chunks = chunk_pages(pages, max_chars=max_chars, overlap=overlap)
    texts = [c["text"] for c in chunks]

    manifest = {
        "pdf": str(pdf_path.resolve()),
        "page_from": page_from,
        "page_to": page_to,
        "num_chunks": len(chunks),
        "max_chars": max_chars,
        "overlap": overlap,
        "embedding_model": embedding_model,
        "has_embeddings": False,
    }

    with open(RAG_DIR / CHUNKS_NAME, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    emb_path = RAG_DIR / EMB_NAME
    if emb_path.exists():
        emb_path.unlink()

    if not skip_embeddings and os.environ.get("OPENAI_API_KEY"):
        emb = embed_texts_openai(texts, model=embedding_model)
        np.savez_compressed(RAG_DIR / EMB_NAME, embeddings=emb)
        manifest["has_embeddings"] = True
        manifest["embedding_dim"] = int(emb.shape[1])

    with open(RAG_DIR / MANIFEST_NAME, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest


def load_store() -> tuple[dict, list[dict], np.ndarray | None]:
    """Carrega manifest, chunks e embeddings (se existirem)."""
    mf = RAG_DIR / MANIFEST_NAME
    cf = RAG_DIR / CHUNKS_NAME
    ef = RAG_DIR / EMB_NAME
    if not mf.exists() or not cf.exists():
        raise FileNotFoundError(
            f"Índice não encontrado em {RAG_DIR}. Rode: python _rag_local.py build ..."
        )
    with open(mf, encoding="utf-8") as f:
        manifest = json.load(f)
    with open(cf, encoding="utf-8") as f:
        chunks = json.load(f)
    emb = None
    if ef.exists():
        z = np.load(ef)
        emb = z["embeddings"].astype(np.float32)
    return manifest, chunks, emb


def search(query: str, k: int = 5) -> list[dict]:
    """Top-k chunks por similaridade coseno (precisa de embeddings.npz)."""
    manifest, chunks, emb = load_store()
    if emb is None:
        raise RuntimeError(
            "Sem embeddings no disco. Defina OPENAI_API_KEY e rode o build sem --skip-embeddings."
        )
    q = embed_texts_openai([query], model=manifest.get("embedding_model", "text-embedding-3-small"))[
        0
    ]
    q = q.astype(np.float32)
    q = q / max(np.linalg.norm(q), 1e-12)
    E = _normalize_rows(emb)
    sims = E @ q
    idx = np.argsort(-sims)[:k]
    out = []
    for i in idx:
        c = chunks[int(i)].copy()
        c["score"] = float(sims[int(i)])
        out.append(c)
    return out


def cmd_build(args: argparse.Namespace) -> None:
    pdf = Path(args.pdf)
    if not pdf.is_file():
        raise SystemExit(f"PDF não encontrado: {pdf}")
    skip_emb = args.skip_embeddings or not os.environ.get("OPENAI_API_KEY")
    if skip_emb and not args.skip_embeddings:
        print("OPENAI_API_KEY não definida: gravando só chunks.json (sem embeddings.npz).")
    m = build_index(
        pdf,
        args.page_from,
        args.page_to,
        max_chars=args.max_chars,
        overlap=args.overlap,
        embedding_model=args.embedding_model,
        skip_embeddings=skip_emb,
    )
    print(f"Índice em {RAG_DIR}")
    print(json.dumps(m, ensure_ascii=False, indent=2))


def cmd_search(args: argparse.Namespace) -> None:
    for r in search(args.query, k=args.k):
        print(f"--- p.{r.get('page')} score={r.get('score', 0):.4f} ---")
        print(r["text"][:2000])
        if len(r["text"]) > 2000:
            print("...")


def cmd_info(_: argparse.Namespace) -> None:
    mf = RAG_DIR / MANIFEST_NAME
    if not mf.exists():
        print(f"Sem índice em {RAG_DIR}")
        return
    with open(mf, encoding="utf-8") as f:
        print(json.dumps(json.load(f), ensure_ascii=False, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description="RAG local (.rag/) para material em PDF")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Extrai páginas, gera chunks e opcionalmente embeddings")
    b.add_argument("--pdf", type=str, required=True, help="Caminho do PDF")
    b.add_argument("--page-from", type=int, default=23)
    b.add_argument("--page-to", type=int, default=57)
    b.add_argument("--max-chars", type=int, default=1200)
    b.add_argument("--overlap", type=int, default=200)
    b.add_argument(
        "--embedding-model",
        type=str,
        default="text-embedding-3-small",
    )
    b.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Só gera chunks.json (sem chamar API)",
    )
    b.set_defaults(func=cmd_build)

    s = sub.add_parser("search", help="Busca por similaridade (requer embeddings)")
    s.add_argument("query", type=str)
    s.add_argument("-k", type=int, default=5)
    s.set_defaults(func=cmd_search)

    i = sub.add_parser("info", help="Mostra manifest do índice")
    i.set_defaults(func=cmd_info)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
