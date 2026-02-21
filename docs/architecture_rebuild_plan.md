# Architektur-Umbauplan (CLAUDE.md + Nexus Session Plan Alignment)

Diese Datei beschreibt den Delta zwischen **aktuellem Local-Baseline-Code** und dem in `claude.md` / `nexus_session_plan.md` definierten **Produktionsziel**.

## 1) Was wurde grundlegend verändert?

Aktuell läuft das Projekt stark auf **in-memory und stdlib Baselines** (für schnelle lokale Iteration), während der Plan eine produktionsnahe Architektur mit echten Providern vorgibt.

## 2) Delta-Matrix: Ist-Zustand vs Zielbild

| Bereich | Aktuell (Ist) | Ziel laut Plan | Erforderlicher Umbau |
|---|---|---|---|
| Settings/Config | `dataclass` in `src/config.py` + `os.getenv` | `pydantic-settings` inkl. strikter Validierung | Settings auf Pydantic umstellen, Secrets/URLs strikt validieren |
| DB/Event Store | `InMemorySupabaseClient` | echter Supabase-Client + tenant-scoped RLS | Repository-Layer + Supabase Adapter implementieren |
| Observability | `InMemoryLangfuseClient` | Langfuse Cloud Traces/Spans + Kostenmetriken | Langfuse SDK Adapter + 18-Felder Logging vollständig mit Traces |
| Memory | lokale Strukturen | Redis + pgvector (tenant-scoped) | Redis/pgvector Adapter + Tokenbudget enforcement via tiktoken |
| Channels | vereinfachte Adapter | Telegram (aiogram) + WebSocket streaming + tenant mapping | echte Channel-Runtime + disclosure/streaming-Endpunkte |
| Eval Runner | deterministische local checks | Live-Agent against suite mit Tokens/Latenz/Grounding | Runner an Live `/chat` koppeln + Metriken aus Decision Logs |
| Calibration | JSON Input-File | Langfuse-basierte Analyse je Tenant | Langfuse Export Reader + automatische Gewichts-Empfehlungen |

## 3) Sofortmaßnahme umgesetzt

Als Brücke wurde ein **Runtime-Mode Adapter-Schnitt** ergänzt:

- `RUNTIME_MODE=local|production` in `src/config.py`
- `src/db/client.py` mit `create_event_store(...)`
- `src/observability/client.py` mit `create_decision_logger(...)`
- `src/main.py` und `src/agent/loop.py` nutzen diese Factory-Funktionen

Damit bleibt Local-Entwicklung stabil, aber die Produktionsadapter können jetzt schrittweise hinter klaren Schnittstellen ersetzt werden.

## 4) Reihenfolge für den Umbau (empfohlen)

1. **Pydantic Settings Migration** (`src/config.py`) 
2. **Supabase Adapter + Repository Layer** (`src/db/*`) 
3. **Langfuse Adapter + Tracing in Agent Loop** (`src/observability/*`, `src/agent/loop.py`) 
4. **Redis/pgvector Memory Backend** (`src/memory/*`) 
5. **Live Eval Runner + Calibration gegen echte Logs** (`tests/golden_questions/runner.py`, `scripts/calibrate.py`) 
6. **Telegram/WebSocket Vollintegration** (`src/channels/*`, `src/main.py`) 

## 5) Definition of Done für „wieder plan-konform“

- Keine produktiven in-memory Adapter im Production-Mode aktiv
- Tenant-Scoping über DB/RLS, Cache Keys und Logs verifiziert
- Evals laufen gegen Live-Agent und prüfen Routing/Grounding/Kosten
- Observability enthält vollständige, tenant-scoped Decision Logs inkl. Kosten
