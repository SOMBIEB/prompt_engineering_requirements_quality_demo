# Requirements Quality with Rule-Based Checks — Demo (No API)

**Author: Bibata Sombié**  
A lightweight demo to analyze **requirements quality** (technical sentences) **without any external API**.  
It applies simple **rule-based heuristics** to detect common issues (vague terms, *and/or*, missing units, unclear conditions, multiple requirements, etc.) and proposes **template rewrites**.

## Contents
- `requirements_sample.xlsx` — example dataset of requirements (edit to match your context).
- `requirements_quality_demo.ipynb` — ready-to-run Jupyter notebook.
- `src/req_qa_cli.py` — CLI script to run checks from the terminal.
- `requirements.txt` — minimal dependencies.

## Local Setup (Python 3.9+)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Use — Notebook
Open and run: `requirements_quality_demo.ipynb`

## Use — CLI
```bash
python src/req_qa_cli.py --input requirements_sample.xlsx --output requirements_report.xlsx
```
Options:
- `--input` : path to input Excel (must contain `requirement_text`; `id` optional).
- `--output` : path to output Excel report.
- `--sheet` : optional sheet name to read (default: first sheet).

## Expected Input Format
Excel file with at least:
- `requirement_text` — the requirement sentence.  
`id` column is recommended.

## Detection Logic (Simplified)
- **Ambiguity `and/or`**: presence of `et/ou` in FR (or `and/or` in EN if adapted).
- **Vague/subjective terms**: `rapide`, `convivial`, `lisible`, `clair`, `optimal`, `robuste`, `léger`, etc.
- **Missing units**: numbers without units (`V`, `A`, `W`, `°C`, `ms`, `kg`, etc.).
- **Unspecified trigger/condition**: phrases like “if a problem occurs”, “when necessary”.
- **Multiple requirements**: several actions jammed into one sentence (heuristic).
- **Unspecific security**: “protected” without a method/standard (e.g., AES-256).

> ⚠️ These are demonstrator heuristics. They **do not replace** expert reviews and should be adapted to internal rules (INCOSE/EARS, company policies, etc.).

## Output
The Excel report includes:
- `id` (if present)
- `requirement_text`
- `issues` — detected issues
- `suggested_rewrite` — template rewrite suggestion

## Next Steps
- Externalize rules to a `rules.yaml` for easy tuning.
- Add a **quality score** (0–100).
- Evaluate on an **annotated golden set** (precision/recall).
- Add a simple **UI** (Streamlit) for non-technical users.