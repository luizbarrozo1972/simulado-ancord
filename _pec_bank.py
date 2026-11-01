# Monta o banco de questões do simulado PEC (recertificação ANCORD).
# Entrada: _questions_raw.json, _questions_topinvest.json, gabarito Toro.
# Saída: estruturas mock_exam (40) e drill (extras cap. I e normas pós-2023).

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Distribuição oficial PEC (Regulamento ANCORD / FGV) — pode estar desatualizada vs. edital vigente.
PEC_CHAPTER_TARGETS = {
    "I": 4,
    "III": 4,
    "VII": 6,
    "VIII": 10,
    "IX": 4,
    "X": 2,
    "XII": 2,
    "XIV": 4,
    "XV": 4,
}

GABARITO = """
01. D 02. D 03. D 04. D 05. D 06. B 07. B 08. C 09. D 10. C 11. C 12. A 13. A 14. B 15. A 16. A 17. A
18. B 19. B 20. A 21. D 22. C 23. D 24. D 25. C 26. A 27. D 28. C 29. A 30. D 31. B 32. D 33. D 34. D
35. B 36. D 37. D 38. D 39. C 40. A 41. D 42. D 43. A 44. C 45. C 46. D 47. B 48. A 49. C 50. D 51. A
52. B 53. B 54. C 55. A 56. C 57. B 58. D 59. A 60. C 61. D 62. A 63. B 64. A 65. C 66. C 67. C 68. C
69. D 70. D 71. C 72. D 73. C 74. C 75. B 76. A 77. D 78. B 79. A 80. D
"""

LET = {"A": 0, "B": 1, "C": 2, "D": 3}

CHAPTER_LABELS = {
    "I": "Cap. I — Atividade do assessor",
    "III": "Cap. III — PLD/FTP e suitability",
    "VII": "Cap. VII — Gestão de risco",
    "VIII": "Cap. VIII — Mercado de capitais",
    "IX": "Cap. IX — Fundos de investimento",
    "X": "Cap. X — Anexos Res. CVM 175 / outros fundos",
    "XII": "Cap. XII — Clubes de investimento",
    "XIV": "Cap. XIV — Outros produtos",
    "XV": "Cap. XV — Derivativos",
}

# (capítulo, fonte, id) — fonte: toro | topinvest | new
MOCK_MANIFEST = [
    ("I", "toro", 2),
    ("I", "toro", 3),
    ("I", "new", "178-exclusividade"),
    ("I", "new", "178-diretor"),
    ("III", "toro", 13),
    ("III", "toro", 14),
    ("III", "toro", 15),
    ("III", "toro", 16),
    ("VII", "topinvest", 37),
    ("VII", "topinvest", 38),
    ("VII", "topinvest", 40),
    ("VII", "topinvest", 41),
    ("VII", "topinvest", 42),
    ("VII", "topinvest", 43),
    ("VIII", "toro", 20),
    ("VIII", "toro", 25),
    ("VIII", "toro", 28),
    ("VIII", "toro", 29),
    ("VIII", "toro", 30),
    ("VIII", "toro", 31),
    ("VIII", "toro", 32),
    ("VIII", "toro", 33),
    ("VIII", "toro", 35),
    ("VIII", "toro", 40),
    ("IX", "toro", 51),
    ("IX", "toro", 52),
    ("IX", "topinvest", 56),
    ("IX", "topinvest", 60),
    ("X", "topinvest", 67),
    ("X", "new", "175-subclasses"),
    ("XII", "topinvest", 86),
    ("XII", "topinvest", 88),
    ("XIV", "toro", 65),
    ("XIV", "toro", 68),
    ("XIV", "topinvest", 100),
    ("XIV", "new", "cmn-5119-lci"),
    ("XV", "toro", 69),
    ("XV", "toro", 70),
    ("XV", "toro", 71),
    ("XV", "toro", 72),
]

DRILL_MANIFEST = [
    ("I", "toro", 5),
    ("I", "toro", 9),
    ("I", "toro", 11),
    ("I", "new", "178-pj-objeto"),
    ("I", "new", "178-comunicacao-cvm"),
    ("I", "new", "179-remuneracao-ordem"),
    ("I", "new", "179-extrato-trimestral"),
    ("I", "new", "179-qualitativa-site"),
    ("X", "new", "175-resp-limitada"),
    ("X", "new", "175-anexo-fii"),
    ("XIV", "new", "cmn-5118-lastro"),
    ("IX", "new", "lei-14754-comecotas-fechado"),
    ("I", "new", "lei-14754-offshore"),
]

NEW_QUESTIONS = {
    "178-exclusividade": {
        "q": "Com a Resolução CVM 178/2023, em vigor desde 1º/6/2023, sobre a vinculação do assessor de investimento (AI) a intermediários, é correto afirmar que:",
        "options": [
            "a exclusividade com um único intermediário passou a ser obrigatória para AI pessoa natural.",
            "o AI pessoa natural e o AI pessoa jurídica podem atuar como prepostos de um ou mais intermediários, não havendo mais exclusividade imposta pela regulamentação da CVM.",
            "o AI pessoa jurídica continua obrigado a contrato de exclusividade, mas o AI pessoa natural não.",
            "contratos de exclusividade firmados antes da norma foram automaticamente invalidados pela CVM.",
        ],
        "correct": 1,
        "explanation": (
            "A RCVM 178/2023 flexibilizou a multivinculação: AI pessoa natural ou jurídica pode prestar serviços a um ou mais "
            "intermediários (arts. 2º, II, e 6º). A exclusividade deixou de ser exigência regulatória; contratos pré-existentes "
            "dependem das cláusulas contratuais, não são invalidados automaticamente pela norma (FAQ mercado)."
        ),
    },
    "178-diretor": {
        "q": "Na credenciamento de assessor de investimento pessoa jurídica, a Resolução CVM 178/2023 exige indicação de diretor responsável. Sobre esse cargo, assinale a alternativa correta:",
        "options": [
            "pode ser qualquer empregado da sociedade, mesmo sem registro como AI pessoa natural.",
            "deve ser diretor, sócio ou administrador da sociedade, registrado como AI pessoa natural; nomeação ou substituição deve ser informada à credenciadora e aos intermediários em até 7 dias úteis.",
            "é opcional quando a sociedade possui apenas um sócio AI.",
            "substitui integralmente o dever de fiscalização do intermediário contratante.",
        ],
        "correct": 1,
        "explanation": (
            "Arts. 2º, III, 16, IV, e 26, § 1º, da RCVM 178/2023: diretor responsável é diretor/sócio/administrador registrado "
            "como AI pessoa natural; comunicação em 7 dias úteis à entidade credenciadora e intermediários."
        ),
    },
    "178-pj-objeto": {
        "q": "Quanto ao credenciamento de assessor de investimento pessoa jurídica após a Resolução CVM 178/2023, é correto afirmar:",
        "options": [
            "o objeto social deve ser exclusivamente assessoria de investimentos, vedada qualquer outra atividade.",
            "a sociedade deve ser necessariamente sociedade simples.",
            "o objeto social deve incluir a prestação dos serviços de assessoria (art. 3º), admitindo-se atividades complementares nos mercados financeiro, de capitais, securitário e de capitalização, se compatíveis e não conflitantes.",
            "sócios não registrados como AI podem executar atividades do art. 3º sem registro.",
        ],
        "correct": 2,
        "explanation": (
            "A RCVM 178/2023 afastou a exigência de objeto social exclusivo e de forma societária única; exige objeto social "
            "compatível com a assessoria (arts. 6º, II, e 16, III), com possibilidade de atividades complementares reguladas, "
            "sem conflito com a atividade central."
        ),
    },
    "178-comunicacao-cvm": {
        "q": "Em caso de conduta do assessor de investimento que configure indício de infração à regulamentação, a comunicação à CVM é de responsabilidade:",
        "options": [
            "exclusiva da Ancord, em até 30 dias após fiscalização mensal.",
            "do credenciado, em 30 dias úteis após descredenciamento.",
            "da Ancord, independentemente do intermediário.",
            "do intermediário integrante do sistema de distribuição contratante do AI que cometeu a possível infração.",
        ],
        "correct": 3,
        "explanation": (
            "Conforme RCVM 178/2023 e deveres do intermediário/preposto: a instituição contratante integrante do sistema de "
            "distribuição deve comunicar indícios de infração à CVM (tema recorrente em provas; alinhado ao dever de supervisão "
            "do intermediário sobre o AI preposto)."
        ),
    },
    "179-remuneracao-ordem": {
        "q": "Pela Resolução CVM 179/2023 (Cap. VII-A da RCVM 35), as informações quantitativas sobre remuneração do intermediário devem ser apresentadas:",
        "options": [
            "somente no extrato anual enviado por correio.",
            "no mesmo momento e ambiente franqueado ao cliente para transmissão da ordem, com valores ou percentuais praticados para o produto ofertado (art. 26-E).",
            "apenas oralmente, antes da ordem.",
            "somente na página pública do site, sem área logada.",
        ],
        "correct": 1,
        "explanation": (
            "Art. 26-E da RCVM 35 (incluído pela RCVM 179/2023): remuneração quantitativa no ambiente de transmissão de ordens. "
            "Obrigações quantitativas e extratos tiveram vigência prorrogada para 1/11/2024 (RCVM 196/2023)."
        ),
    },
    "179-extrato-trimestral": {
        "q": "Sobre o extrato trimestral de remuneração previsto na Resolução CVM 179/2023, assinale a correta:",
        "options": [
            "é facultativo para clientes pessoa jurídica.",
            "deve conter remuneração auferida pelo intermediário em razão dos investimentos do cliente, discriminando modalidade, natureza da remuneração e parcela relativa a assessores (art. 26-F).",
            "substitui a declaração de IR do investidor.",
            "só se aplica a fundos exclusivos.",
        ],
        "correct": 1,
        "explanation": "Art. 26-F da RCVM 35: extrato trimestral com discriminação exigida, incluindo parcela de remuneração de assessores.",
    },
    "179-qualitativa-site": {
        "q": "As informações qualitativas sobre remuneração e conflitos de interesse (Res. CVM 179/2023) devem:",
        "options": [
            "ser mantidas apenas na área logada, sem acesso público.",
            "constar em página na rede mundial de computadores, em linguagem clara, descrevendo formas e arranjos (art. 26-B), sem necessidade de divulgar valores efetivos praticados nessa página.",
            "ser comunicadas verbalmente em cada prospecção.",
            "ser enviadas somente a investidores profissionais.",
        ],
        "correct": 1,
        "explanation": (
            "Arts. 26-A a 26-B da RCVM 35: transparência qualitativa no site; valores/percentuais efetivos vão ao ambiente de ordens "
            "(quantitativo). Norma não se aplica a investidores profissionais (art. 26-A e regulamentação)."
        ),
    },
    "175-subclasses": {
        "q": "A Resolução CVM 175/2022, no novo marco de fundos, permite:",
        "options": [
            "apenas uma classe de cotas por fundo, vedadas subclasses.",
            "estruturação em classes e subclasses de cotas, conforme regulamento do fundo e normas da Resolução.",
            "subclasses apenas para FII, vedadas nos demais anexos.",
            "classes de cotas somente para fundos fechados.",
        ],
        "correct": 1,
        "explanation": (
            "A RCVM 175/2022 modernizou fundos e prevê classes e subclasses de cotas (estrutura de condomínio), "
            "com regras nos anexos por tipo de fundo — base para FII, FIDC, FIP, ETF etc."
        ),
    },
    "175-resp-limitada": {
        "q": "No regime da Resolução CVM 175/2022, quanto à responsabilidade do cotista:",
        "options": [
            "o cotista responde ilimitada e solidariamente por todas as obrigações do fundo.",
            "a responsabilidade do cotista limita-se ao valor de suas cotas, salvo disposição legal específica em contrário.",
            "cotistas pessoa física respondem com patrimônio pessoal por débitos trabalhistas do administrador.",
            "não há previsão de limitação de responsabilidade em fundos fechados.",
        ],
        "correct": 1,
        "explanation": (
            "A RCVM 175/2022 mantém o princípio de responsabilidade limitada ao valor das cotas subscritas, "
            "característica central do condomínio de fundos."
        ),
    },
    "175-anexo-fii": {
        "q": "Fundos de investimento imobiliário (FII) no marco da Resolução CVM 175/2022:",
        "options": [
            "foram revogados e substituídos apenas por CRIs.",
            "têm regras específicas no Anexo da Resolução aplicável a FII (condomínio fechado, política de investimento, oferta etc.).",
            "só podem investir em títulos públicos.",
            "não podem ter cotas negociadas em bolsa.",
        ],
        "correct": 1,
        "explanation": "A RCVM 175/2022 traz anexo próprio para FII, consolidando regras antes espalhadas em instruções revogadas (ex.: ICVM 555).",
    },
    "cmn-5119-lci": {
        "q": "Segundo a Resolução CMN nº 5.119/2024 (alteração à Res. 4.410), o prazo mínimo de vencimento da LCI, quando atualizada mensalmente por índice de preços, é de:",
        "options": [
            "9 meses.",
            "12 meses.",
            "24 meses.",
            "36 meses.",
        ],
        "correct": 3,
        "explanation": (
            "Res. CMN 5.119/2024 alterou o art. 4º da Res. 4.410: LCI indexada a preços — prazo mínimo 36 meses; "
            "nos demais casos, prazo mínimo conforme redação vigente (9 meses após Res. 5.168/2024)."
        ),
    },
    "cmn-5118-lastro": {
        "q": "A Resolução CMN nº 5.118/2024 restringe o lastro de CRAs e CRIs. É vedado lastrear com:",
        "options": [
            "direitos creditórios do agronegócio em CRA de emissor do setor.",
            "títulos de dívida cujo devedor seja instituição financeira ou conglomerado prudencial (salvo exceções regulamentares).",
            "créditos imobiliários em CRI de emissor do setor imobiliário.",
            "recebíveis performados de consumo.",
        ],
        "correct": 1,
        "explanation": (
            "Art. 3º da Res. CMN 5.118/2024: veda lastro com devedores instituição financeira/conglomerado prudencial, "
            "operações entre partes relacionadas, entre outras restrições; há regras de transição para emissões anteriores."
        ),
    },
    "lei-14754-comecotas-fechado": {
        "q": "A Lei nº 14.754/2023 instituiu tributação periódica (come-cotas) para fundos de investimento. Sobre fundos fechados, assinale a correta:",
        "options": [
            "permanecem isentos de qualquer antecipação de IR.",
            "passam a sofrer retenção na fonte nos últimos dias úteis de maio e novembro, nos termos do art. 17 (abrangendo condomínios abertos e fechados, salvo exceções legais).",
            "só têm come-cotas se forem FII.",
            "come-cotas incide apenas sobre cotistas pessoa jurídica.",
        ],
        "correct": 1,
        "explanation": (
            "Art. 17, § 8º, da Lei 14.754/2023: incidência periódica abrange fundos abertos e fechados, com retenção em maio e "
            "novembro; alíquotas conforme longo/curto prazo (15%/20% na periodicidade, complemento no resgate)."
        ),
    },
    "lei-14754-offshore": {
        "q": "Quanto à tributação de investimentos no exterior pela Lei nº 14.754/2023, para pessoa física residente no Brasil:",
        "options": [
            "lucros de entidades controladas no exterior ficam isentos até repatriação.",
            "rendimentos de aplicações diretas e lucros de entidades controladas em paraíso fiscal ou com renda passiva relevante podem ser tributados anualmente (alíquota de 15%), com apuração na declaração anual.",
            "offshore nunca exige balanço patrimonial.",
            "fundos no exterior usam sempre regime de caixa sem ajuste anual.",
        ],
        "correct": 1,
        "explanation": (
            "Lei 14.754/2023 e IN RFB 2.180/2024: regime de transparência fiscal anual para aplicações no exterior e "
            "entidades controladas (art. 2º e seguintes); alíquota 15% na DAA para hipóteses previstas."
        ),
    },
}


def parse_gabarito() -> dict[int, int]:
    out: dict[int, int] = {}
    for m in re.finditer(r"(\d+)\.\s*([A-D])", GABARITO):
        out[int(m.group(1))] = LET[m.group(2)]
    return out


def load_toro() -> dict[int, dict]:
    gab = parse_gabarito()
    with open(ROOT / "_questions_raw.json", encoding="utf-8") as f:
        raw = json.load(f)
    return {q["id"]: {**q, "correct": gab[q["id"]]} for q in raw}


def load_topinvest() -> dict[int, dict]:
    with open(ROOT / "_questions_topinvest.json", encoding="utf-8") as f:
        data = json.load(f)
    return {q["id"]: q for q in data}


def _fix_explanation(text: str | None) -> str:
    if not text or text.startswith("INSUFICIENTE"):
        return ""
    text = re.sub(r"ICVM\s*301/99", "Res. CVM 30/2021", text, flags=re.I)
    text = re.sub(r"ICVM\s*539", "Res. CVM 30/2021", text, flags=re.I)
    return text.strip()


def _toro_explanation(qid: int, qtext: str) -> str:
    hints = {
        2: "Art. 28, II, RCVM 178/2023: fiscalização do AI preposto é dever do intermediário contratante.",
        3: "Vedado ao AI utilizar senha do cliente ou repassar ordens/credenciais a terceiros (deveres de conduta e sigilo).",
        13: "Lei 9.613/1998 e regulamentação PLD: destinação de recursos recuperados conforme legislação.",
        14: "Circular BACEN 3.978/2020: operações atípicas e comunicação ao COAF/BACEN.",
        15: "Lei 9.613/1998: tipificação de lavagem de dinheiro e ocultação de bens.",
        16: "Res. CVM 50/2021: deveres de PLD-FTP das entidades administradoras de mercados.",
        20: "Mercado de ações B3: liquidação e sistemas de negociação (Câmara de Ações).",
        65: "CDB: título de crédito emitido por IF bancária; características de emissão e negociação.",
        68: "Letras Imobiliárias (LI): captacao por sociedades de crédito imobiliário; características de prazo/garantia.",
    }
    if qid in hints:
        return hints[qid]
    return f"Gabarito apostila Rafael Toro (fev/2024), questão {qid}."


def _item_from_source(
    chapter: str,
    source: str,
    sid: int | str,
    seq: int,
    prefix: str,
    toro: dict,
    top: dict,
) -> dict:
    if source == "new":
        nq = NEW_QUESTIONS[str(sid)]
        return {
            "id": f"{prefix}-{seq}",
            "chapter": chapter,
            "q": nq["q"],
            "options": nq["options"],
            "correct": nq["correct"],
            "explanation": nq["explanation"],
            "source": f"new:{sid}",
        }
    if source == "toro":
        q = toro[int(sid)]
        return {
            "id": f"{prefix}-{seq}",
            "chapter": chapter,
            "q": q["q"],
            "options": q["options"],
            "correct": q["correct"],
            "explanation": _toro_explanation(int(sid), q["q"]),
            "source": f"toro:{sid}",
        }
    q = top[int(sid)]
    expl = _fix_explanation(q.get("justificationText")) or (
        f"Material Top Invest (ref. {q.get('ref', '?')}, módulo {q.get('section', '?')})."
    )
    return {
        "id": f"{prefix}-{seq}",
        "chapter": chapter,
        "q": q["q"],
        "options": q["options"],
        "correct": q["correct"],
        "explanation": expl,
        "source": f"topinvest:{sid}",
    }


def assemble_bank() -> dict:
    toro = load_toro()
    top = load_topinvest()
    mock = []
    for i, (ch, src, sid) in enumerate(MOCK_MANIFEST, start=1):
        mock.append(_item_from_source(ch, src, sid, i, "pec-m", toro, top))
    drill = []
    for i, (ch, src, sid) in enumerate(DRILL_MANIFEST, start=1):
        drill.append(_item_from_source(ch, src, sid, i, "pec-d", toro, top))

    counts: dict[str, int] = {}
    for q in mock:
        counts[q["chapter"]] = counts.get(q["chapter"], 0) + 1
    for ch, need in PEC_CHAPTER_TARGETS.items():
        if counts.get(ch, 0) != need:
            raise ValueError(f"Capítulo {ch}: esperado {need}, obtido {counts.get(ch, 0)}")
    if len(mock) != 40:
        raise ValueError(f"Mock deve ter 40 questões, tem {len(mock)}")

    return {
        "mock_exam": mock,
        "drill": drill,
        "chapter_labels": CHAPTER_LABELS,
        "targets": PEC_CHAPTER_TARGETS,
    }


def write_bank_json(path: Path | None = None) -> dict:
    bank = assemble_bank()
    path = path or ROOT / "_pec_questions.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)
    return bank


if __name__ == "__main__":
    b = write_bank_json()
    print("mock", len(b["mock_exam"]), "drill", len(b["drill"]))
