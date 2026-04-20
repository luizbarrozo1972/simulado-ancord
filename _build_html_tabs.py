# Gera simulado_ancord_1.html com abas: Simulado 1 (ANCORD) + Simulado 2 (Top Invest).
import json
import re

ROOT = r"c:\Users\luiz.barrozo\Desktop\simulado ancord"

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


def load_s1():
    gab = parse_gabarito()
    with open(f"{ROOT}\\_questions_raw.json", encoding="utf-8") as f:
        raw = json.load(f)
    items = []
    for q in raw:
        i = q["id"]
        items.append(
            {
                "id": i,
                "q": q["q"],
                "options": q["options"],
                "correct": gab[i],
            }
        )
    items.sort(key=lambda x: x["id"])
    return items


def load_s2():
    with open(f"{ROOT}\\_questions_topinvest.json", encoding="utf-8") as f:
        return json.load(f)


def main():
    s1 = load_s1()
    s2 = load_s2()
    j1 = json.dumps(s1, ensure_ascii=False)
    j2 = json.dumps(s2, ensure_ascii=False)
    n1, n2 = len(s1), len(s2)

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulados ANCORD — Apostila + Top Invest</title>
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
            padding: 158px 16px 120px;
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
            padding: 28px 22px 26px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,.06);
            margin-bottom: 28px;
        }}
        .tab-bar {{
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 6px;
            margin-bottom: 22px;
            padding: 6px 4px 8px;
        }}
        .tab-bar button {{
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.92rem;
            background: #e2e8f0;
            color: var(--primary);
        }}
        .tab-bar button:hover {{ filter: brightness(0.97); }}
        .tab-bar button.active {{
            background: var(--primary);
            color: #fff;
        }}
        .header h1 {{ margin: 0 0 10px; font-size: 1.35rem; }}
        .header p {{ margin: 0; color: var(--muted); font-size: 0.92rem; }}
        #quiz-container {{
            padding-top: 12px;
        }}
        .question-card {{
            background: var(--card);
            padding: 22px 22px 20px;
            margin-bottom: 16px;
            border-radius: 12px;
            box-shadow: 0 1px 6px rgba(0,0,0,.06);
        }}
        .question-text {{ font-weight: 600; margin-bottom: 14px; font-size: 0.98rem; }}
        .ref-tag {{ font-size: 0.82rem; color: var(--muted); font-weight: 500; margin-bottom: 10px; margin-top: 2px; }}
        .question-card:first-child {{
            margin-top: 8px;
        }}
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
        button.footer-btn {{
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
            <div class="score-item"><strong id="pct-total">0%</strong><span id="partial-label">Parcial (questões)</span></div>
            <div class="progress-wrap"><div class="progress-bar" id="progress-bar"></div></div>
        </div>
    </div>

    <div class="header">
        <div class="tab-bar">
            <button type="button" class="tab-btn active" data-tab="1">Simulado 1 · ANCORD ({n1})</button>
            <button type="button" class="tab-btn" data-tab="2">Simulado 2 · Top Invest ({n2})</button>
        </div>
        <h1 id="hdr-title">Simulado ANCORD 1</h1>
        <p id="hdr-desc">{n1} questões · Gabarito apostila Fevereiro/2024 (Rafael Toro). Progresso salvo por aba.</p>
    </div>

    <div id="quiz-container"></div>

    <div class="controls">
        <button type="button" class="footer-btn btn-clear" id="btn-clear">Limpar respostas desta aba</button>
    </div>

    <script>
        const QUESTIONS_S1 = {j1};
        const QUESTIONS_S2 = {j2};

        const STORAGE = {{
            1: "ancord_sim1_v2",
            2: "ancord_top_v1"
        }};

        const META = {{
            1: {{
                title: "Simulado ANCORD 1",
                desc: "{n1} questões · Gabarito apostila Fevereiro/2024 (Rafael Toro). Progresso salvo por aba."
            }},
            2: {{
                title: "Simulado Top Invest",
                desc: "{n2} questões · Extraídas do PDF Material Top Invest (simulados por módulo). Referência ref # em cada questão."
            }}
        }};

        let activeTab = 1;

        const hitsEl = document.getElementById("hits");
        const wrongEl = document.getElementById("wrong");
        const answeredEl = document.getElementById("answered");
        const pctEl = document.getElementById("pct");
        const pctTotalEl = document.getElementById("pct-total");
        const partialLabel = document.getElementById("partial-label");
        const progressBar = document.getElementById("progress-bar");
        const container = document.getElementById("quiz-container");

        function getQuestions() {{
            return activeTab === 1 ? QUESTIONS_S1 : QUESTIONS_S2;
        }}

        function storageKey() {{
            return STORAGE[activeTab];
        }}

        function loadSaved() {{
            try {{
                return JSON.parse(localStorage.getItem(storageKey()) || "{{}}");
            }} catch (e) {{
                return {{}};
            }}
        }}

        function saveAnswer(qId, optionIdx) {{
            const data = loadSaved();
            data[qId] = optionIdx;
            localStorage.setItem(storageKey(), JSON.stringify(data));
            updateScore();
            renderHints();
        }}

        function updateScore() {{
            const questions = getQuestions();
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
            partialLabel.textContent = "Parcial sobre " + questions.length + " questões";
            progressBar.style.width = (answered / questions.length * 100) + "%";
        }}

        function renderHints() {{
            const questions = getQuestions();
            const data = loadSaved();
            questions.forEach((item) => {{
                const sel = data[item.id];
                if (sel === undefined || sel === null) return;
                const nOpt = item.options.length;
                for (let o = 0; o < nOpt; o++) {{
                    const lab = document.getElementById(
                        "label-" + activeTab + "-" + item.id + "-" + o
                    );
                    if (!lab) continue;
                    lab.classList.remove("correct", "wrong");
                    if (o === sel) {{
                        lab.classList.add(o === item.correct ? "correct" : "wrong");
                    }}
                }}
            }});
        }}

        function initQuiz() {{
            const questions = getQuestions();
            container.innerHTML = "";
            const data = loadSaved();
            questions.forEach((item, qIdx) => {{
                const card = document.createElement("div");
                card.className = "question-card";
                if (activeTab === 2 && item.ref) {{
                    const rt = document.createElement("div");
                    rt.className = "ref-tag";
                    rt.textContent = "Ref. #" + item.ref + (item.section ? " · Módulo " + item.section : "");
                    card.appendChild(rt);
                }}
                const opts = document.createElement("div");
                item.options.forEach((opt, oIdx) => {{
                    const lab = document.createElement("label");
                    lab.className = "option-label";
                    lab.id = "label-" + activeTab + "-" + item.id + "-" + oIdx;
                    const inp = document.createElement("input");
                    inp.type = "radio";
                    inp.name = "quiz" + activeTab + "-q-" + item.id;
                    inp.value = String(oIdx);
                    if (data[item.id] === oIdx) inp.checked = true;
                    inp.addEventListener("change", () => saveAnswer(item.id, oIdx));
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
            document.getElementById("hdr-title").textContent = META[activeTab].title;
            document.getElementById("hdr-desc").textContent = META[activeTab].desc;
            updateScore();
            renderHints();
        }}

        document.querySelectorAll(".tab-btn").forEach((btn) => {{
            btn.addEventListener("click", () => {{
                const t = parseInt(btn.getAttribute("data-tab"), 10);
                if (t === activeTab) return;
                activeTab = t;
                document.querySelectorAll(".tab-btn").forEach((b) =>
                    b.classList.toggle("active", parseInt(b.getAttribute("data-tab"), 10) === activeTab)
                );
                initQuiz();
            }});
        }});

        document.getElementById("btn-clear").addEventListener("click", () => {{
            if (confirm("Limpar todas as respostas desta aba neste dispositivo?")) {{
                localStorage.removeItem(storageKey());
                initQuiz();
            }}
        }});

        initQuiz();
    </script>
</body>
</html>
"""

    out_path = f"{ROOT}\\simulado_ancord_1.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("written", out_path, "s1=", n1, "s2=", n2)


if __name__ == "__main__":
    main()
