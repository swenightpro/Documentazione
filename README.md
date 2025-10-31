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
- **Website:** [https://swenightpro.github.io/Documentazione/](https://swenightpro.github.io/Documentazione/)


## 2. Architettura dell'Organizzazione

Il progetto è articolato su due repository distinti, ospitati all'interno dell'organizzazione del gruppo, al fine di mantenere una netta separazione tra la documentazione di progetto e l'implementazione del prodotto software.

-   📄 **Repository Documentazione:** [https://github.com/swenightpro/Documentazione](https://github.com/swenightpro/Documentazione)
-   💻 **Repository del Prodotto Software:** *`in assegnazione...`*


## 3. Contenuti del repository

- **`.github/workflows/`**: Contiene i workflow GitHub Actions utilizzati per automatizzare la compilazione dei file LaTeX in PDF (build_latex.yml) e la pubblicazione dei documenti tramite GitHub Pages (deploy_pages.yml).

- **`src/`**: Contiene i file sorgente LaTeX (.tex) e i relativi asset utilizzati per la compilazione dell'intera documentazione.

- **`docs/`**: Contiene le versioni finali e compilate (.pdf) di tutti i documenti prodotti.

- **`site/`**: Contiene il codice sorgente del sito web pubblicato tramite GitHub Pages (HTML/CSS/JS) e uno script Python che, durante il workflow di build e deploy, scansiona la directory docs/ e genera un file JSON con la struttura aggiornata dei documenti, utilizzato per popolare il sito con i contenuti aggiornati.

- **`template/`**: Contiene i file modello messi a disposizione del team per la stesura dei documenti.

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

