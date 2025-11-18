# Valutazione LLM — Istruzioni rapide

Questo repository contiene uno script di valutazione (`evaluation.py`) che valuta conversazioni generate da agenti LLM secondo metriche definite in `config/config_metrics.json` e impostazioni in `config/config_judge.json`.

Questo README spiega come risolvere il problema "Import 'llm_conversation' could not be resolved", come impostare la chiave API e come eseguire lo script.

---
## Sommario rapido
- Requisiti minimi: Python 3.13
- File principali:
  - `evaluation.py` — script principale di valutazione
  - `config/config_judge.json` — configurazione del giudice (deve contenere `system_prompt`)
  - `config/config_metrics.json` — definizione delle metriche
  - `conversation_logs/` — cartella con i log da valutare

---
## Installazione (consigliata in virtualenv)
Apri PowerShell nella cartella del progetto e crea/attiva un virtualenv (opzionale ma consigliato):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Aggiorna pip ed installa dipendenze utili (facoltative):

```powershell
python -m pip install --upgrade pip
python -m pip install python-dotenv rich
```

Nota: il client ufficiale per Gemini si chiama `google-generativeai`. Se vuoi usare il servizio reale, installalo:

```powershell
python -m pip install --upgrade google-generativeai
```

Se usi il package manager del progetto (hatch/pyproject), aggiungi/installa le dipendenze secondo il tuo workflow.

---
## Impostare la chiave API
Lo script legge la chiave dalle variabili d'ambiente `GOOGLE_API_KEY` o (in fallback) `API_KEY`.

Temporaneo (solo sessione corrente):

```powershell
$env:GOOGLE_API_KEY = "LA_TUA_CHIAVE"
python .\evaluation.py
```

Permanente (per il tuo utente, riavvia PowerShell dopo):

```powershell
setx GOOGLE_API_KEY "LA_TUA_CHIAVE"
```

Supporto `.env` (comodo in sviluppo):
- Copia il file di esempio `.env.example` in `.env` e inserisci la tua chiave.
- Installa `python-dotenv` (vedi sopra). Lo script tenterà di caricare `.env` automaticamente se la libreria è presente.

**Non committare** il file `.env` nel repository.

---
## Modello da usare
Se vuoi usare un modello specifico (ad es. `gemini-pro-latest`), puoi:
- impostare la variabile d'ambiente `MODEL_NAME` prima di eseguire lo script, oppure
- modificare il file `evaluation.py` per cambiare i fallback di default.

Esempio temporaneo:

```powershell
$env:MODEL_NAME = 'gemini-pro-latest'
python .\evaluation.py
```

Lo script prova una lista di modelli candidati (incluso `gemini-pro-latest`). Se il modello non è disponibile o non supporta il metodo richiesto dall'SDK, lo script passerà a un fallback stub locale e produrrà risultati marcati come fallback.

---
## Esecuzione e test rapido
Per validare che i file JSON di configurazione siano corretti, puoi eseguire lo script di validazione incluso:

```powershell
python .\scripts\validate_config.py
```

Esegui la valutazione:

```powershell
python .\evaluation.py
```

Output: i risultati verranno salvati in `evaluation_results/results.csv` per default.

---
## Note sul comportamento e suggerimenti
- Se vedi errori 404 tipo "model ... is not found" o messaggi che indicano che il modello non supporta `generateContent`, prova prima a eseguire `list_models()` con il client ufficiale per ottenere i nomi corretti dei modelli disponibili per il tuo account.
- Per test offline o sviluppo rapido, lo stub locale risponde con un JSON di fallback in modo che lo script produca comunque un output.
