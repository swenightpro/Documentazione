# Guida all'uso del compilatore automatico del repository
1) I progetti latex vanno caricati nell'apposita cartella src. Potete caricare progetti latex mono-file oppure multi-file. Per i progetti multi-file è importante che esista un file `.tex` principale e una cartella obbligatoriamente chiamata `contenuti/` in cui disporre tutti i file secondari del progetto (questo nome è un vincolo tecnico per far funzionare la build).
2) Attenzione: se si modifica una immagine mantenendo lo stesso nome del file immagine, la ricompilazione non avverrá in automatico, dunque bisognerá forzarla eliminando il file pdf che vogliamo ricompilare.
3) I file `.pdf` firmati devono essere caricati a mano in `docs/` dopo averli rinominati con un nome che termina con `firmato.pdf` oppure `signed.pdf` (esempio: `verbale_v0.2_firmato.pdf`). Questi file infatti pur essendo "orfani" verranno ignorati dal controllo di integritá (e quindi non eliminati) tra `src/` e `docs/` grazie al loro nome specifico.
4) La build si attiverà anche se elimini, modifichi o aggiungi un file .pdf da docs/. Questo perché il sistema deve garantire che i PDF in docs/ siano sempre e solo quelli generati dalla build (quindi li rigenera o li elimina se necessario).
5) Report sui risultati di compilazione della build: potete controllare quali file sono stati effettivamente compilati correttamente, e quali hanno fallito la compilazione, nel file `report.md` (si aggiorna ad ogni build chiaramente).
6) Da evitare l'utilizzo di rebase in favore del merge per creare meno problemi.
7) I file `.pdf` che si trovano direttamente in `docs/` (senza passare per cartelle intermedie) vengono completamente ignorati dallo script che crea la struttura dei documenti per il sito web, di conseguenza non saranno visualizzati (per il nostro progetto questo sará un non problema dato che non é previsto accada).
8) Nomenclatura file pdf: strutturare il nome del file latex mettendo la versione alla fine (es: nome_v0.1.5.tex). Quando si inserisce un file `.pdf` firmato a mano, si deve aggiungere la parola `firmato` o `signed` alla fine nel nome del file pdf (es: nome_v0.1.5_firmato.pdf). L'ordine è importante per garantire allo script python del sito web di riconoscere correttamente versione del file e presenza della firma. Per fare gli spazi si può usare `_` o il classico spazio. Utilizzare il `-` per le date.
9) È possibile l'attivazione dei workflow anche manualmente direttamente tramite pulsante dedicato in github action.

# Obiettivi della build di compilazione automatica

L’obiettivo della build implementata con github action è di compilare automaticamente i progetti latex caricati nel repository, mantenendo **coerenza e consistenza** tra i file sorgenti latex e i rispettivi pdf.
Nello specifico la build garantisce che:
- `src/` e `docs/` siano perfettamente allineati;  
- ogni file pdf presente in `docs/` é generato esclusivamente dalla build di github action
- i documenti latex che falliscono la compilazione non avranno il rispettivo documento pdf (nemmeno la versione precedente alla build)
- non esistono PDF orfani o obsoleti;

Attenzione: tutto ció non vale per i file firmati, dovranno essere gestiti manualmente.

# Come funziona il file di compilazione automatica?

### Step 1 – Rilevazione modifiche
- Viene individuato l’ultimo commit creato dalla build automatica (`LAST_COMPILED`) e confrontato con `HEAD`.
- Dal diff si ottiene una lista unica di PDF da rigenerare, composta da:
  - tutti i `.tex` modificati/aggiunti/rinominati (se un file è in una cartella `contenuti/`, si considera il relativo file padre nella stessa directory);
  - tutti i `.pdf` in `docs/` modificati/aggiunti/rinominati manualmente (non orfani).

### Step 2 – Pulizia
- Si eliminano i PDF corrispondenti agli elementi identificati nello Step 1 (se esistono).
- Si eliminano i PDF orfani (`.pdf` presenti in `docs/` senza il rispettivo `.tex` in `src/`).
  - Eccezione: i file che terminano con `firmato.pdf` o `signed.pdf` non vengono eliminati se orfani.

### Step 3 – Creazione della lista di compilazione
- Scansionando `src/` si genera un lista di file `.tex` da compilare (detta `compile_list.txt`), composta da tutti i file `.tex` in `src/` a cui manca il rispettivo `.pdf` in `docs/`. Nella scansione si escludono i file nelle cartelle `contenuti/`.

### Step 4 – Compilazione e report
- I file in `compile_list.txt` vengono compilati con `latexmk` dentro l’immagine Docker `ghcr.io/xu-cheng/texlive-full:latest`.
- Viene generato/aggiornato il `report.md` con:
  - ✅ elenco dei `.pdf` compilati correttamente (con link ai file);
  - ❌ elenco dei documenti che hanno fallito (con link alla build).
- Se la lista è vuota, il report indicherá che non è stata necessaria alcuna compilazione.

### Step 5 – Commit finale
- Se sono stati generati o aggiornati PDF, il builder crea un commit automatico: `Automated LaTeX build (base: <SHA>)` dove `<SHA>` è il commit della precedente build automatica ritenuta coerente.  
- Questo commit diventa il nuovo punto di riferimento per la prossima build (in pratica, ogni commit “Automated LaTeX build”rappresenta uno snapshot coerente tra `src/` e `docs/`

# Informazioni di compilazione
- Compilatore: `latexmk`  
- Ambiente: Docker `ghcr.io/xu-cheng/texlive-full`
