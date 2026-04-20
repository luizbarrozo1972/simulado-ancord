# Gera simulado_ancord_1.html a partir de _questions_raw.json + gabarito do PDF.
import json
import re

GABARITO = """
01. D 02. D 03. D 04. D 05. D 06. B 07. B 08. C 09. D 10. C 11. C 12. A 13. A 14. B 15. A 16. A 17. A
18. B 19. B 20. A 21. D 22. C 23. D 24. D 25. C 26. A 27. D 28. C 29. A 30. D 31. B 32. D 33. D 34. D
35. B 36. D 37. D 38. D 39. C 40. A 41. D 42. D 43. A 44. C 45. C 46. D 47. B 48. A 49. C 50. D 51. A
52. B 53. B 54. C 55. A 56. C 57. B 58. D 59. A 60. C 61. D 62. A 63. B 64. A 65. C 66. C 67. C 68. C
69. D 70. D 71. C 72. D 73. C 74. C 75. B 76. A 77. D 78. B 79. A 80. D
"""

LET = {"A": 0, "B": 1, "C": 2, "D": 3}


def parse_gabarito():
    out = {}
    for m in re.finditer(r"(\d+)\.\s*([A-D])", GABARITO):
        out[int(m.group(1))] = LET[m.group(2)]
    return out


def main():
    gab = parse_gabarito()
    with open(
        r"c:\Users\luiz.barrozo\Desktop\simulado ancord\_questions_raw.json",
        encoding="utf-8",
    ) as f:
        raw = json.load(f)
    items = []
    for q in raw:
        i = q["id"]
        if i not in gab:
            raise SystemExit(f"Sem gabarito para id {i}")
        items.append(
            {
                "id": i,
                "q": q["q"],
                "options": q["options"],
                "correct": gab[i],
            }
        )
    items.sort(key=lambda x: x["id"])
    payload = json.dumps(items, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulado ANCORD 1 — 80 questões</title>
    <style>
        :root {{
            --primary: #1a365d;
            --accent: #2b6cb0;
            --success: #276749;
            --success-bg: #c6f6d5;
            --error: #c53030;
            --error-bg: #fed7d7;
            --muted: #718096;
            --bg: #edf2f7;
            --card: #ffffff;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: "Segoe UI", system-ui, sans-serif;
            background: var(--bg);
            color: var(--primary);
            line-height: 1.55;
            margin: 0;
            padding: 88px 16px 100px;
            max-width: 920px;
            margin-left: auto;
            margin-right: auto;
        }}
        .score-panel {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 100;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: #fff;
            padding: 12px 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,.15);
        }}
        .score-inner {{
            max-width: 920px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px 16px;
            align-items: center;
        }}
        .score-item {{ text-align: center; }}
        .score-item strong {{
            display: block;
            font-size: 1.35rem;
            font-variant-numeric: tabular-nums;
        }}
        .score-item span {{ font-size: 0.78rem; opacity: 0.92; }}
        .progress-wrap {{
            grid-column: 1 / -1;
            height: 8px;
            background: rgba(255,255,255,.25);
            border-radius: 999px;
            overflow: hidden;
            margin-top: 4px;
        }}
        .progress-bar {{
            height: 100%;
            width: 0%;
            background: #9ae6b4;
            border-radius: 999px;
            transition: width 0.25s ease;
        }}
        .header {{
            text-align: center;
            background: var(--card);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,.06);
            margin-bottom: 20px;
        }}
        .header h1 {{ margin: 0 0 8px; font-size: 1.35rem; }}
        .header p {{ margin: 0; color: var(--muted); font-size: 0.92rem; }}
        .question-card {{
            background: var(--card);
            padding: 18px 20px;
            margin-bottom: 16px;
            border-radius: 12px;
            box-shadow: 0 1px 6px rgba(0,0,0,.06);
        }}
        .question-text {{ font-weight: 600; margin-bottom: 14px; font-size: 0.98rem; }}
        .option-label {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 10px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 8px;
            transition: background .15s, border-color .15s;
        }}
        .option-label:hover {{ background: #f7fafc; }}
        .option-label input {{ margin-top: 3px; accent-color: var(--accent); }}
        .correct {{ background: var(--success-bg) !important; border-color: var(--success) !important; }}
        .wrong {{ background: var(--error-bg) !important; border-color: var(--error) !important; }}
        .opt-text {{ flex: 1; }}
        .controls {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--card);
            padding: 12px 16px;
            display: flex;
            justify-content: center;
            gap: 12px;
            box-shadow: 0 -4px 16px rgba(0,0,0,.08);
        }}
        button {{
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        .btn-clear {{ background: var(--error); color: #fff; }}
        .btn-clear:hover {{ filter: brightness(1.05); }}
    </style>
</head>
<body>
    <div class="score-panel" role="region" aria-label="Pontuação">
        <div class="score-inner">
            <div class="score-item"><strong id="hits">0</strong><span>Acertos</span></div>
            <div class="score-item"><strong id="wrong">0</strong><span>Erros</span></div>
            <div class="score-item"><strong id="answered">0</strong><span>Respondidas</span></div>
            <div class="score-item"><strong id="pct">0%</strong><span>Taxa (sobre respondidas)</span></div>
            <div class="score-item"><strong id="pct-total">0%</strong><span>Parcial sobre 80 questões</span></div>
            <div class="progress-wrap"><div class="progress-bar" id="progress-bar"></div></div>
        </div>
    </div>

    <div class="header">
        <h1>Simulado ANCORD 1</h1>
        <p>80 questões · Gabarito conforme apostila Fevereiro/2024 · Progresso salvo neste navegador.</p>
    </div>

    <div id="quiz-container"></div>

    <div class="controls">
        <button type="button" class="btn-clear" id="btn-clear">Limpar respostas</button>
    </div>

    <script>
        const questions = {payload};

        const STORAGE_KEY = "ancord_sim1_v2";

        const hitsEl = document.getElementById("hits");
        const wrongEl = document.getElementById("wrong");
        const answeredEl = document.getElementById("answered");
        const pctEl = document.getElementById("pct");
        const pctTotalEl = document.getElementById("pct-total");
        const progressBar = document.getElementById("progress-bar");
        const container = document.getElementById("quiz-container");

        function loadSaved() {{
            try {{
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}");
            }} catch (e) {{
                return {{}};
            }}
        }}

        function saveAnswer(qId, optionIdx) {{
            const data = loadSaved();
            data[qId] = optionIdx;
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
            updateScore();
            renderHints();
        }}

        function updateScore() {{
            const data = loadSaved();
            let hits = 0, wrong = 0, answered = 0;
            questions.forEach((item) => {{
                const sel = data[item.id];
                if (sel === undefined || sel === null) return;
                answered++;
                if (sel === item.correct) hits++;
                else wrong++;
            }});
            hitsEl.textContent = hits;
            wrongEl.textContent = wrong;
            answeredEl.textContent = answered;
            const rate = answered ? Math.round((hits / answered) * 1000) / 10 : 0;
            pctEl.textContent = rate + "%";
            const rateTotal = Math.round((hits / questions.length) * 1000) / 10;
            pctTotalEl.textContent = rateTotal + "%";
            progressBar.style.width = (answered / questions.length * 100) + "%";
        }}

        function renderHints() {{
            const data = loadSaved();
            questions.forEach((item) => {{
                const sel = data[item.id];
                if (sel === undefined || sel === null) return;
                for (let o = 0; o < 4; o++) {{
                    const lab = document.getElementById("label-" + item.id + "-" + o);
                    if (!lab) continue;
                    lab.classList.remove("correct", "wrong");
                    if (o === sel) {{
                        lab.classList.add(o === item.correct ? "correct" : "wrong");
                    }}
                }}
            }});
        }}

        function initQuiz() {{
            container.innerHTML = "";
            const data = loadSaved();
            questions.forEach((item, qIdx) => {{
                const card = document.createElement("div");
                card.className = "question-card";
                const opts = document.createElement("div");
                item.options.forEach((opt, oIdx) => {{
                    const lab = document.createElement("label");
                    lab.className = "option-label";
                    lab.id = "label-" + item.id + "-" + oIdx;
                    const inp = document.createElement("input");
                    inp.type = "radio";
                    inp.name = "q-" + item.id;
                    inp.value = String(oIdx);
                    if (data[item.id] === oIdx) inp.checked = true;
                    inp.addEventListener("change", () => {{
                        saveAnswer(item.id, oIdx);
                    }});
                    const span = document.createElement("span");
                    span.className = "opt-text";
                    span.textContent = String.fromCharCode(65 + oIdx) + ") " + opt;
                    lab.appendChild(inp);
                    lab.appendChild(span);
                    opts.appendChild(lab);
                }});
                const title = document.createElement("div");
                title.className = "question-text";
                title.textContent = (qIdx + 1) + ". " + item.q;
                card.appendChild(title);
                card.appendChild(opts);
                container.appendChild(card);
            }});
            updateScore();
            renderHints();
        }}

        document.getElementById("btn-clear").addEventListener("click", () => {{
            if (confirm("Limpar todas as respostas salvas neste dispositivo?")) {{
                localStorage.removeItem(STORAGE_KEY);
                initQuiz();
            }}
        }});

        initQuiz();
    </script>
</body>
</html>
"""

    out_path = r"c:\Users\luiz.barrozo\Desktop\simulado ancord\simulado_ancord_1.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("written", out_path)


if __name__ == "__main__":
    main()
