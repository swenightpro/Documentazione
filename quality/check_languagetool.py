import glob
import sys
from pathlib import Path
import re
import csv

import language_tool_python

IGNORED_RULES_FOR_COUNT = {
    "MORFOLOGIK_RULE_IT_IT",
    "UNPAIRED_BRACKETS",
    "COMMA_PARENTHESIS_WHITESPACE",
    "WHITESPACE_PUNCTUATION",
}

IGNORED_NAMES = {
    "Biasuzzi",
    "Davide",
    "Bilato",
    "Leonardo",
    "Zanella",
    "Francesco",
    "Romascu",
    "Mihaela-Mariana",
    "Mihaela",
    "Mariana",
    "Ogniben",
    "Michele",
    "Perozzo",
    "Samuele",
    "Ponso",
    "Giovanni",
    "Ergon",
    "Ergon Informatica",
    "NightPRO",
    "branch",
    "Branch",
    "commit",
    "committer",
    "pushata",
    "GitHub Action",
    "GitHub Actions",
    "Teams",
    "Slack",
    "Zoom",
    "Google Meet",
    "PoC",
}

MAX_ERRORS_PER_FILE = 10

REPORT_PATH = Path("quality/quality_report.md")
GULPEASE_CSV = Path("quality/gulpease_results.csv")


def strip_latex_for_lt(text: str) -> str:
    text = re.sub(r'%.*', '', text)
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', ' ', text)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\\[[^\\]*\\\]', ' ', text)
    text = re.sub(r'\\', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def highlight_in_context(match) -> str:
    context = getattr(match, "context", "")
    offset_in_ctx = getattr(match, "offsetInContext", None)
    length = getattr(match, "errorLength", None)

    if not context or offset_in_ctx is None or length is None:
        return context.replace("|", "\\|")

    start = offset_in_ctx
    end = offset_in_ctx + length
    before = context[:start]
    error = context[start:end]
    after = context[end:]

    before = before.replace("|", "\\|")
    error = error.replace("|", "\\|")
    after = after.replace("|", "\\|")

    return f"{before}**{error}**{after}"


def load_gulpease():
    data = {}
    if not GULPEASE_CSV.is_file():
        return data
    with GULPEASE_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                data[row["file"]] = float(row["gulpease"].replace(",", "."))
            except Exception:
                continue
    return data


def find_latest_glossary() -> Path | None:
    """
    Cerca in tutto il repo i file che iniziano con 'glossario' (case insensitive)
    e ritorna quello più recente in base al timestamp del file.
    L'idea è: se spostate il glossario o ne create uno nuovo per RTB, qui lo troviamo
    senza dover aggiornare a mano il path.
    """
    candidates = []
    for p in Path(".").rglob("*.tex"):
        if p.name.lower().startswith("glossario"):
            try:
                mtime = p.stat().st_mtime
            except OSError:
                continue
            candidates.append((mtime, p))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def extract_glossary_terms(glossary_path: Path) -> set[str]:
    """
    Dal file di glossario estraiamo i termini tecnici.
    Nel vostro glossario ogni termine è una \\subsection*{Termine} in appendice,
    quindi qui ci limitiamo a prendere il contenuto delle \\subsection*{...}
    e a usarlo come "parola chiave" da escludere dai controlli.
    È un approccio semplice ma robusto rispetto alle modifiche future.
    """
    text = glossary_path.read_text(encoding="utf-8", errors="ignore")
    terms = set()

    # Prendiamo tutte le \subsection*{...} e ci teniamo il contenuto fra le graffe.
    for m in re.finditer(r"\\subsection\*\{([^}]*)\}", text):
        raw = m.group(1).strip()
        if not raw:
            continue
        # Evitiamo di mettere nel dizionario roba ovviamente generica
        if raw in {"Componenti del Gruppo", "Informazioni Generali", "Introduzione"}:
            continue
        terms.add(raw)

    return terms


def contains_ignored_term(text: str, extra_terms: set[str]) -> bool:
    if not text:
        return False
    tokens = IGNORED_NAMES | extra_terms
    return any(term in text for term in tokens)


def main():
    tex_files = glob.glob("src/**/*.tex", recursive=True)
    if not tex_files:
        print("Nessun file .tex trovato in src/.")
        sys.exit(0)

    tool = language_tool_python.LanguageTool("it")
    failed = False

    gulpease_data = load_gulpease()

    # Prima di tutto proviamo a individuare il glossario più aggiornato e
    # a ricavare da lì le parole tecniche da escludere. Questo tiene
    # allineato il controllo con il glossario che consegnate ai prof.
    glossary_path = find_latest_glossary()
    glossary_terms: set[str] = set()
    if glossary_path is not None:
        print(f"Glossario rilevato: {glossary_path}")
        try:
            glossary_terms = extract_glossary_terms(glossary_path)
        except Exception as e:
            print(f"Impossibile leggere il glossario {glossary_path}: {e}")
            glossary_terms = set()
    else:
        print("Nessun file di glossario trovato, nessun termine tecnico escluso.")

    lines = []
    lines.append("# Quality report (Gulpease & LanguageTool)\n")
    lines.append("Report automatico di qualità sui file LaTeX in `src/`.\n")

    if gulpease_data:
        lines.append("\n## Indice Gulpease\n\n")
        lines.append("| File | Gulpease |\n")
        lines.append("|------|----------|\n")
        for path in sorted(gulpease_data.keys()):
            g = gulpease_data[path]
            lines.append(f"| `{path}` | {g:.2f} |\n")
    else:
        lines.append(
            "\n> Nessun dato Gulpease trovato (file `quality/gulpease_results.csv` mancante).\n"
        )

    print("== Controllo LanguageTool sui .tex in src/ ==")

    for path in sorted(tex_files):
        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        clean = strip_latex_for_lt(content)
        matches = tool.check(clean)
        num_errors = len(matches)
        print(f"{path}: {num_errors} potenziali errori")

        MAX_DETAILS = 50
        considered_errors = 0
        row_index = 0
        rows = []

        for m in matches[:MAX_DETAILS]:
            rule = getattr(m, "rule_id", getattr(m, "ruleId", "UNKNOWN_RULE"))
            issue_type = getattr(m, "ruleIssueType", "")
            msg = m.message.replace("|", "\\|")
            repl = ", ".join(m.replacements[:3]).replace("|", "\\|") or "-"
            ctx = highlight_in_context(m)
            matched_text = getattr(m, "matchedText", "")

            # Se il testo o il contesto contengono un nome del gruppo o un termine del glossario,
            # non ha senso segnalarlo come errore: il glossario è proprio la fonte di verità.
            if contains_ignored_term(matched_text, glossary_terms) or contains_ignored_term(
                ctx, glossary_terms
            ):
                continue

            if rule in {
                "MORFOLOGIK_RULE_IT_IT",
                "UNPAIRED_BRACKETS",
                "COMMA_PARENTHESIS_WHITESPACE",
                "WHITESPACE_PUNCTUATION",
            }:
                continue

            row_index += 1
            rows.append(
                f"| {row_index} | `{rule}` | {issue_type} | {msg} | {repl} | {ctx} |\n"
            )

            if rule not in IGNORED_RULES_FOR_COUNT:
                considered_errors += 1

        # Se non ci sono segnalazioni rilevanti, non aggiungiamo proprio la sezione del file al report.
        if considered_errors == 0:
            continue

        lines.append(f"\n## {path}\n")
        lines.append(f"Totale segnalazioni (tutte le regole): **{num_errors}**\n")

        if rows:
            lines.append(
                "\n| # | Regola | Tipo | Messaggio | Suggerimenti | Contesto |\n"
            )
            lines.append(
                "|---|--------|------|-----------|--------------|---------|\n"
            )
            lines.extend(rows)

        lines.append(
            f"\nSegnalazioni considerate ai fini del fail: **{considered_errors}**\n"
        )

        if considered_errors > MAX_ERRORS_PER_FILE:
            failed = True
            print(
                f"::error file={path}::Troppe segnalazioni rilevanti "
                f"({considered_errors} > {MAX_ERRORS_PER_FILE})"
            )

    # In fondo al report aggiungiamo un riepilogo dei termini che sono stati esclusi
    # in quanto presenti nel glossario. Questo serve sia a documentare la scelta
    # verso i prof, sia a far capire al gruppo cosa il controllo sta "lasciando passare".
    if glossary_path is not None and glossary_terms:
        lines.append("\n## Termini esclusi dal glossario\n\n")
        lines.append(
            f"_Glossario usato_: `{glossary_path}`\n\n"
        )
        lines.append("| Termine |\n")
        lines.append("|---------|\n")
        for term in sorted(glossary_terms):
            lines.append(f"| {term} |\n")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("".join(lines), encoding="utf-8")
    print(f"Report dettagliato scritto in {REPORT_PATH}")

    if failed:
        print("Alcuni file superano la soglia di errori rilevanti consentiti.")
        sys.exit(1)
    else:
        print("Tutti i file rientrano nella soglia di errori rilevanti consentiti.")
        sys.exit(0)


if __name__ == "__main__":
    main()
