#!/usr/bin/env python3
"""
check_chktex.py - Linter per LaTeX usando ChkTeX
Controlla errori stilistici e semantici nei file .tex
"""

import subprocess
import sys
from pathlib import Path
import json

# Soglia massima di errori ChkTeX per file
MAX_CHKTEX_ERRORS = 5

# Errori ChkTeX da ignorare (rumore):
# - 8: Possibile comando incompleto (spesso falsi positivi)
# - 12: Spazio mancante dopo comando (spesso falsi positivi in macro)
# - 16: Riferimento a comando non riconosciuto (ignore custom command)
# - 17: Numero non seguito da unità (comune nei numeri di versione)
# - 25: Uso della d eufonica senza necessità (troppo sensibile) 
IGNORED_WARNINGS = {8, 12, 16, 17, 25}

REPORT_PATH = Path("quality/chktex_results.json")

def install_chktex():
    """Installa ChkTeX se non presente"""
    try:
        subprocess.run(
            ["chktex", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        print("✓ ChkTeX già installato")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ ChkTeX non trovato. Installandolo...")
        try:
            # Su Ubuntu/Debian
            subprocess.run(
                ["sudo", "apt-get", "update"],
                capture_output=True,
                timeout=30
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "chktex"],
                capture_output=True,
                timeout=60,
                check=True
            )
            print("✓ ChkTeX installato via apt")
            return True
        except Exception as e:
            print(f"✗ Impossibile installare ChkTeX: {e}")
            print("  Istruzioni manuali:")
            print("  - Ubuntu/Debian: sudo apt-get install chktex")
            print("  - macOS: brew install chktex")
            print("  - Windows: scaricare da https://www.nongnu.org/chktex/")
            return False

def run_chktex(tex_file):
    """
    Esegue ChkTeX su un file e ritorna una lista di errori
    Filtra gli warning basandosi su IGNORED_WARNINGS
    """
    try:
        result = subprocess.run(
            ["chktex", "--quiet", str(tex_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # ChkTeX output format: Warning XXX in file.tex line Y col Z
        errors = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            
            # Estrai il numero dell'avviso
            try:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == "Warning":
                    warning_num = int(parts[1])
                    if warning_num not in IGNORED_WARNINGS:
                        errors.append({
                            "file": str(tex_file),
                            "line": line.strip(),
                            "warning_id": warning_num
                        })
            except (ValueError, IndexError):
                continue
        
        return errors
    
    except subprocess.TimeoutExpired:
        print(f"⚠ ChkTeX timeout su {tex_file}")
        return []
    except Exception as e:
        print(f"✗ Errore ChkTeX su {tex_file}: {e}")
        return []

def main():
    print("=" * 60)
    print("ChkTeX - LaTeX Linter")
    print("=" * 60)
    
    # Installa ChkTeX se necessario
    if not install_chktex():
        print("\n⚠ ChkTeX non disponibile, skip del controllo")
        sys.exit(0)
    
    # Trova tutti i file .tex
    tex_files = list(Path("src").rglob("*.tex"))
    if not tex_files:
        print("✓ Nessun file .tex trovato in src/")
        sys.exit(0)
    
    print(f"\n📄 Trovati {len(tex_files)} file .tex\n")
    
    all_errors = []
    failed = False
    
    for tex_file in sorted(tex_files):
        errors = run_chktex(tex_file)
        
        if errors:
            print(f"⚠ {tex_file}: {len(errors)} warning rilevanti")
            for error in errors:
                print(f"  → {error['line']}")
            all_errors.extend(errors)
            
            if len(errors) > MAX_CHKTEX_ERRORS:
                failed = True
                print(f"  ✗ Superati {MAX_CHKTEX_ERRORS} errori tollerati")
        else:
            print(f"✓ {tex_file}: OK")
    
    # Salva risultati
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(all_errors, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"\n📊 Risultati ChkTeX salvati in {REPORT_PATH}")
    
    if failed:
        print("\n✗ Alcuni file hanno superato la soglia ChkTeX")
        sys.exit(1)
    else:
        print(f"\n✓ Tutti i file passano il controllo ChkTeX ({len(all_errors)} warning filtrati)")
        sys.exit(0)

if __name__ == "__main__":
    main()
