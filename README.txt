# 🎻 Collective IMPROV (Simulazione)

Uno strumento modulare di sentiment analysis basato sull'IA che utilizza Google Gemini per elaborare i messaggi del pubblico in tempo reale e inviare aggiornamenti parametrici adattivi tramite OSC (Open Sound Control).

---

## Panoramica (Overview)

Il sistema riceve in ingresso dei messaggi da parte del pubblico, li raggruppa e li invia a Gemini per l'analisi. I parametri risultanti (es. dinamica, timbro, frammentazione ritmica) vengono poi spediti via OSC a Max/MSP.

La latenza in ogni fase della pipeline viene misurata e registrata in performance_report.txt.

---

## Struttura del Progetto

viola_analyzer/
├── config.py          # Tutte le costanti: chiave API, impostazioni OSC, tempistiche, parametri iniziali
├── gemini_client.py   # Wrapper per l'API di Gemini — restituisce (parsed_json, api_latency_ms)
├── logger.py          # PerformanceLogger — scrive su file il dettaglio della latenza per ogni ciclo
├── main.py            # Punto di ingresso CLI: simula, esci o inserisci messaggi manualmente
├── osc_handler.py     # Client UDP OSC — send_params(params, ramp_ms)
├── processor.py       # Stato condiviso, audience_buffer, loop di analisi, calcolo della latenza
├── simulation.py      # Simulazione casuale: 9 gruppi di scenari distribuiti su 10 minuti
└── README.md

---

## Requisiti

- Python 3.10+
- Consulta requirements.txt per le dipendenze

Installa le dipendenze:
pip install -r requirements.txt

---

## Configurazione

Modifica config.py per impostare i tuoi valori prima dell'avvio:

- GEMINI_API_KEY: La tua chiave API di Google Gemini (Default: "...")
- GEMINI_MODEL: Identificatore del modello Gemini (Default: "models/gemini-2.5-flash")
- OSC_IP: IP di destinazione per i messaggi OSC (Default: "127.0.0.1")
- OSC_PORT: Porta di destinazione per i messaggi OSC (Default: 8000)
- K_INTERVAL: Intervallo del ciclo di analisi in secondi (Default: 60)
- SIMULATION_DURATION: Durata totale della simulazione in secondi (Default: 600)

---

## Utilizzo

python main.py

Una volta avviato, vedrai un prompt dei comandi. Comandi disponibili:
- simulate: Avvia la simulazione casuale del pubblico di 10 minuti
- exit: Chiudi il programma
- (qualsiasi testo): Inserisci manualmente un messaggio nel buffer

---

## Simulazione

La simulazione (simulation.py) attinge da 9 gruppi di scenari che coprono una gamma di stati d'animo del pubblico. I messaggi vengono distribuiti casualmente all'interno della finestra di 10 minuti utilizzando random.uniform(5, 540), rispecchiando il comportamento imprevedibile del pubblico nel mondo reale.

---

## Metriche di Latenza

Ogni ciclo di analisi riporta le seguenti metriche in performance_report.txt:

- api_ms: Solo il tempo di round-trip HTTP di Gemini
- llm_to_update_ms (*): Dall'inizio della chiamata Gemini al completamento dell'invio OSC (metrica chiave)
- cycle_ms: Tempo di elaborazione completo, incluso lo svuotamento del buffer
- avg_msg_wait_ms: Tempo medio di permanenza dei messaggi nel buffer prima dell'elaborazione
- max_e2e_ms: Dal messaggio più vecchio nel batch all'invio OSC (esperienza utente nel peggiore dei casi)

* llm_to_update_ms è la metrica di lantenze principale: misura la rapidità con cui il sistema traduce l'input del pubblico in un aggiornamento dei parametri.

---

## Output

- Console: riepiloghi dei cicli in tempo reale con informazioni sulla latenza
- performance_report.txt: registro completo per ciascun ciclo, scritto nella directory di lavoro

---

## Note

- I messaggi OSC vengono inviati a OSC_IP:OSC_PORT via UDP — assicurati che il tuo sistema di destinazione sia in ascolto.
- Se non è attivo alcun ricevitore OSC, l'invio fallirà silenziosamente (UDP è un protocollo di tipo fire-and-forget).
- Ogni messaggio viene marcato con un timestamp al momento dell'inserimento in add_message() tramite time.perf_counter(), per un tracciamento accurato dei tempi di attesa.
