import glob
import sys
from pathlib import Path
import re

import language_tool_python

# Numero massimo di errori accettati per file (puoi cambiarlo)
MAX_ERRORS_PER_FILE = 15

def strip_latex_for_lt(text: str) -> str:
    # Simile a quello di prima, ma lasciamo un po' più di testo
    text = re.sub(r'%.*', '', text)
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', ' ', text)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\\[[^\\]*\\\]', ' ', text)
    text = re.sub(r'\\', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    tex_files = glob.glob("src/**/*.tex", recursive=True)
    if not tex_files:
        print("Nessun file .tex trovato in src/.")
        sys.exit(0)

    tool = language_tool_python.LanguageTool('it')
    failed = False

    print("== Controllo LanguageTool sui .tex in src/ ==")
    for path in tex_files:
        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        clean = strip_latex_for_lt(content)
        matches = tool.check(clean)
        num_errors = len(matches)
        print(f"{path}: {num_errors} potenziali errori")

        for m in matches[:20]:
            rule = getattr(m, "rule_id", getattr(m, "ruleId", "UNKNOWN_RULE"))
            offset = getattr(m, "offset", -1)
            msg = f"{rule}: {m.message} (offset {offset})"
            print(f"::warning file={path}::{msg}")


        if num_errors > MAX_ERRORS_PER_FILE:
            failed = True
            print(f"::error file={path}::Troppe segnalazioni ({num_errors} > {MAX_ERRORS_PER_FILE})")

    if failed:
        print("Alcuni file superano la soglia di errori consentiti.")
        sys.exit(1)
    else:
        print("Tutti i file rientrano nella soglia di errori consentiti.")
        sys.exit(0)

if __name__ == "__main__":
    main()
