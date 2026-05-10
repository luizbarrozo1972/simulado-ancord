# Enriquece _questions_topinvest.json com justificationText via RAG local + OpenAI Chat.
# Pré-requisitos: índice em .rag/ (python _rag_local.py build ... com embeddings) e OPENAI_API_KEY.
import argparse
import json
import os
import shutil
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
QUESTIONS_PATH = ROOT / "_questions_topinvest.json"

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

try:
    from _rag_local import search as rag_search
except ImportError:  # execução fora da pasta do repo
    import sys

    sys.path.insert(0, str(ROOT))
    from _rag_local import search as rag_search


SYSTEM_PROMPT = """És um assistente para preparação à prova ANCORD.
REGRAS OBRIGATÓRIAS:
1) Usa APENAS informação presente no CONTEXTO fornecido (trechos do material). Não inventes artigos, leis ou órgãos que não apareçam no contexto.
2) Escreve em português do Brasil, 2 a 5 frases, tom objetivo.
3) Explica só porque a alternativa marcada como correta está certa em relação ao contexto.
4) Se o contexto NÃO permitir fundamentar a resposta com segurança, responde EXACTAMENTE uma linha começando por: INSUFICIENTE:
5) Sem markdown, sem listas numeradas, sem citar "o contexto diz" de forma vaga — integra a ideia de forma direta."""


def build_user_prompt(question: dict, context_blocks: str) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lines = [f"CONTEXTO (material de estudo):\n\n{context_blocks}"]
    lines.append("\n---\n")
    lines.append("QUESTÃO:\n" + question["q"].strip())
    lines.append("\nALTERNATIVAS:")
    for i, opt in enumerate(question["options"]):
        lines.append(f"{letters[i]}) {opt}")
    ci = int(question["correct"])
    cor = letters[ci] + ") " + question["options"][ci]
    lines.append("\nALTERNATIVA CORRETA (gabarito): " + cor)
    lines.append(
        "\n\nRedige a justificativa segundo as regras do sistema. "
        "Se no contexto não houver base suficiente, usa só a linha INSUFICIENTE: ..."
    )
    return "\n".join(lines)


def format_rag_hits(hits: list[dict]) -> str:
    parts = []
    for h in hits:
        score = h.get("score", 0)
        parts.append(f"[página ~{h['page']}, relevância {score:.3f}]\n{h['text'].strip()}")
    return "\n\n".join(parts)


def call_chat(system: str, user: str, model: str, temperature: float) -> str:
    client = OpenAI()
    r = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (r.choices[0].message.content or "").strip()


def should_skip_existing(q: dict, force: bool) -> bool:
    if not force and q.get("justificationText"):
        t = q["justificationText"]
        if isinstance(t, str) and t.strip():
            return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Gera justificationText no JSON usando .rag/ + OpenAI Chat"
    )
    ap.add_argument(
        "--questions",
        type=Path,
        default=QUESTIONS_PATH,
        help="JSON de questões Top Invest (default: _questions_topinvest.json)",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Onde gravar (default: sobrescreve --questions)",
    )
    ap.add_argument("--rag-k", type=int, default=6, help="Trechos RAG por questão")
    ap.add_argument(
        "--model",
        default=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        help="Modelo chat (ou env OPENAI_CHAT_MODEL)",
    )
    ap.add_argument("--temperature", type=float, default=0.25)
    ap.add_argument(
        "--force",
        action="store_true",
        help="Regenera mesmo quando já existe justificationText",
    )
    ap.add_argument("--limit", type=int, default=0, help="Processar só as N primeiras (0=todas)")
    ap.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Pausa em segundos entre chamadas à API",
    )
    ap.add_argument(
        "--allow-insufficient",
        action="store_true",
        help="Gravar mesmo quando o modelo devolver linha INSUFICIENTE:",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Não chama API nem grava ficheiro; mostra 1 exemplo",
    )
    ap.add_argument("--no-backup", action="store_true", help="Não criar .bak antes de gravar")
    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Defina OPENAI_API_KEY no ambiente.")

    path_in = args.questions
    path_out = args.output or path_in
    if not path_in.is_file():
        raise SystemExit(f"Ficheiro não encontrado: {path_in}")

    with open(path_in, encoding="utf-8") as f:
        questions: list = json.load(f)

    if args.dry_run:
        q = questions[0]
        try:
            hits = rag_search(q["q"][:500], k=args.rag_k)
        except Exception as e:
            raise SystemExit(
                f"RAG indisponível ({e}). Monte o índice: python _rag_local.py build --pdf <PDF> ..."
            ) from e
        ctx = format_rag_hits(hits)
        user = build_user_prompt(q, ctx)
        print("=== Exemplo de prompt (primeira questão, truncado) ===\n")
        print(user[:4000])
        if len(user) > 4000:
            print("\n... [truncado]")
        print("\n(dry-run: sem chamada ao Chat)")
        return

    n_done = 0
    n_skip = 0
    n_fail = 0
    lim = args.limit if args.limit > 0 else len(questions)

    for idx, q in enumerate(questions):
        if idx >= lim:
            break
        qid = q.get("id", idx + 1)
        if should_skip_existing(q, args.force):
            n_skip += 1
            continue

        query = q["q"].strip()
        # Reforço semântico com palavras-chave da alternativa correta
        ci = int(q["correct"])
        query = query + " " + q["options"][ci][:280]

        try:
            hits = rag_search(query, k=args.rag_k)
        except Exception as e:
            print(f"id {qid}: ERRO RAG — {e}")
            n_fail += 1
            continue

        ctx = format_rag_hits(hits)
        user = build_user_prompt(q, ctx)

        try:
            text = call_chat(SYSTEM_PROMPT, user, args.model, args.temperature)
        except Exception as e:
            print(f"id {qid}: ERRO API — {e}")
            n_fail += 1
            continue

        if text.upper().startswith("INSUFICIENTE:") and not args.allow_insufficient:
            print(f"id {qid}: omitido (INSUFICIENTE sem --allow-insufficient)")
            n_fail += 1
            continue

        q["justificationText"] = text
        n_done += 1
        print(f"id {qid}: OK ({len(text)} chars)")

        if args.sleep > 0:
            time.sleep(args.sleep)

    print(f"\nResumo: gravadas={n_done}, ignoradas(já preenchidas)={n_skip}, falhas/omitidas={n_fail}")

    if n_done == 0:
        print("Nada a gravar.")
        return

    if not args.no_backup and path_out == path_in and path_in.exists():
        bak = path_in.with_suffix(path_in.suffix + ".bak")
        shutil.copy2(path_in, bak)
        print(f"Cópia de segurança: {bak}")

    tmp = path_out.with_suffix(".tmp.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    tmp.replace(path_out)
    print(f"Gravado: {path_out}")


if __name__ == "__main__":
    main()
