# Extrai todos os blocos N.M. SIMULADO do PDF Top Invest e o gabarito seguinte.
# Gabarito: após "Justificativa:", extrai o texto explicativo do PDF e a URL (complemento).
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "Material_TopInvest_AI-da-Ancord.pdf"
OUT = ROOT / "_questions_topinvest.json"

LET = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}


def full_text(pdf):
    parts = []
    for i, p in enumerate(pdf.pages):
        t = p.extract_text() or ""
        parts.append(f"\n__P{i}__\n{t}")
    return "\n".join(parts)


def iter_sections(blob: str):
    sim_re = re.compile(r"(\d+\.\d+)\.\s*SIMULADO", re.IGNORECASE)
    gab_re = re.compile(r"(\d+\.\d+)\.\s*GABARITO", re.IGNORECASE)
    pos = 0
    while True:
        sm = sim_re.search(blob, pos)
        if not sm:
            break
        sec = sm.group(1)
        gm = gab_re.search(blob, sm.end())
        if not gm:
            break
        next_sim = sim_re.search(blob, gm.end())
        gab_end = next_sim.start() if next_sim else len(blob)
        body = blob[sm.end() : gm.start()]
        gab_block = blob[gm.start() : gab_end]
        yield sec, body, gab_block
        pos = gab_end


def clean_pdf_glue(s: str) -> str:
    s = re.split(r"__P\d+__", s)[0]
    s = re.sub(r"\s+\d{1,3}\s*$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def parse_question_header(ch: str):
    """Vários formatos do PDF Top Invest."""
    ch = ch.strip()
    patterns = [
        r"(\d+)\.\s*#(\d+)\s*-\s*(.*)",
        r"(\d+)\s*-\s*#(\d+)\s*-\s*(.*)",
        r"(\d+)\s*-\s*#(\d+)\.(.*)",
        r"(\d+)\.#(\d+)\s*-\s*(.*)",
        r"(\d+)\.(\d{4,})\s*-\s*(.*)",
    ]
    for pat in patterns:
        m = re.match(pat, ch, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1), m.group(2), m.group(3)
    return None


def question_starts(text: str):
    pos = set()
    patterns = [
        r"(?:^|\n)\s*(\d+)\.\s*#(\d+)\s*-\s*",
        r"(?:^|\n)\s*(\d+)\s*-\s*#(\d+)\s*-\s*",
        r"(?:^|\n)\s*(\d+)\s*-\s*#(\d+)\.",
        r"(?:^|\n)\s*(\d+)\.#(\d+)\s*-\s*",
        r"(?:^|\n)\s*(\d+)\.(\d{4,})\s*-\s*",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            pos.add(m.start())
    return sorted(pos)


def parse_questions_block(text: str):
    text = re.sub(r"__P\d+__", " ", text)
    cut = re.search(
        r"(?:^|\n)\s*1(?:\.|\s*-)\s*#\d+", text
    )
    if cut:
        text = text[cut.start() + 1 :]

    starts = question_starts(text)
    chunks = []
    for i, st in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        chunks.append(text[st:end].strip())

    out = []
    opt_split = re.compile(
        r"(?=^(?:\([a-e]\)|[a-e]\))\s*)",
        re.MULTILINE | re.IGNORECASE,
    )

    for ch in chunks:
        mh = parse_question_header(ch)
        if not mh:
            continue
        num, ref, body = mh
        parts = opt_split.split(body)
        stem = clean_pdf_glue(parts[0])
        opts = []
        for p in parts[1:]:
            mm = re.match(
                r"^(?:([a-e])\)|\(([a-e])\))\s*(.*)$",
                p.strip(),
                re.DOTALL | re.IGNORECASE,
            )
            if mm:
                opts.append(clean_pdf_glue(mm.group(3)))
        if len(opts) < 4 or len(opts) > 5:
            continue
        out.append({"n_local": int(num), "ref": ref, "q": stem, "options": opts})
    return out


def parse_gabarito_block(text: str):
    answers = {}
    for m in re.finditer(
        r"(\d+)\s*-\s*Resposta[s]?\s*:\s*([A-E]+)([A-E])?",
        text,
        re.IGNORECASE,
    ):
        n = int(m.group(1))
        raw = m.group(2).upper()
        letter = raw[0] if raw else ""
        extra = m.group(3)
        if extra:
            answers[n] = LET[letter]
        elif letter in LET:
            answers[n] = LET[letter]
    return answers


def normalize_gabarito_urls_blob(text: str) -> str:
    """Corrige quebras de linha no meio de URLs e variantes '5-Resposta'."""
    t = text
    t = re.sub(r"(?m)^(\d+)\s*-\s*Resposta", r"\1 - Resposta", t)
    t = re.sub(
        r"(https?://simulados\.topinvest\.com\.br/simulados/)\s*\n\s*(\d+/iniciar[^\s<>]*)",
        r"\1\2",
        t,
        flags=re.IGNORECASE,
    )
    return t


def parse_justification_urls(text: str) -> dict[int, str]:
    """URLs após 'Justificativa:' no gabarito Top Invest (material PDF)."""
    urls = {}
    blob = normalize_gabarito_urls_blob(text)
    pat = re.compile(
        r"(?m)^(\d+)\s*-\s*Resposta[s]?\s*:\s*[A-E]+\.\s*Justificativa:\s*(?:\r\n|\n|\r)\s*(?:<)?(https?://[^\s<>]+)>?",
        re.IGNORECASE,
    )
    for m in pat.finditer(blob):
        urls[int(m.group(1))] = m.group(2).strip()
    # Alguns PDFs colam Justificativa na mesma linha da resposta
    pat2 = re.compile(
        r"(?m)^(\d+)\s*-\s*Resposta[s]?\s*:\s*[A-E]+\.\s*Justificativa:\s*(?:<)?(https?://[^\s<>]+)>?",
        re.IGNORECASE,
    )
    for m in pat2.finditer(blob):
        n = int(m.group(1))
        if n not in urls:
            urls[n] = m.group(2).strip()
    return urls


def parse_justification_meta(gab_block: str) -> dict[int, dict]:
    """
    Por número da questão no gabarito: texto do PDF após 'Justificativa:' e URL Top Invest.
    O texto é o corpo da justificativa no material; a URL é referência adicional ao site.
    """
    blob = normalize_gabarito_urls_blob(gab_block)
    out = {}
    starts = list(re.finditer(r"(?m)^(\d+)\s*-\s*Resposta[s]?\s*:", blob))
    for i, m in enumerate(starts):
        qn = int(m.group(1))
        seg_end = starts[i + 1].start() if i + 1 < len(starts) else len(blob)
        segment = blob[m.start() : seg_end]
        jm = re.search(r"Justificativa:\s*", segment, flags=re.IGNORECASE | re.DOTALL)
        if not jm:
            continue
        tail = segment[jm.end() :].strip()
        url = None
        um = re.search(r"(https?://[^\s<>]+)", tail)
        if um:
            url = um.group(1).rstrip(">).,;")
            before = tail[: um.start()].strip()
            after = tail[um.end() :].strip()
            parts_txt = [before, after]
            text_part = " ".join(p for p in parts_txt if p).strip()
        else:
            text_part = tail
        text_part = re.sub(r"\s+", " ", text_part).strip()
        out[qn] = {
            "url": url,
            "text": text_part if text_part else None,
        }
    legacy = parse_justification_urls(gab_block)
    for qn, u in legacy.items():
        if qn not in out:
            out[qn] = {"url": u, "text": None}
        elif not out[qn].get("url"):
            out[qn]["url"] = u
    return out


def main():
    with pdfplumber.open(str(PDF)) as pdf:
        blob = full_text(pdf)

    all_q = []
    problems = []

    for sec, body, gab_block in iter_sections(blob):
        qs = parse_questions_block(body)
        gab = parse_gabarito_block(gab_block)
        just_meta = parse_justification_meta(gab_block)
        for q in qs:
            ln = q["n_local"]
            if ln not in gab:
                problems.append(f"sec {sec} q {ln} ref {q['ref']} sem gabarito")
                continue
            c_idx = gab[ln]
            if c_idx >= len(q["options"]):
                problems.append(f"sec {sec} q {ln} gabarito fora do índice")
                continue
            entry = {
                "ref": q["ref"],
                "section": sec,
                "q": q["q"],
                "options": q["options"],
                "correct": c_idx,
            }
            jm = just_meta.get(ln)
            if jm:
                if jm.get("url"):
                    entry["justificationUrl"] = jm["url"]
                if jm.get("text"):
                    entry["justificationText"] = jm["text"]
            all_q.append(entry)

    for i, q in enumerate(all_q, start=1):
        q["id"] = i

    with open(str(OUT), "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)

    print("questions", len(all_q))
    if problems:
        print("problems", len(problems))
        for p in problems[:40]:
            print(" ", p)


if __name__ == "__main__":
    main()
