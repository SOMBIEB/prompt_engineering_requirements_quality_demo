
import argparse
import re
import sys
from pathlib import Path
import pandas as pd

VAGUE_TERMS = [
    "rapide", "rapidement", "convivial", "conviviale", "lisible", "suffisant",
    "assez grand", "agréable", "optimal", "performant", "robuste", "léger", "sûr", "sécurisé"
]

SUBJECTIVE_TERMS = ["convivial", "conviviale", "lisible", "clair", "claire", "agréable", "intuitif", "intuitive"]
AND_OR_PATTERN = r"\bet\/?ou\b"
UNIT_NUMBER_PATTERN = r"\b\d+(?:[\,\.]\d+)?\s*(?:v|a|w|°c|ms|s|kg|m|cm|mm|db|kbit/s|hz|khz|mhz|g)\b"
NUMBER_ONLY_PATTERN = r"\b\d+(?:[\,\.]\d+)?\b(?!\s*(?:v|a|w|°c|ms|s|kg|m|cm|mm|db|kbit/s|hz|khz|mhz|g))"
MULTI_ACTION_PATTERN = r"\b(et|,|;)\b.*\b(démarrer|initialiser|envoyer|activer|désactiver)\b"
UNSPECIFIED_COND_TERMS = ["si un problème survient", "quand c’est nécessaire", "si nécessaire", "au besoin"]

def detect_issues(text: str):
    t = str(text).lower()
    issues = []

    if re.search(AND_OR_PATTERN, t):
        issues.append("AND_OR")

    if any(term in t for term in VAGUE_TERMS):
        issues.append("VAGUE_TERM")

    if any(term in t for term in SUBJECTIVE_TERMS):
        issues.append("SUBJECTIVE")

    if re.search(NUMBER_ONLY_PATTERN, t) and not re.search(UNIT_NUMBER_PATTERN, t):
        issues.append("UNIT_MISSING")

    if any(phrase in t for phrase in UNSPECIFIED_COND_TERMS):
        issues.append("UNSPECIFIED_CONDITION")

    if re.search(MULTI_ACTION_PATTERN, t):
        issues.append("MULTIPLE_REQUIREMENTS")

    if "rapidement" in t or "vite" in t:
        issues.append("UNMEASURABLE")

    if "protég" in t and ("comment" not in t and "norme" not in t and "iso" not in t and "aes" not in t):
        issues.append("UNSPECIFIC_SECURITY")

    return sorted(set(issues))

def suggest_rewrite(text: str, issues: list):
    t = str(text)
    suggestion = None

    if "AND_OR" in issues:
        suggestion = t.replace("et/ou", "et").replace("ET/OU", "et")
        suggestion += " (si l’affichage d’un seul paramètre est requis, le préciser dans la configuration)."

    if "VAGUE_TERM" in issues or "UNMEASURABLE" in issues:
        suggestion = "Remplacer les termes vagues par des critères mesurables. Exemple : "
        if any(w in t.lower() for w in ["rapide", "rapidement", "vite"]):
            suggestion += "« Le système doit s’éteindre en moins de 5 s »."
        elif "léger" in t.lower():
            suggestion += "« Le dispositif doit peser moins de 3 kg »."
        elif "robuste" in t.lower():
            suggestion += "« Le dispositif doit résister à une chute de 1 m sans dommage fonctionnel »."
        elif any(w in t.lower() for w in ["convivial", "lisible", "clair"]):
            suggestion += "« Le texte doit être lisible à 50 cm avec un contraste ≥ 4.5:1 »."
        else:
            suggestion += "« Remplacer par une valeur numérique et une unité vérifiable »."

    if "SUBJECTIVE" in issues and suggestion is None:
        suggestion = "Remplacer les termes subjectifs par des critères objectifs et testables (valeurs numériques, normes, conditions de test)."

    if "UNIT_MISSING" in issues:
        suggestion = "Ajouter les unités manquantes (ex.: V, A, W, °C, ms, kg, etc.)."

    if "UNSPECIFIED_CONDITION" in issues:
        suggestion = "Spécifier la condition/événement déclencheur mesurable (ex.: « si la température dépasse 80 °C pendant 5 s, la LED clignote à 2 Hz »)."

    if "MULTIPLE_REQUIREMENTS" in issues:
        suggestion = "Scinder en exigences atomiques (une action/objectif par exigence)."

    if "UNSPECIFIC_SECURITY" in issues:
        suggestion = "Préciser la mesure de sécurité et/ou la norme (ex.: « chiffrer en AES-256, rotation des clés toutes les 24 h »)."

    return suggestion

def main():
    parser = argparse.ArgumentParser(description="Analyse simple de la qualité des exigences (sans API).")
    parser.add_argument("--input", required=True, help="Chemin du fichier Excel d'entrée (doit contenir 'requirement_text').")
    parser.add_argument("--output", required=True, help="Chemin du fichier Excel de sortie (rapport).")
    parser.add_argument("--sheet", default=None, help="Nom de la feuille à lire (défaut: première).")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        print(f"[ERREUR] Fichier introuvable : {in_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_excel(in_path, sheet_name=args.sheet)
    if "requirement_text" not in df.columns:
        print("[ERREUR] La colonne 'requirement_text' est requise.", file=sys.stderr)
        sys.exit(1)

    results = []
    for _, row in df.iterrows():
        rid = row.get("id", "")
        text = row["requirement_text"]
        issues = detect_issues(text)
        suggestion = suggest_rewrite(text, issues)
        results.append({
            "id": rid,
            "requirement_text": text,
            "issues": ", ".join(issues) if issues else "",
            "suggested_rewrite": suggestion if suggestion else ""
        })

    out_df = pd.DataFrame(results)

    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        out_df.to_excel(writer, index=False, sheet_name="report")
        df.to_excel(writer, index=False, sheet_name="input_sample")

    print(f"[OK] Rapport généré : {out_path}")

if __name__ == "__main__":
    main()
