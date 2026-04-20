# Extrai Simulado Ancord 1 do PDF (páginas 3-21) — filtra anomalias (x0<0) e monta texto em ordem.
import json
import re
import pdfplumber

PDF = r"c:\Users\luiz.barrozo\Desktop\simulado ancord\SIMULADO_ANCORD_Fevereiro-1.pdf"
OUT = r"c:\Users\luiz.barrozo\Desktop\simulado ancord\_questions_raw.json"


def page_reading_text(page):
    w, h = page.width, page.height
    words = [x for x in page.extract_words() if 20 < x["x0"] < w - 20 and x.get("x1", 0) > 0]
    # Ordena: linha a linha (y) depois coluna (x)
    words.sort(key=lambda t: (round(t["top"] / 2) * 2, t["x0"]))
    lines, cur, last_key = [], [], None
    for t in words:
        key = round(t["top"] / 3) * 3
        if last_key is not None and key != last_key and cur:
            lines.append(" ".join(cur))
            cur = []
        last_key = key
        cur.append(t["text"])
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)


def main():
    parts = []
    with pdfplumber.open(PDF) as pdf:
        for pi in range(2, 21):
            parts.append(page_reading_text(pdf.pages[pi]))
    full = "\n\n".join(parts)
    # Remove marcas
    lines = []
    for ln in full.splitlines():
        if any(
            s in ln
            for s in (
                "Apostila",
                "Simulados para a Ancord",
                "www.academiarafaeltoro",
            )
        ):
            continue
        lines.append(ln)
    full = "\n".join(lines)
    full = re.sub(r"^Simulado\s+", "", full, flags=re.MULTILINE)

    chunks = re.split(r"\n(?=\d{2}\s*\[)", full.strip())
    questions = []
    opt_re = re.compile(r"^[abcd]\)\s*", re.MULTILINE)

    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        m_head = re.match(r"(\d{2})\s*\[([^\]]+)\]\s*(.*)", ch, re.DOTALL)
        if not m_head:
            continue
        num_s, code, rest = m_head.group(1), m_head.group(2), m_head.group(3)
        split_m = opt_re.search(rest)
        if not split_m:
            continue
        stem = rest[: split_m.start()].strip()
        opts_blob = rest[split_m.start() :].strip()
        positions = [(m.start(), m.group()) for m in opt_re.finditer(opts_blob)]
        if len(positions) < 4:
            continue
        opts = []
        for i in range(4):
            start = positions[i][0]
            end = positions[i + 1][0] if i + 1 < len(positions) else len(opts_blob)
            block = opts_blob[start:end].strip()
            line0, _, body = block.partition("\n")
            combined = line0.replace(positions[i][1], "").strip()
            if body:
                combined = (combined + " " + body.replace("\n", " ")).strip()
            opts.append(combined)
        questions.append(
            {
                "id": int(num_s),
                "code": code,
                "q": stem.replace("\n", " ").strip(),
                "options": opts,
            }
        )

    questions.sort(key=lambda x: x["id"])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print("parsed", len(questions))
    missing = [i for i in range(1, 81) if i not in {q["id"] for q in questions}]
    print("missing", missing)


if __name__ == "__main__":
    main()
