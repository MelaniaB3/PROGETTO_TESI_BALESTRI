## Uso della cartella conversation_logs

Questa cartella contiene le conversazioni generate che il programma userà in formato JSON. Per far funzionare correttamente il progetto, aggiungi qui i file JSON delle conversazioni seguendo le linee guida sotto.

- Cosa inserire: file .json che rappresentano una o più conversazioni.
- Nome file consigliato: usa nomi descrittivi e senza spazi, ad esempio `2025-11-10_customer-support.json` o `faq_it.json`.
- Formato minimo consigliato: ogni file dovrebbe contenere un oggetto con almeno una proprietà `messages` che è un array di messaggi. Ogni messaggio può avere una `role` e un `content`.

Esempio minimo di struttura JSON:

```json
{
	"id": "convo-001",
	"title": "Esempio conversazione",
	"messages": [
		{"role": "user", "content": "Ciao, come posso resettare la password?"},
		{"role": "assistant", "content": "Per resettare la password, segui questi passaggi..."}
	]
}
```

Suggerimenti:
- Mantieni i campi consistenti tra file (stesse chiavi per i messaggi) per facilitare il parsing.
- Evita caratteri speciali nei nomi dei file; usa trattini o underscore per separare parole.
- Se generi molte conversazioni, raggruppale in sottocartelle e aggiungi un file README locale con note sul contenuto.

Problemi o domande: aggiungi un issue nel repository o contatta il manutentore del progetto.

Grazie per aver mantenuto questa cartella ordinata — rende più semplice il testing e l'uso dei dati.
