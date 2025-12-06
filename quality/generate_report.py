#!/usr/bin/env python3
"""
generate_report.py - Genera il report consolidato qualità
Combina risultati di Gulpease, LanguageTool e ChkTeX
"""

import json
from pathlib import Path
from datetime import datetime

def load_json_safe(path):
    """Carica JSON in modo sicuro, ritorna dict vuoto se non esiste"""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠ Errore lettura {path}: {e}")
        return {}

def main():
    quality_dir = Path("quality")
    
    # Leggi i risultati da tutti i check
    gulpease_csv = quality_dir / "gulpease_results.csv"
    chktex_json = quality_dir / "chktex_results.json"
    languagetool_report = quality_dir / "quality_report.md"
    
    report_lines = []
    report_lines.append("# Quality Report Consolidato\n\n")
    report_lines.append(f"**Generato:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
    
    # ====================
    # SEZIONE GULPEASE
    # ====================
    report_lines.append("## 📊 Indice Gulpease (Leggibilità Italiana)\n\n")
    
    if gulpease_csv.exists():
        with gulpease_csv.open() as f:
            lines = f.readlines()
        
        if len(lines) > 1:
            report_lines.append("| File | Gulpease Score | Livello |\n")
            report_lines.append("|------|----------------|--------|\n")
            
            for line in lines[1:]:  # Skip header
                parts = line.strip().split(";")
                if len(parts) == 2:
                    file, score = parts
                    try:
                        score_float = float(score)
                        if score_float >= 80:
                            level = "✓ Facile"
                        elif score_float >= 60:
                            level = "✓ Medio"
                        elif score_float >= 45:
                            level = "⚠ Difficile"
                        else:
                            level = "✗ Molto Difficile"
                        report_lines.append(f"| `{file}` | {score_float:.2f} | {level} |\n")
                    except ValueError:
                        continue
        else:
            report_lines.append("> Nessun dato Gulpease disponibile\n\n")
    else:
        report_lines.append("> Nessun file gulpease_results.csv trovato\n\n")
    
    # ====================
    # SEZIONE CHKTEX
    # ====================
    report_lines.append("\n## 🔍 ChkTeX (LaTeX Linter)\n\n")
    
    chktex_data = load_json_safe(chktex_json)
    
    if isinstance(chktex_data, list) and chktex_data:
        report_lines.append(f"**Totale warning rilevanti:** {len(chktex_data)}\n\n")
        
        # Raggruppa per file
        by_file = {}
        for error in chktex_data:
            file = error.get("file", "unknown")
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(error)
        
        for file in sorted(by_file.keys()):
            errors = by_file[file]
            report_lines.append(f"### {file}\n\n")
            report_lines.append(f"- **Warning trovati:** {len(errors)}\n\n")
            for error in errors[:5]:  # Max 5 per file
                report_lines.append(f"  - {error.get('line', 'N/A')}\n")
            if len(errors) > 5:
                report_lines.append(f"  - ... e {len(errors) - 5} altri\n")
            report_lines.append("\n")
    else:
        report_lines.append("> ✓ Nessun warning ChkTeX rilevante\n\n")
    
    # ====================
    # SEZIONE LANGUAGETOOL
    # ====================
    report_lines.append("\n## ✍️ LanguageTool (Grammatica & Ortografia)\n\n")
    
    if languagetool_report.exists():
        with languagetool_report.open() as f:
            content = f.read()
        
        # Estrai summary dal file
        if "Segnalazioni considerate ai fini del fail" in content:
            report_lines.append("> Vedi il file `quality_report.md` per i dettagli completi\n\n")
            # Conta errori totali
            error_count = content.count("Segnalazioni considerate ai fini del fail:")
            report_lines.append(f"- **File con segnalazioni:** {error_count}\n")
        else:
            report_lines.append("> ✓ Nessuna segnalazione LanguageTool significativa\n\n")
    else:
        report_lines.append("> ✓ Nessun file quality_report.md trovato\n\n")
    
    # ====================
    # FOOTER
    # ====================
    report_lines.append("\n---\n\n")
    report_lines.append("## 📌 Come leggere questo report\n\n")
    report_lines.append("- **Gulpease**: Target 60-80 per documentazione tecnica universitaria\n")
    report_lines.append("- **ChkTeX**: Errori stilistici LaTeX (rumore filtrato automaticamente)\n")
    report_lines.append("- **LanguageTool**: Problemi grammaticali e ortografici rilevanti\n\n")
    report_lines.append("> Per il dettaglio completo, scarica l'artefatto `quality-report-*` da GitHub Actions\n")
    
    # Salva il report consolidato
    output_path = quality_dir / "QUALITY_SUMMARY.md"
    output_path.write_text("".join(report_lines), encoding="utf-8")
    print(f"✓ Report consolidato generato: {output_path}")

if __name__ == "__main__":
    main()
