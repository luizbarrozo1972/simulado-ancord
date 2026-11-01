# Gera simulado_pec_recertificacao.html — mock PEC 40 questões + drill recertificação.
import json
from pathlib import Path

from _pec_bank import CHAPTER_LABELS, PEC_CHAPTER_TARGETS, write_bank_json

ROOT = Path(__file__).resolve().parent
EXAM_SEC = 150 * 60  # 2h30 — Regulamento ANCORD PEC (FGV)


def main():
    bank = write_bank_json()
    mock = bank["mock_exam"]
    drill = bank["drill"]
    j_mock = json.dumps(mock, ensure_ascii=False)
    j_drill = json.dumps(drill, ensure_ascii=False)
    j_labels = json.dumps(CHAPTER_LABELS, ensure_ascii=False)
    j_targets = json.dumps(PEC_CHAPTER_TARGETS, ensure_ascii=False)
    n_mock, n_drill = len(mock), len(drill)

    desc_mock = (
        f"{n_mock} questões · Prova PEC recertificação (FGV/ANCORD): "
        "aprovação ≥70% global (28/40) e ≥50% em cada capítulo · 2 h 30 min."
    )
    desc_drill = (
        f"{n_drill} questões extras · Cap. I (RCVM 178/179) e normas pós-2023 "
        "(RCVM 175, CMN 5.118/5.119, Lei 14.754/2023). Mesmas regras de aprovação por capítulo."
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulado ANCORD – Recertificação PEC</title>
    <style>
        :root {{
            --primary: #1a365d;
            --accent: #2b6cb0;
            --success: #276749;
            --success-bg: #c6f6d5;
            --error: #c53030;
            --error-bg: #fed7d7;
            --warn: #b7791f;
            --warn-bg: #fefcbf;
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
            padding: 208px 16px 120px;
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
            grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
            gap: 8px 12px;
            align-items: center;
        }}
        .score-item {{ text-align: center; }}
        .score-item strong {{
            display: block;
            font-size: 1.25rem;
            font-variant-numeric: tabular-nums;
        }}
        .score-item span {{ font-size: 0.75rem; opacity: 0.92; }}
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
            padding: 24px 22px 22px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,.06);
            margin-bottom: 20px;
        }}
        .tab-bar {{
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 4px;
            margin-bottom: 16px;
            padding: 4px;
        }}
        .tab-bar button, .tab-bar a.tab-link {{
            padding: 11px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.88rem;
            background: #e2e8f0;
            color: var(--primary);
            text-decoration: none;
            display: inline-block;
        }}
        .tab-bar button.active {{
            background: var(--primary);
            color: #fff;
        }}
        .tab-bar a.tab-link {{
            background: #bee3f8;
        }}
        .header h1 {{ margin: 0 0 8px; font-size: 1.32rem; }}
        .header p {{ margin: 0; color: var(--muted); font-size: 0.9rem; }}
        .pec-results {{
            background: var(--card);
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 6px rgba(0,0,0,.06);
        }}
        .pec-results h2 {{
            margin: 0 0 12px;
            font-size: 1.05rem;
        }}
        .pec-verdict {{
            padding: 10px 14px;
            border-radius: 8px;
            font-weight: 600;
            margin-bottom: 14px;
        }}
        .pec-verdict.pass {{ background: var(--success-bg); color: var(--success); }}
        .pec-verdict.fail {{ background: var(--error-bg); color: var(--error); }}
        .pec-verdict.pending {{ background: var(--warn-bg); color: var(--warn); }}
        .chapter-grid {{
            display: grid;
            gap: 8px;
        }}
        .chapter-row {{
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 12px;
            align-items: center;
            padding: 8px 10px;
            border-radius: 8px;
            background: #f7fafc;
            font-size: 0.88rem;
        }}
        .chapter-row.fail-ch {{ background: #fff5f5; }}
        .chapter-row.pass-ch {{ background: #f0fff4; }}
        .chapter-pct {{ font-weight: 700; font-variant-numeric: tabular-nums; }}
        #quiz-container {{ padding-top: 8px; }}
        .question-card {{
            background: var(--card);
            padding: 22px;
            margin-bottom: 16px;
            border-radius: 12px;
            box-shadow: 0 1px 6px rgba(0,0,0,.06);
        }}
        .chapter-tag {{
            font-size: 0.8rem;
            color: var(--accent);
            font-weight: 600;
            margin-bottom: 8px;
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
        }}
        .option-label:hover {{ background: #f7fafc; }}
        .option-label input {{ margin-top: 3px; accent-color: var(--accent); }}
        .correct {{ background: var(--success-bg) !important; border-color: var(--success) !important; }}
        .wrong {{ background: var(--error-bg) !important; border-color: var(--error) !important; }}
        .option-label.reveal-correct {{
            background: #e6fffa !important;
            border-color: #319795 !important;
            border-width: 2px;
        }}
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
        .timer-row {{
            grid-column: 1 / -1;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 10px 16px;
            padding-top: 10px;
            margin-top: 6px;
            border-top: 1px solid rgba(255,255,255,.28);
            font-size: 0.88rem;
        }}
        .timer-row #timer-display {{
            font-size: 1.5rem;
            font-variant-numeric: tabular-nums;
            font-weight: 700;
        }}
        .timer-row .timer-btn {{
            padding: 6px 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.82rem;
            background: rgba(255,255,255,.22);
            color: #fff;
        }}
        .score-panel.timer-expired #timer-display {{ color: #feb2b2; }}
        .q-footer {{
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px dashed #cbd5e0;
            font-size: 0.88rem;
        }}
        .wrong-reveal {{
            margin-top: 8px;
            padding: 10px 12px;
            border-radius: 8px;
            background: #fff5f5;
            border: 1px solid #feb2b2;
            color: #742a2a;
        }}
        .justification-text {{
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px dashed rgba(116, 42, 42, 0.35);
            line-height: 1.45;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="score-panel" role="region" aria-label="Pontuação">
        <div class="score-inner">
            <div class="score-item"><strong id="hits">0</strong><span>Acertos</span></div>
            <div class="score-item"><strong id="wrong">0</strong><span>Erros</span></div>
            <div class="score-item"><strong id="answered">0</strong><span>Respondidas</span></div>
            <div class="score-item"><strong id="pct">0%</strong><span>Taxa (respondidas)</span></div>
            <div class="score-item"><strong id="pct-total">0%</strong><span id="partial-label">Parcial</span></div>
            <div class="progress-wrap"><div class="progress-bar" id="progress-bar"></div></div>
            <div class="timer-row" aria-live="polite">
                <span id="timer-caption">PEC recertificação · 2 h 30 min</span>
                <strong id="timer-display">150:00</strong>
                <button type="button" class="timer-btn" id="timer-start">Iniciar</button>
                <button type="button" class="timer-btn" id="timer-reset">Zerar timer</button>
            </div>
        </div>
    </div>

    <div class="header">
        <div class="tab-bar">
            <button type="button" class="tab-btn active" data-tab="1">Mock PEC ({n_mock})</button>
            <button type="button" class="tab-btn" data-tab="2">Drill recertificação ({n_drill})</button>
            <a class="tab-link" href="simulado_ancord_1.html">← Simulados apostila / Top Invest</a>
        </div>
        <h1 id="hdr-title">Simulado ANCORD – Recertificação PEC</h1>
        <p id="hdr-desc">{desc_mock}</p>
    </div>

    <div class="pec-results" id="pec-results" aria-live="polite">
        <h2>Resultado por capítulo (regra PEC)</h2>
        <div class="pec-verdict pending" id="pec-verdict">Responda as questões para calcular aprovação.</div>
        <div class="chapter-grid" id="chapter-grid"></div>
    </div>

    <div id="quiz-container"></div>

    <div class="controls">
        <button type="button" class="footer-btn btn-clear" id="btn-clear">Limpar respostas desta aba</button>
    </div>

    <script>
        const QUESTIONS_MOCK = {j_mock};
        const QUESTIONS_DRILL = {j_drill};
        const CHAPTER_LABELS = {j_labels};
        const CHAPTER_TARGETS = {j_targets};
        const PASS_OVERALL = 0.7;
        const PASS_CHAPTER = 0.5;

        const STORAGE = {{ 1: "ancord_pec_mock_v1", 2: "ancord_pec_drill_v1" }};
        const META = {{
            1: {{ title: "Simulado ANCORD – Recertificação PEC", desc: {json.dumps(desc_mock)} }},
            2: {{ title: "Drill — Cap. I e normas pós-2023", desc: {json.dumps(desc_drill)} }}
        }};
        const EXAM_DURATION_SEC = {{ 1: {EXAM_SEC}, 2: {EXAM_SEC} }};
        const TIMER_STORAGE = "ancord_pec_timer_v1";

        let activeTab = 1;
        const hitsEl = document.getElementById("hits");
        const wrongEl = document.getElementById("wrong");
        const answeredEl = document.getElementById("answered");
        const pctEl = document.getElementById("pct");
        const pctTotalEl = document.getElementById("pct-total");
        const partialLabel = document.getElementById("partial-label");
        const progressBar = document.getElementById("progress-bar");
        const container = document.getElementById("quiz-container");
        const timerDisplay = document.getElementById("timer-display");
        const timerCaption = document.getElementById("timer-caption");
        const timerStartBtn = document.getElementById("timer-start");
        const timerResetBtn = document.getElementById("timer-reset");
        const scorePanelEl = document.querySelector(".score-panel");
        const pecVerdict = document.getElementById("pec-verdict");
        const chapterGrid = document.getElementById("chapter-grid");

        function getQuestions() {{
            return activeTab === 1 ? QUESTIONS_MOCK : QUESTIONS_DRILL;
        }}

        function storageKey() {{ return STORAGE[activeTab]; }}

        function loadSaved() {{
            try {{ return JSON.parse(localStorage.getItem(storageKey()) || "{{}}"); }}
            catch (e) {{ return {{}}; }}
        }}

        function loadTimerState() {{
            try {{ return JSON.parse(localStorage.getItem(TIMER_STORAGE) || "{{}}"); }}
            catch (e) {{ return {{}}; }}
        }}

        function saveTimerState(state) {{
            localStorage.setItem(TIMER_STORAGE, JSON.stringify(state));
        }}

        function getTimerSlot() {{
            const st = loadTimerState();
            const tab = String(activeTab);
            if (!st[tab]) st[tab] = {{ startAt: null, durationSec: EXAM_DURATION_SEC[activeTab] }};
            return st;
        }}

        function formatRemain(sec) {{
            sec = Math.max(0, Math.floor(sec));
            const h = Math.floor(sec / 3600);
            const m = Math.floor((sec % 3600) / 60);
            const s = sec % 60;
            if (h > 0) return h + ":" + String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
            return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
        }}

        function updateTimerUI() {{
            const st = getTimerSlot();
            const tab = String(activeTab);
            const slot = st[tab] || {{}};
            const dur = slot.durationSec ?? EXAM_DURATION_SEC[activeTab];
            timerCaption.textContent = "PEC · 2 h 30 min · " + getQuestions().length + " questões";
            if (!slot.startAt) {{
                timerDisplay.textContent = formatRemain(dur);
                timerStartBtn.textContent = "Iniciar";
                scorePanelEl.classList.remove("timer-expired");
                return;
            }}
            const left = dur - (Date.now() - slot.startAt) / 1000;
            timerDisplay.textContent = formatRemain(left);
            timerStartBtn.textContent = "Em andamento";
            scorePanelEl.classList.toggle("timer-expired", left <= 0);
        }}

        let timerInterval = null;
        function ensureTimerTick() {{
            if (timerInterval) clearInterval(timerInterval);
            timerInterval = setInterval(updateTimerUI, 1000);
        }}

        function saveAnswer(qId, optionIdx) {{
            const data = loadSaved();
            data[qId] = optionIdx;
            localStorage.setItem(storageKey(), JSON.stringify(data));
            updateScore();
            renderHints();
        }}

        function chapterStats(questions, data) {{
            const stats = {{}};
            questions.forEach((item) => {{
                const ch = item.chapter;
                if (!stats[ch]) stats[ch] = {{ total: 0, hits: 0, answered: 0 }};
                stats[ch].total++;
                const sel = data[item.id];
                if (sel === undefined || sel === null) return;
                stats[ch].answered++;
                if (sel === item.correct) stats[ch].hits++;
            }});
            return stats;
        }}

        function updateChapterResults(questions, data, hits, total) {{
            const stats = chapterStats(questions, data);
            chapterGrid.innerHTML = "";
            const chapters = Object.keys(CHAPTER_LABELS).filter((c) => stats[c]);
            chapters.forEach((ch) => {{
                const s = stats[ch];
                const pct = s.total ? Math.round((s.hits / s.total) * 1000) / 10 : 0;
                const row = document.createElement("div");
                row.className = "chapter-row";
                if (s.answered === s.total) {{
                    row.classList.add(pct >= PASS_CHAPTER * 100 ? "pass-ch" : "fail-ch");
                }}
                row.innerHTML =
                    "<span>" + CHAPTER_LABELS[ch] + "</span>" +
                    "<span>" + s.hits + "/" + s.total + " acertos</span>" +
                    '<span class="chapter-pct">' + pct + "%</span>";
                chapterGrid.appendChild(row);
            }});

            const answeredAll = questions.every((q) => {{
                const sel = data[q.id];
                return sel !== undefined && sel !== null;
            }});
            const overallPct = total ? hits / total : 0;
            let chapterOk = true;
            for (const ch of chapters) {{
                const s = stats[ch];
                if (s.hits / s.total < PASS_CHAPTER) chapterOk = false;
            }}
            if (!answeredAll) {{
                pecVerdict.className = "pec-verdict pending";
                pecVerdict.textContent =
                    "Responda todas as questões desta aba para simular aprovação PEC (≥70% global e ≥50% por capítulo).";
            }} else if (overallPct >= PASS_OVERALL && chapterOk) {{
                pecVerdict.className = "pec-verdict pass";
                pecVerdict.textContent =
                    "Aprovado simulado: " + hits + "/" + total + " (" + Math.round(overallPct * 100) + "%) e todos os capítulos ≥50%.";
            }} else {{
                pecVerdict.className = "pec-verdict fail";
                const parts = [];
                if (overallPct < PASS_OVERALL)
                    parts.push("global " + Math.round(overallPct * 100) + "% (mín. 70%)");
                if (!chapterOk) parts.push("algum capítulo abaixo de 50%");
                pecVerdict.textContent = "Reprovado simulado: " + parts.join("; ") + ".";
            }}
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
            updateChapterResults(questions, data, hits, questions.length);
        }}

        function renderHints() {{
            const questions = getQuestions();
            const data = loadSaved();
            questions.forEach((item) => {{
                const sel = data[item.id];
                const nOpt = item.options.length;
                for (let o = 0; o < nOpt; o++) {{
                    const lab = document.getElementById("label-" + activeTab + "-" + item.id + "-" + o);
                    if (lab) lab.classList.remove("correct", "wrong", "reveal-correct");
                }}
                const wrongBox = document.getElementById("wrong-" + activeTab + "-" + item.id);
                if (wrongBox) wrongBox.hidden = sel === undefined || sel === null || sel === item.correct;
                if (sel === undefined || sel === null) return;
                for (let o = 0; o < nOpt; o++) {{
                    const lab = document.getElementById("label-" + activeTab + "-" + item.id + "-" + o);
                    if (!lab) continue;
                    if (o === sel) lab.classList.add(o === item.correct ? "correct" : "wrong");
                    if (sel !== item.correct && o === item.correct) lab.classList.add("reveal-correct");
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
                const ct = document.createElement("div");
                ct.className = "chapter-tag";
                ct.textContent = CHAPTER_LABELS[item.chapter] || item.chapter;
                card.appendChild(ct);
                const title = document.createElement("div");
                title.className = "question-text";
                title.textContent = (qIdx + 1) + ". " + item.q;
                card.appendChild(title);
                const opts = document.createElement("div");
                item.options.forEach((opt, oIdx) => {{
                    const lab = document.createElement("label");
                    lab.className = "option-label";
                    lab.id = "label-" + activeTab + "-" + item.id + "-" + oIdx;
                    const inp = document.createElement("input");
                    inp.type = "radio";
                    inp.name = "pec-q-" + activeTab + "-" + item.id;
                    inp.value = String(oIdx);
                    if (data[item.id] === oIdx) inp.checked = true;
                    inp.addEventListener("change", () => saveAnswer(item.id, oIdx));
                    const span = document.createElement("span");
                    span.textContent = String.fromCharCode(65 + oIdx) + ") " + opt;
                    lab.appendChild(inp);
                    lab.appendChild(span);
                    opts.appendChild(lab);
                }});
                card.appendChild(opts);
                const footer = document.createElement("div");
                footer.className = "q-footer";
                const wrongReveal = document.createElement("div");
                wrongReveal.className = "wrong-reveal";
                wrongReveal.id = "wrong-" + activeTab + "-" + item.id;
                const cLet = String.fromCharCode(65 + item.correct);
                wrongReveal.innerHTML =
                    "<strong>Resposta correta:</strong> " + cLet + ") " + item.options[item.correct];
                if (item.explanation) {{
                    const jt = document.createElement("div");
                    jt.className = "justification-text";
                    jt.textContent = item.explanation;
                    wrongReveal.appendChild(jt);
                }}
                wrongReveal.hidden = true;
                footer.appendChild(wrongReveal);
                card.appendChild(footer);
                container.appendChild(card);
            }});
            document.getElementById("hdr-title").textContent = META[activeTab].title;
            document.getElementById("hdr-desc").textContent = META[activeTab].desc;
            document.getElementById("pec-results").style.display = activeTab === 1 ? "block" : "block";
            updateScore();
            renderHints();
            updateTimerUI();
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

        timerStartBtn.addEventListener("click", () => {{
            const st = getTimerSlot();
            const tab = String(activeTab);
            const slot = st[tab] || {{}};
            if (slot.startAt) return;
            slot.durationSec = EXAM_DURATION_SEC[activeTab];
            slot.startAt = Date.now();
            st[tab] = slot;
            saveTimerState(st);
            updateTimerUI();
        }});

        timerResetBtn.addEventListener("click", () => {{
            if (!confirm("Zerar o timer desta aba?")) return;
            const st = loadTimerState();
            const tab = String(activeTab);
            st[tab] = {{ startAt: null, durationSec: EXAM_DURATION_SEC[activeTab] }};
            saveTimerState(st);
            updateTimerUI();
        }});

        document.getElementById("btn-clear").addEventListener("click", () => {{
            if (confirm("Limpar todas as respostas desta aba neste dispositivo?")) {{
                localStorage.removeItem(storageKey());
                initQuiz();
            }}
        }});

        ensureTimerTick();
        initQuiz();
    </script>
</body>
</html>
"""

    out = ROOT / "simulado_pec_recertificacao.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("written", out, "mock=", n_mock, "drill=", n_drill)


if __name__ == "__main__":
    main()
