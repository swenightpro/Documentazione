import re
import glob
import sys
from pathlib import Path
import csv

# Soglia minima consigliata (puoi cambiarla)
MIN_GULPEASE = 45
CSV_PATH = Path("quality/gulpease_results.csv")


def strip_latex(text: str) -> str:
    # Rimuove commenti
    text = re.sub(r'%.*', '', text)
    # Rimuove comandi tipo \command{...} o \command[...]{...}
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', ' ', text)
    # Rimuove ambiente math $...$ e \[...\]
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\\[[^\\]*\\\]', ' ', text)
    # Rimuove restanti backslash singoli
    text = re.sub(r'\\', ' ', text)
    # Spazi multipli -> singolo
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def gulpease_index(text: str) -> float:
    if not text:
        return 0.0
    letters = len(re.findall(r'[A-Za-zÀ-ÿ]', text))
    words = len(re.findall(r'\w+', text))
    sentences = len(re.findall(r'[.!?]+', text))
    if words == 0:
        return 0.0
    if sentences == 0:
        sentences = 1
    # Formula ufficiale Gulpease per testi in italiano
    return 89 + (300 * sentences - 10 * letters) / words


def main():
    tex_files = glob.glob("src/**/*.tex", recursive=True)
    if not tex_files:
        print("Nessun file .tex trovato in src/.")
        sys.exit(0)

    failed = False
    results = []

    print("== Controllo indice Gulpease sui .tex in src/ ==")
    for path in sorted(tex_files):
        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        clean = strip_latex(content)
        g = gulpease_index(clean)
        print(f"{path}: Gulpease = {g:.2f}")
        results.append((path, g))
        if g < MIN_GULPEASE:
            failed = True
            print(
                f"::warning file={path}::Indice Gulpease basso ({g:.2f} < {MIN_GULPEASE})"
            )

    # salva risultati in CSV per il report complessivo
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["file", "gulpease"])
        for path, g in results:
            writer.writerow([path, f"{g:.2f}"])

    print(f"Risultati Gulpease salvati in {CSV_PATH}")

    if failed:
        print("Alcuni documenti hanno indice Gulpease sotto la soglia.")
        sys.exit(1)
    else:
        print("Tutti i documenti rispettano la soglia Gulpease.")
        sys.exit(0)


if __name__ == "__main__":
    main()
