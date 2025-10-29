# Guida all'uso dei workflow del repository
1) Per compilare i vostri file latex, caricateli tutti nella cartella `src/`. La build si attiverà in automatico e salverà tutti i rispettivi `.pdf` compilati nella cartella `docs/`, con una struttura di cartelle uguale a quella che abbiamo usato in `src/`.
2) Potete caricare progetti latex mono-file oppure multi-file. Per i progetti multi-file è importante che esista un file `.tex` principale e una cartella obbligatoriamente chiamata `contenuti/` in cui disporre tutti i file secondari del progetto (questo nome è un vincolo tecnico per far funzionare la build).
3) Questione immagini: la compilazione dei progetti latex parte dalla root, dunque per la compilazione delle immagini basta procedere nel seguente modo:
   - aggiungi all'inizio del file latex principale le seguenti direttive:
   ```
   \usepackage{graphicx} % Pacchetto classico per le immagini
   \usepackage{currfile} % Pacchetto per ottenere il percorso del file compilato dinamicamente
   \graphicspath{{src/immagini/}{\currfiledir contenuti/}{\currfiledir contenuti/immagini/}} % Percorsi dove cercare le immagini
   ```
   - Potrai disporre le immagini condivise da tutti i documenti (come il logo) nella cartella `src/immagini/`, e salvare le immagini specifiche dei progetti nelle rispettive cartelle dedicate (`.../progetto/contenuti/` o `.../progetto/contenuti/immagini/`).
   - Infine utilizza il seguente comando per includere l'immagine: `\includegraphics{logo.jpg}` (non serve specificare il percorso)
5) Attenzione: se modificate una immagine mantenendo lo stesso nome del file immagine, la ricompilazione non avverrá in automatico, dunque bisognerá forzarla eliminando il file pdf che vogliamo ricompilare.
6) Potete caricare i file pdf firmati, caricandoli a mano in `docs/` dopo averli rinominati con un nome che termina con `*firmato.pdf` oppure `*signed.pdf` (esempio: `verbale_firmato.pdf`). Questi file infatti pur essendo "orfani" verranno ignorati (e quindi non eliminati) durante il controllo di integritá tra `src/` e `docs/` grazie al loro nome specifico.
7) Dettaglio da evidenziare: la build si attiverà anche se elimini, modifichi o aggiungi un file .pdf da docs/. Questo accade perché il sistema deve garantire che i PDF in docs/ siano sempre e solo quelli generati dalla build stessa e non modificati a mano (quindi li rigenera o li elimina se necessario).
8) Report sui risultati di compilazione della build: potete controllare quali file sono stati effettivamente compilati correttamente, e quali hanno fallito la compilazione, nel file `report.md` (si aggiorna ad ogni build chiaramente).
9) Da evitare l'utilizzo di rebase in favore del merge per creare meno problemi.
10) Processo di creazione e pubblicazione della pagina web dedicata ai documenti del repository: i file `.pdf` che si trovano direttamente in `docs/` (senza passare per cartelle intermedie) vengono completamente ignorati dallo script che crea la struttura dei documenti per il sito web, di conseguenza non saranno visualizzati (per il nostro progetto questo sará un non problema dato che non é previsto accada).
11) Nomenclatura file pdf: strutturare il nome del file latex mettendo la versione alla fine (es: nome_v0.1.5.tex). Quando si inserisce un file `.pdf` firmato a mano, si deve aggiungere la parola `firmato` o `signed` alla fine nel nome del file pdf (es: nome_v0.1.5_firmato.pdf). L'ordine è importante per garantire allo script python del sito web di riconoscere correttamente versione del file e presenza della firma. Per fare gli spazi si può tranquillamente usare `_` o fare il classico spazio (verrà gestito correttamente anche il `-` ma é da preferirsi per le date).

# Obiettivi della build di compilazione automatica dei file LaTeX

L’obiettivo della build implementata con github action è di compilare automaticamente i progetti latex caricati nel repository, mantenendo **coerenza e consistenza** tra i file sorgenti latex e i rispettivi pdf.
Nello specifico la build garantisce che:
- `src/` e `docs/` siano perfettamente allineati;  
- ogni file pdf presente in `docs/` é generato esclusivamente dalla build di github action
- i documenti latex che falliscono la compilazione non avranno il rispettivo documento pdf (nemmeno la versione precedente alla build)
- non esistono PDF orfani o obsoleti;

Attenzione: tutto ció non vale per i file firmati, dovranno essere gestiti manualmente.

# Struttura logica del processo

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
