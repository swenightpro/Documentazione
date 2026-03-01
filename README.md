# Documentazione del Progetto di Ingegneria del Software
### Anno Accademico 2025/2026

---


## 1. Informazioni Generali

- **Corso:** Ingegneria del Software
- **Corso di Laurea:** Informatica (L-31)
- **Università:** Università degli Studi di Padova
- **Anno Accademico:** 2025/2026
- **Gruppo di Lavoro:** NightPRO
- **Email:** [swe.nightpro@gmail.com](mailto:swe.nightpro@gmail.com)
- **Sito Web:** [https://swenightpro.github.io/Documentazione/](https://swenightpro.github.io/Documentazione/)


## 2. Struttura dei Repository

Questo repository ospita la documentazione ufficiale prodotta dal gruppo **NightPro**.
Il codice sorgente del software **SmartOrder** è invece distribuito su due repository distinti, corrispondenti alle fasi di sviluppo del prodotto:

- **[SmartOrder-PoC](https://github.com/swenightpro/SmartOrder-PoC)**: Codice relativo al *Proof of Concept* (Requirements and Technology Baseline).
- **SmartOrder-MVP** _(Coming Soon)_: Repository destinato allo sviluppo del *Minimum Viable Product* (Product Baseline).

## 3. Contenuti del repository

- **`.github/workflows/`**: Contiene le definizioni delle GitHub Actions per l'automazione del ciclo di vita del progetto: compilazione dei documenti (`build_latex.yml`), pubblicazione del sito web (`deploy_pages.yml`) e analisi della qualità con generazione di report (`quality_checks.yml`).

- **`src/`**: Contiene i file sorgente LaTeX (.tex) e i relativi asset utilizzati per la compilazione dell'intera documentazione.

- **`docs/`**: Contiene le versioni finali e compilate (.pdf) di tutti i documenti prodotti.

- **`site/`**: Contiene il codice sorgente del sito web pubblicato tramite GitHub Pages (HTML/CSS/JS) e uno script Python che, durante il workflow di build e deploy, scansiona la directory docs/ e genera un file JSON con la struttura aggiornata dei documenti, utilizzato per popolare il sito con i contenuti aggiornati.

- **`quality/`**: Contiene gli script e le configurazioni necessarie per il workflow `quality_checks.yml`.

- **`report.md`**: File generato automaticamente dal workflow di build dei file LaTeX: fornisce una panoramica dei risultati di compilazione e include link diretti ai PDF prodotti per una rapida verifica.


## 4. Componenti del Gruppo

Il gruppo di lavoro NightPro è composto dai seguenti membri:

| Cognome         | Nome            | Matricola |
| :-------------- | :-------------- | :-------- |
| Biasuzzi        | Davide          | 2111000   |
| Bilato          | Leonardo        | 2071084   |
| Zanella         | Francesco       | 2116442   |
| Romascu         | Mihaela-Mariana | 2079726   |
| Ogniben         | Michele         | 2042325   |
| Perozzo         | Samuele         | 2110989   |
| Ponso           | Giovanni        | 2000558   |

