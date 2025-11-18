import argparse
import json
import csv
import time
from pathlib import Path
from datetime import datetime
import os

from rich.console import Console
from rich.progress import Progress

# Import gestiti con controlli successivi
try:
    # Prova a importare i componenti necessari
    from llm_conversation import configure, GenerationConfig, GenerativeModel
except ImportError:
    # Se fallisce, imposta le variabili a None per un controllo successivo
    configure, GenerationConfig, GenerativeModel = None, None, None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# --- CONFIGURAZIONE GLOBALE ---
console = Console()

# --- CLASSE FALLBACK ---
# Modello stub locale usato quando il modello remoto non è disponibile.
class StubGenerativeModel:
    def __init__(self, label: str = "local-stub"):
        self.model_name = label

    def generate_content(self, prompt: str):
        class Resp:
            def __init__(self, text: str):
                self.text = text
        stub = {"Score": "EVALUATION_SKIPPED", "Justification": "Fallback stub used: remote model unavailable or unsupported."}
        return Resp(json.dumps(stub, ensure_ascii=False))

# --- CONFIGURAZIONE GEMINI ---

# Verifica che la libreria google.generativeai sia installata
if configure is None or GenerationConfig is None or GenerativeModel is None:
    console.print("[bold red]Libreria 'google.generativeai' non trovata.[/bold red]")
    console.print("Installala con: [bold]pip install --upgrade google-generativeai[/bold]")
    exit(1)

# Carica le variabili d'ambiente da .env se dotenv è disponibile
if load_dotenv:
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

# Ottieni la chiave API
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY")
if not api_key:
    console.print("[bold red]ERRORE: Variabile d'ambiente GOOGLE_API_KEY non impostata.[/bold red]")
    exit(1)

# Configura l'API
configure(api_key=api_key.strip())

# Cerca un modello valido da usare
env_model = os.getenv("MODEL_NAME")
candidate_models = [env_model] if env_model else []
candidate_models.extend(["gemini-pro-latest", "gemini-1.5-pro-latest", "models/text-bison-001"])

json_generation_config = GenerationConfig(
    temperature=0.0,
    response_mime_type="application/json"
)

gemini_model = None
last_exc = None
for candidate in filter(None, candidate_models): # filter(None, ...) rimuove stringhe vuote
    try:
        gemini_model = GenerativeModel(model_name=candidate, generation_config=json_generation_config)
        console.print(f"[green]Modello '{candidate}' inizializzato con successo.[/green]")
        break
    except Exception as e:
        last_exc = e
        console.print(f"[yellow]Impossibile inizializzare il modello '{candidate}': {e}[/yellow]")

# Blocco di controllo per prevenire errori successivi se nessun modello è stato caricato
if gemini_model is None:
    console.print("\n[bold red]ERRORE CRITICO: Impossibile inizializzare qualsiasi modello generativo.[/bold red]")
    console.print(f"L'ultimo errore ricevuto è stato: [italic]{last_exc}[/italic]\n")
    console.print("[bold yellow]Controlla che la chiave API sia valida e che l'API 'Generative Language' sia abilitata nel tuo progetto Google Cloud.[/bold yellow]")
    exit(1)

# --- FUNZIONI HELPER ---

def load_json_config(path: Path) -> dict | list:
    """Carica in modo sicuro un file di configurazione JSON."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]Errore fatale durante il caricamento di '{path}': {e}[/bold red]")
        raise

def format_transcript(conversation_log: list[dict]) -> str:
    """Formatta il log di conversazione in una stringa leggibile.

    Supporta più formati di log: prova chiavi comuni come
    'agent'/'content' oppure 'speaker'/'message' o 'speaker'/'text'.
    """
    lines = []
    for turn in conversation_log:
        if not isinstance(turn, dict):
            continue
        agent = turn.get('agent') or turn.get('speaker') or turn.get('speaker_name') or turn.get('from') or turn.get('role') or 'Unknown'
        content = turn.get('content') or turn.get('message') or turn.get('text') or turn.get('utterance') or turn.get('body') or ''
        try:
            content_str = str(content)
        except Exception:
            content_str = ''
        lines.append(f"{agent}: {content_str}")
    return "\n".join(lines)

def evaluate_single_metric(system_prompt: str, user_prompt: str) -> dict:
    """Chiama l'API di Gemini per valutare una singola metrica, con logica di retry."""
    global gemini_model
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    if gemini_model is None or not hasattr(gemini_model, "generate_content"):
        console.log("[yellow]gemini_model non inizializzato o manca 'generate_content': uso StubGenerativeModel come fallback.[/yellow]")
        gemini_model = StubGenerativeModel()

    for attempt in range(3):
        resp_text = ""
        try:
            response = gemini_model.generate_content(full_prompt)
            resp_text = getattr(response, 'text', str(response))
            result = json.loads(resp_text)
            return {
                "Score": result.get('Score', 'EVALUATION_FAILED'),
                "Justification": result.get('Justification', 'Giustificazione non fornita.'),
                "RawResponse": resp_text,
            }
        except json.JSONDecodeError:
            console.log(f"[yellow]Risposta non JSON (tentativo {attempt+1}). Contenuto: {resp_text}[/yellow]")
        except Exception as e:
            msg = str(e).lower()
            console.log(f"[yellow]Tentativo {attempt + 1}/3 fallito. Errore: {e}. Riprovo...[/yellow]")
            if "not found" in msg or "not supported" in msg or "permission_denied" in msg:
                console.log("[yellow]Errore irreversibile: passo al modello di fallback locale (stub).[/yellow]")
                gemini_model = StubGenerativeModel()
                continue
            time.sleep(5)

    return {"Score": "EVALUATION_FAILED", "Justification": "Gemini non ha risposto correttamente dopo 3 tentativi.", "RawResponse": ""}

def main(logs_dir: Path, output_dir: Path, judge_config_path: Path, metrics_config_path: Path):
    """Orchestra il processo di valutazione."""
    try:
        judge_config = load_json_config(judge_config_path)
        metrics_config = load_json_config(metrics_config_path)
    except Exception:
        return

    if not isinstance(judge_config, dict) or 'system_prompt' not in judge_config:
        console.print("[bold red]Errore: 'config_judge.json' deve essere un oggetto JSON con la chiave 'system_prompt'.[/bold red]")
        return
    if not isinstance(metrics_config, list):
        console.print("[bold red]Errore: 'config_metrics.json' deve essere un array JSON.[/bold red]")
        return

    script_dir = Path(__file__).parent
    if not logs_dir.is_absolute():
        logs_dir = (script_dir / logs_dir).resolve()

    if not logs_dir.exists():
        console.print(f"[bold red]La cartella di input non esiste: '{logs_dir}'.[/bold red]")
        return

    log_files = sorted(list(logs_dir.rglob("*.json")))
    if not log_files:
        console.print(f"[bold red]Nessun file .json trovato in '{logs_dir}'.[/bold red]")
        return

    console.print(f"[bold cyan]Trovati {len(log_files)} log. Inizio valutazione.[/bold cyan]")

    output_dir.mkdir(parents=True, exist_ok=True)
    
    # MODIFICA 1: Rinominiamo il file CSV per chiarire che è un riepilogo.
    csv_path = output_dir / "results_summary.csv"

    metric_names = [metric.get('metric_name', f'UNKNOWN_METRIC_{i}') for i, metric in enumerate(metrics_config)]
    
    # MODIFICA 2: L'header ora contiene solo i nomi delle metriche, non le giustificazioni.
    header = ["Sim_ID", "Approach", "Profile", "Scenario", "Asymmetry"] + metric_names

    # Gestione apertura file CSV con fallback in caso di file bloccato
    used_csv_path = None
    try:
        csv_file = open(csv_path, "w", newline="", encoding="utf-8")
        used_csv_path = csv_path
    except PermissionError:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback = output_dir / f"results_summary_{ts}.csv"
        console.print(f"[yellow]PermissionError: non posso scrivere su '{csv_path}'. Provo con file alternativo: '{fallback}'[/yellow]")
        try:
            csv_file = open(fallback, "w", newline="", encoding="utf-8")
            used_csv_path = fallback
        except Exception as e:
            console.print(f"[bold red]Errore: impossibile aprire file di output: {e}[/bold red]")
            return
    except Exception as e:
        console.print(f"[bold red]Errore aprendo il file di output '{csv_path}': {e}[/bold red]")
        return

    # Raccogliamo anche un unico JSON riepilogativo con tutti i dettagli per conversazione
    all_details = []

    with csv_file as csv_f, Progress(console=console) as progress:
        csv_writer = csv.writer(csv_f)
        csv_writer.writerow(header)

        log_task = progress.add_task("[green]Valutando i log...", total=len(log_files))

        for i, log_file in enumerate(log_files):
            progress.update(log_task, description=f"Processing [bold]{log_file.name}[/bold]")
            # Protezione: salta file JSON vuoti o non-parsabili invece di rompere l'intero run.
            try:
                # controlla dimensione file prima di aprire
                if log_file.stat().st_size == 0:
                    console.print(f"[yellow]File vuoto ignorato: {log_file}[/yellow]")
                    progress.update(log_task, advance=1)
                    continue
                with open(log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
            except json.JSONDecodeError:
                # Tentativo di recupero: rimuoviamo eventuale testo prefisso non-JSON
                try:
                    txt = open(log_file, 'r', encoding='utf-8', errors='replace').read()
                    start = txt.find('{')
                    end = txt.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        candidate = txt[start:end+1]
                        log_data = json.loads(candidate)
                        console.print(f"[yellow]Parsed JSON dopo trimming del prefisso per: {log_file}[/yellow]")
                    else:
                        console.print(f"[yellow]JSON non valido in file (nessun oggetto individuabile), salto: {log_file}[/yellow]")
                        progress.update(log_task, advance=1)
                        continue
                except Exception:
                    console.print(f"[yellow]JSON non valido in file, salto: {log_file}[/yellow]")
                    progress.update(log_task, advance=1)
                    continue
            except Exception as e:
                console.print(f"[yellow]Errore aprendo/parsing {log_file}: {e} - salto file[/yellow]")
                progress.update(log_task, advance=1)
                continue

            # Normalizziamo la struttura della conversazione per chiavi alternative
            conv = log_data.get('conversation') or []
            if isinstance(conv, list):
                for turn in conv:
                    if not isinstance(turn, dict):
                        continue
                    if 'speaker' in turn and 'agent' not in turn:
                        try:
                            turn['agent'] = turn.pop('speaker')
                        except Exception:
                            pass
                    if 'message' in turn and 'content' not in turn:
                        try:
                            turn['content'] = turn.pop('message')
                        except Exception:
                            pass
            if 'conversation' in log_data:
                log_data['conversation'] = conv

            # Estrazione metadati dal nome/percorso del file
            relative_path = log_file.relative_to(logs_dir)
            profile = relative_path.parent.name if len(relative_path.parts) > 1 else "N/A"
            scenario_name = relative_path.stem
            sim_id = f"Sim_{(i+1):03d}_{scenario_name}"
            approach = 'A' if 'approach_a' in log_file.name.lower() else 'B'
            asymmetry_level = scenario_name.split('_')[-1]
            
            # Preparazione dati per la valutazione
            agents = log_data.get("agents", [])

            # Estrarre ground-truth e il system_prompt completo dell'Agent_2 (raw + parsed se JSON)
            gt_obj = agents[0].get("system_prompt", {}) if len(agents) > 0 and isinstance(agents[0], dict) else {}
            ground_truth = json.dumps(gt_obj, ensure_ascii=False)
            transcript = format_transcript(log_data.get("conversation", []))

            # Agent_2: estrai system_prompt raw e prova a parsarlo se contiene JSON
            agent2_persona_raw = ""
            agent2_persona_parsed = {}
            agent2_profile_name = ""
            if len(agents) > 1 and isinstance(agents[1], dict):
                agent2_persona_raw = agents[1].get("system_prompt", "") or ""
                # tentativo semplice di estrarre oggetto JSON contenuto nella stringa
                try:
                    start = agent2_persona_raw.find("{")
                    end = agent2_persona_raw.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        candidate = agent2_persona_raw[start:end+1]
                        parsed = json.loads(candidate)
                        if isinstance(parsed, dict):
                            agent2_persona_parsed = parsed
                            persona_cfg = parsed.get("persona_configuration", {}) or {}
                            agent2_profile_name = persona_cfg.get("profile_name", "") or persona_cfg.get("agent_name", "")
                except Exception:
                    agent2_persona_parsed = {}

            # Aggiungiamo le informazioni del personaggio al prompt del giudice per valutazioni contestuali
            persona_section = ""
            if agent2_profile_name or agent2_persona_parsed:
                persona_section = "\n\n**AGENT_2 PERSONA / CHARACTER METADATA**\n"
                if agent2_profile_name:
                    persona_section += f"- Profile name: {agent2_profile_name}\n"
                if agent2_persona_parsed:
                    persona_section += f"- Persona JSON (estratto): {json.dumps(agent2_persona_parsed, ensure_ascii=False)}\n"
                else:
                    persona_section += f"- Persona raw (non-json): {agent2_persona_raw[:1000]}\n"

            # Rendiamo disponibili queste informazioni anche nei dettagli di output
            # (evaluations viene popolato più avanti; salviamo comunque i raw qui)
            extra_persona_info = {
                "agent2_persona_raw": agent2_persona_raw,
                "agent2_persona_parsed": agent2_persona_parsed,
                "agent2_profile_name": agent2_profile_name,
            }
            
            row = [sim_id, approach, profile, scenario_name, asymmetry_level]
            evaluations = {}

            metric_task = progress.add_task(f"  -> Metriche per {log_file.name}", total=len(metrics_config))
            for metric in metrics_config:
                metric_name = metric.get('metric_name', 'UNKNOWN_METRIC')
                progress.update(metric_task, description=f"  -> Valutando [yellow]{metric_name}[/yellow]")

                # Applicabilità: default = "all". Se configurato diversamente, rispettalo.
                applicable = metric.get("applicable_to", "all")
                applies = False
                if isinstance(applicable, str):
                    applies = (applicable.lower() == "all") or (applicable.upper() == approach)
                elif isinstance(applicable, list):
                    applies = ( "all" in [a.lower() for a in applicable] ) or (approach in applicable)
                if not applies:
                    # scrivi N/A per questa metrica nel CSV e continua
                    row.append("N/A")
                    evaluations[metric_name] = {"Score": "N/A", "Justification": "Metric not applicable for this approach.", "RawResponse": ""}
                    progress.update(metric_task, advance=1)
                    continue

                system_prompt_str = json.dumps(judge_config['system_prompt'], ensure_ascii=False)

                user_prompt_str = f"""
                **CONTESTO DELLA CONVERSAZIONE**
                - Ground Truth (Obiettivi Segreti Agente B): {ground_truth}
                - Trascrizione Completa:\n{transcript}
                {persona_section}

                **METRICA DA VALUTARE**
                - Nome Metrica: "{metric.get('metric_name', 'N/A')}
                - Descrizione: {metric.get('description', 'N/A')}

                **CRITERI DI VALUTAZIONE**
                {json.dumps(metric.get('scoring_criteria', {}), ensure_ascii=False, indent=2)}

                Per favore, valuta la conversazione SOLO in base alla metrica e ai criteri forniti.
                """

                evaluation = evaluate_single_metric(system_prompt_str, user_prompt_str)

                # Normalizza tipi speciali (likert_5 -> int 1..5)
                value_type = metric.get("value_type", "").lower()
                score_to_write = evaluation.get('Score', '')
                if value_type == "likert_5":
                    try:
                        # supporta numeri come "4", "4.0" o anche stringhe
                        si = int(float(str(score_to_write).strip()))
                        if si < 1: si = 1
                        if si > 5: si = 5
                        score_to_write = str(si)
                    except Exception:
                        score_to_write = ""
                else:
                    score_to_write = str(score_to_write)

                # Scrivi solo il punteggio sintetico nel CSV
                row.append(score_to_write)

                # Salviamo comunque l'intera valutazione per il file di dettaglio JSON.
                evaluations[metric_name] = evaluation

                progress.update(metric_task, advance=1)
                time.sleep(1) # Rallenta le chiamate per rispettare i limiti API

            csv_writer.writerow(row)

            # Il salvataggio del JSON di dettaglio per l'audit rimane invariato ed è cruciale.
            details_dir = output_dir / "details"
            details_dir.mkdir(parents=True, exist_ok=True)
            details_path = details_dir / f"{sim_id}__details.json"
            detail_obj = {
                'Sim_ID': sim_id,
                'log_file': str(log_file),
                'evaluations': evaluations,
                'ground_truth': ground_truth,
                'transcript': transcript,
                'agent2_persona': extra_persona_info,
                'evaluated_at': datetime.now().isoformat()
            }
            all_details.append(detail_obj)

            # salva anche file di dettaglio singolo (opzionale, per auditing)
            details_dir = output_dir / "details"
            details_dir.mkdir(parents=True, exist_ok=True)
            details_path = details_dir / f"{sim_id}__details.json"
            with open(details_path, "w", encoding="utf-8") as df:
                json.dump(detail_obj, df, ensure_ascii=False, indent=2)

            progress.remove_task(metric_task)
            progress.update(log_task, advance=1)

    # MODIFICA 4: Aggiorniamo i messaggi finali per riflettere la nuova struttura dei file.
    console.print(f"\n[bold green]Valutazione completata![/bold green]")
    if used_csv_path:
        console.print(f"-> Riepilogo CSV salvato in: '{used_csv_path}'")
    console.print(f"-> Dettagli JSON per l'analisi approfondita salvati in: '{output_dir / 'details'}'")

    # Scriviamo un singolo file JSON riepilogativo contenente tutti i dettagli per conversazione
    summary_json_path = output_dir / "results_details.json"
    try:
        with open(summary_json_path, 'w', encoding='utf-8') as sf:
            json.dump(all_details, sf, ensure_ascii=False, indent=2)
        console.print(f"-> File JSON riepilogativo salvato in: '{summary_json_path}'")
    except Exception as e:
        console.print(f"[yellow]Impossibile scrivere il file JSON riepilogativo: {summary_json_path} - Errore: {e}[/yellow]")
        # fine loop dei log
    # Merge con eventuale results_details.json esistente e scrittura atomica
    final_json = output_dir / "results_details.json"
    merged_map = {}
    if final_json.exists():
        try:
            with open(final_json, "r", encoding="utf-8") as f_exist:
                existing = json.load(f_exist)
                for item in existing:
                    key = item.get("log_file") or item.get("Sim_ID")
                    if key:
                        merged_map[key] = item
        except Exception:
            # se il file esistente è corrotto, lo ignoro e sovrascrivo
            merged_map = {}

    for item in all_details:
        key = item.get("log_file") or item.get("Sim_ID")
        if key:
            merged_map[key] = item  # le nuove entry sovrascrivono le vecchie

    merged_list = list(merged_map.values())
    tmp_path = final_json.with_suffix(".json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as tf:
            json.dump(merged_list, tf, ensure_ascii=False, indent=2)
        os.replace(tmp_path, final_json)  # atomic move
        console.print(f"[green]Aggregated JSON aggiornato: {final_json}[/green]")
    except Exception as e:
        console.print(f"[bold red]Errore scrivendo il JSON aggregato: {e}[/bold red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Valuta i log di conversazione usando il giudice LLM di Google Gemini.")
    parser.add_argument("-i", "--input-dir", type=Path, default="conversation_logs", help="Cartella contenente i log .json.")
    parser.add_argument("-o", "--output-dir", type=Path, default="evaluation_results", help="Cartella dove salvare gli output.")
    parser.add_argument("-c", "--config-dir", type=Path, default="config", help="Cartella contenente i file di configurazione JSON.")
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    config_dir = args.config_dir if args.config_dir.is_absolute() else (script_dir / args.config_dir).resolve()
    
    main(
        logs_dir=args.input_dir,
        output_dir=args.output_dir,
        judge_config_path=config_dir / "config_judge.json",
        metrics_config_path=config_dir / "config_metrics.json"
    )