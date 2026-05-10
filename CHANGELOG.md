# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers are assigned chronologically for this repository (not necessarily tagged in git).

## [Unreleased]

<!-- Add significant work here before folding it into a dated release section below. -->

## [0.4.0] - 2026-05-10

### Added

- Cursor project rules under `.cursor/rules/` (repository context, Python scripts, env/secrets guidance).
- `.cursorignore` so local `.env` files are not indexed by Cursor.
- Local RAG tooling: `_rag_local.py`, `_enrich_justifications.py`, and `requirements-rag.txt`.
- `.gitignore` entries for `.venv/`, local `.rag/` index, and `.env` / `.env.*`.

### Changed

- Refreshed Top Invest extraction, `_questions_topinvest.json`, `_build_html_tabs.py`, and regenerated `simulado_ancord_1.html`.

### Notes

- Assistant-facing workflow: Cursor replies in **English**; learner-facing simulado copy stays **pt-BR**.

## [0.3.0] - 2026-05-08

### Added

- Exam timer (2h30 ANCORD pacing; equivalent pacing on the Top Invest tab).
- Top Invest justification URLs from the gabarito PDF stored on questions metadata.
- Footer links in HTML to Top Invest commentary / justification pages.
- Highlight of the correct alternative when the learner picks a wrong answer.

### Fixed

- Top Invest answer-key parsing edge cases (e.g. **AB** glued together, URLs split across lines).

## [0.2.0] - 2026-04-20

### Added

- Tabbed simulado: **Apostila** (ANCORD) and **Top Invest** sources.
- Source PDF `Material_TopInvest_AI-da-Ancord.pdf` for Top Invest content.
- `_extract_topinvest.py` and `_questions_topinvest.json`.
- `_build_html_tabs.py` for tabbed HTML output.

### Changed

- `simulado_ancord_1.html` updated for dual-source navigation.

## [0.1.0] - 2026-04-20

### Added

- Initial static HTML simulado **ANCORD 1** (80 multiple-choice questions).
- Source PDF `SIMULADO_ANCORD_Fevereiro-1.pdf`.
- Extraction script `_extract_q.py` producing `_questions_raw.json`.
- HTML builder `_build_html.py` and initial `simulado_ancord_1.html`.
- Basic `.gitignore`.
