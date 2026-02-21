# Project Nexus – Claude Code Session Plan

> Für jede Session: Öffne Claude Code im Projekt-Root und paste den Prompt.
> Claude Code liest automatisch CLAUDE.md als Kontext.

-----

## Session 0: Repository Setup

**Ziel:** Lauffähiges Skelett mit Docker, Configs, Projektstruktur.

```
Lies CLAUDE.md. Erstelle die komplette Projektstruktur:

1. pyproject.toml mit allen Dependencies (siehe CLAUDE.md Key Libraries)
2. docker-compose.yml: agent (Python), litellm (proxy), redis
3. .env.example mit allen nötigen Variablen (LLM keys, Telegram token, Supabase URL, Redis, n8n URL)
4. Komplette src/ Verzeichnisstruktur inkl. __init__.py:
   agent/, routing/, memory/, grounding/, plugins/, integrations/,
   channels/, subagents/, onboarding/, observability/, db/
5. src/config.py: Pydantic Settings
6. configs/litellm_config.yaml: 3-Tier mit Fallbacks + $2/day Budget
7. configs/nexus.yaml: Core Settings (language, grounding_mode defaults, etc.)
8. configs/intents/personal.yaml: Personal Assistant Intents:
   - mail (check mail, send mail, search mail)
   - calendar (show events, create event, find free time)
   - reminder (set reminder, list reminders, cancel reminder)
   - automation (create workflow, list workflows, run workflow)
   - knowledge (remember this, what do you know about, search KB)
   - subagent (create bot, manage bot, bot status)
   - web_search (search for, look up, what is)
   - general (greeting, thanks, help, smalltalk)
   - unknown (fallback)
9. configs/plugins/available.yaml: All known plugins with metadata
10. configs/plugins/enabled.yaml: Default enabled (kb, reminders, web_search)
11. configs/intents/subagent_base.yaml: Base intents for business bots (faq, booking, cancellation, complaint, general)
12. configs/subagents/example_bot/: Example sub-agent config
13. tests/conftest.py mit Fixtures
14. .github/workflows/eval.yml
15. README.md: "Nexus – Your Personal AI Agent. Self-hosted, open-source."
    - What is Nexus? (30-second pitch)
    - Quick Start (docker compose up + Telegram setup)
    - Connecting Services (Gmail, Calendar, n8n)
    - Creating Sub-Agents
    - Plugin Development Guide (kurz)
16. .gitignore
17. scripts/setup.sh: One-command setup (copy .env.example, docker compose up)

`docker compose up` soll starten ohne Fehler. Kein Anwendungscode.
```

-----

## Session 1: Core Agent + Onboarding

**Ziel:** Agent der in Telegram antwortet + interaktives Erstsetup.

```
Lies CLAUDE.md. Baue Core Agent + Telegram + Onboarding:

1. src/agent/loop.py: Async ReAct Loop
   - Input: UnifiedMessage + ContextBundle + RoutingDecision
   - Dynamischer System Prompt (Base + Personal Facts + Plugin Schemas)
   - LiteLLM Call (Tier aus RoutingDecision)
   - Structured Output → AgentResponse
   - Max 3 Loops, 30s Timeout

2. src/agent/prompt.py: Prompt Builder
   - Base Template: "Du bist Nexus, ein persönlicher AI-Agent. Du kannst Emails lesen,
     Termine verwalten, Automationen bauen und Sub-Agents erstellen."
   - Inject: Active plugin schemas, personal facts, conversation context
   - Grounding-Mode-Aware: In OPEN mode keine Citation-Pflicht, in STRICT schon

3. src/agent/structured.py: Pydantic Schemas
   - AgentResponse, Citation, UIComponent, DecisionLog
   - ConfirmationPayload (für Inline-Keyboard Aktionen)

4. src/channels/telegram.py: Telegram Bot (aiogram 3.x)
   - /start → Onboarding Flow
   - Nachrichten → UnifiedMessage → Agent → Response
   - Inline Keyboards für Confirmations
   - /connect, /subagents, /help Commands

5. src/channels/message.py: UnifiedMessage Model

6. src/onboarding/flow.py: Interaktives Telegram-Setup
   - Schritt 1: LLM Provider wählen (OpenRouter / eigener Key)
   - Schritt 2: Name + Sprache
   - Schritt 3: Speichert in DB/Config
   - Am Ende: Willkommensnachricht mit verfügbaren Commands

7. src/main.py: FastAPI + Telegram Bot Startup

8. Tests: test_agent.py + test_onboarding.py
   - Agent antwortet auf "Hallo"
   - Agent gibt valid AgentResponse zurück
   - Agent hält Max-Loops ein
   - Onboarding speichert User-Preferences

`python -m pytest tests/test_agent.py tests/test_onboarding.py`
```

-----

## Session 2: Routing + Memory

**Ziel:** Intelligentes Routing + Kontext-Management.

```
Lies CLAUDE.md. Baue Routing + Memory:

ROUTING:
1. src/routing/models.py: RoutingDecision mit grounding_mode Feld
2. src/routing/keyword.py: Keywords aus configs/intents/personal.yaml
3. src/routing/semantic.py: Embedding Router (multilingual MiniLM)
   - Intents aus personal.yaml laden
   - Unknown-Intent Bucket für Drift-Handling
4. src/routing/llm_classifier.py: Fallback
5. src/routing/confidence.py: Heuristic mit Grounding-Mode-Awareness
   - OPEN mode: validator_weight=0, citation redistributed
   - STRICT mode: full formula
6. src/routing/__init__.py: route(message) → RoutingDecision
   - Pipeline: keyword → semantic → llm
   - Setzt grounding_mode automatisch:
     - mail/calendar/reminder/automation intents → OPEN
     - knowledge intents + KB exists → HYBRID
     - subagent messages → STRICT

MEMORY:
7. src/memory/working.py: Last N turns (Redis)
8. src/memory/summary.py: Running Summary (Tier-1 model)
9. src/memory/semantic.py: RAG from personal KB (pgvector)
10. src/memory/personal.py: Personal Facts Store
    - Extrahiert automatisch Fakten aus Gesprächen:
      "User heißt Jerome", "User's n8n ist auf localhost:5678"
    - Speichert in Supabase, injiziert in System Prompt
    - CRUD: User kann Facts manuell hinzufügen/löschen (/facts)
11. src/memory/context.py: Context Assembler (1,200 Token Budget)

Tests: test_routing.py + test_memory.py
- "Check my mails" → intent=mail, grounding=OPEN, Tier 1
- "Remind me tomorrow at 9" → intent=reminder, OPEN, Tier 1
- "Create a bot for my shop" → intent=subagent, Tier 2
- "What's quantum physics?" → intent=general, OPEN, Tier 1
- Memory: Personal facts extracted + recalled
- Memory: Budget nie überschritten
- Memory: Tenant-scoped (Sub-Agent sieht nicht personal memory)

`python -m pytest tests/test_routing.py tests/test_memory.py`
```

-----

## Session 3: Plugin System

**Ziel:** MCP-basiertes Plugin-System + Built-in Plugins.

```
Lies CLAUDE.md. Baue das Plugin-System:

1. src/plugins/manager.py: Plugin Manager
   - discover() → list available plugins (from configs/plugins/)
   - install(plugin_id) → activate plugin
   - enable/disable per user
   - /connect {plugin} Telegram command handler

2. src/plugins/registry.py: Active Plugin Registry
   - get_plugins_for_intent(intent) → nur relevante Plugin-Schemas
   - Core plugins immer geladen (kb, reminders, web_search, escalation)

3. src/plugins/trimming.py: Result Trimming
   - Per-plugin limits + Global 4KB cap

4. src/plugins/firewall.py: Security
   - Pydantic validation, injection detection, whitelist only

5. src/plugins/permissions.py: Scopes + Confirmation Gates
   - Read-Aktionen: kein Confirm nötig
   - Write-Aktionen: Inline Keyboard Confirm
   - Destructive: Double Confirm

6. Built-in Plugins:
   src/plugins/builtin/knowledge_base.py:
   - search(query) → chunks with citations
   - add(content, category) → neuer KB-Eintrag
   - /kb add "Mein Geburtstag ist am 18. Juli"

   src/plugins/builtin/reminders.py:
   - set(text, datetime) → Redis-backed, APScheduler
   - list() → alle aktiven Reminders
   - cancel(id)
   - Sendet Erinnerung via Telegram zur eingestellten Zeit

   src/plugins/builtin/web_search.py:
   - search(query) → Top-5 Ergebnisse (via SearXNG oder DuckDuckGo API)

7. Tests: test_plugins.py
   - Dynamic loading: mail intent → gmail plugin loaded
   - Trimming: oversized result → trimmed to cap
   - Firewall: injection blocked
   - Reminders: set → fires at correct time (mock clock)
   - KB: add entry → searchable

`python -m pytest tests/test_plugins.py`
```

-----

## Session 4: Gmail + Calendar Integration

**Ziel:** Echte Gmail und Google Calendar Anbindung.

```
Lies CLAUDE.md. Baue Gmail + Calendar MCP-Server:

1. src/integrations/gmail/server.py: Gmail MCP Server
   - list_unread(max=10) → subjects, senders, preview
   - search(query) → filtered results
   - read(message_id) → full body
   - send(to, subject, body) → requires confirmation
   - summarize_inbox() → AI-powered inbox summary

2. src/integrations/gmail/auth.py: OAuth2 Flow
   - /connect gmail → generates OAuth URL → user clicks → callback saves token
   - Token refresh logic
   - Tokens encrypted in Supabase

3. src/integrations/gcalendar/server.py: Calendar MCP Server
   - list_events(date_range) → upcoming events
   - create_event(title, date, time, duration) → requires confirmation
   - find_free_time(date_range) → available slots
   - update_event(id, changes) → requires confirmation
   - delete_event(id) → requires double confirmation

4. src/integrations/gcalendar/auth.py: Shared OAuth2 (Google scopes)

5. Tests: test_gmail.py + test_calendar.py (mit Mocks)
   - "Check my mails" → list_unread aufgerufen, formatiert zurück
   - "Send an email to X" → confirmation gate → send
   - "What's on my calendar tomorrow?" → list_events
   - "Book a meeting tomorrow at 3" → create_event + confirm
   - OAuth flow: Token gespeichert + refreshed

`python -m pytest tests/test_gmail.py tests/test_calendar.py`
```

-----

## Session 5: n8n Integration (Game-Changer)

**Ziel:** n8n Workflows lesen, triggern und ERSTELLEN via Chat.

```
Lies CLAUDE.md. Baue den n8n MCP-Server:

1. src/integrations/n8n/server.py: n8n MCP Server
   - list_workflows() → name, active status, last run
   - get_workflow(id) → full workflow details
   - trigger_workflow(id, data?) → execute + return result
   - create_workflow(spec) → creates new workflow via n8n API
   - update_workflow(id, changes) → modify existing
   - activate/deactivate_workflow(id)

2. src/integrations/n8n/builder.py: Workflow Builder (AI-powered)
   - User beschreibt in natürlicher Sprache was der Workflow tun soll
   - Nexus generiert n8n-kompatibles Workflow-JSON
   - Kennt n8n Node-Typen: Cron, Gmail, HTTP, AI, Telegram, Notion, etc.
   - Generiert via Tier-2/3 LLM mit Structured Output
   - Validiert JSON gegen n8n Schema bevor es gesendet wird

3. src/integrations/n8n/templates.py: Workflow-Vorlagen
   - "Daily inbox summary" → fertige Vorlage
   - "Weekly report" → fertige Vorlage
   - "Invoice monitor" → fertige Vorlage
   - Templates können als Basis genommen und angepasst werden

4. src/integrations/n8n/auth.py: API Key Auth
   - /connect n8n → User gibt n8n URL + API Key ein
   - Stored encrypted in Supabase

5. Telegram UX für Workflow-Erstellung:
   - User beschreibt Workflow
   - Nexus zeigt Preview (Schritte als nummerierte Liste)
   - Inline Keyboard: [✅ Erstellen] [✏️ Anpassen] [❌ Abbrechen]
   - "Anpassen" → follow-up Fragen
   - "Erstellen" → API call + Bestätigung

6. Tests: test_n8n.py
   - list_workflows → korrekt formatiert
   - trigger_workflow → Ausführung + Ergebnis
   - create_workflow: "Send me a Telegram message every day at 8am"
     → valides n8n JSON mit Cron + Telegram Node
   - create_workflow: "Monitor Gmail for invoices, save to Drive"
     → valides JSON mit Gmail + Google Drive Nodes
   - Confirmation gate für create/delete

`python -m pytest tests/test_n8n.py`
```

-----

## Session 6: Grounding + Observability

**Ziel:** Mode-abhängige Faktenprüfung + Decision Logs.

```
Lies CLAUDE.md. Baue Grounding + Observability:

GROUNDING:
1. src/grounding/validator.py: Mode-Aware Validator
   - STRICT: Full validation (Hard-Fact detection, citation check, repair)
   - HYBRID: Validate if KB-hit exists, allow LLM-only answers (marked)
   - OPEN: Skip validation (tool results are ground truth)

2. src/grounding/citations.py: Citation Engine (nur STRICT/HYBRID)
3. src/grounding/entity_registry.py: Per-namespace (user KB, sub-agent KB)
4. src/grounding/repair.py: 1-step repair (nur STRICT)

OBSERVABILITY:
5. src/observability/langfuse.py: Decision Logs (20 Felder, siehe CLAUDE.md)
6. src/observability/pii.py: Synthetic PII replacement
7. src/observability/alerts.py: Telegram alerts bei Anomalien

Tests: test_grounding.py + test_observability.py
- STRICT mode: fact without citation → FAIL
- OPEN mode: same fact → PASS (no validation)
- HYBRID mode: KB hit → validated, no KB hit → allowed but marked
- Decision log: all fields populated
- PII redaction works

`python -m pytest tests/test_grounding.py tests/test_observability.py`
```

-----

## Session 7: Sub-Agent Factory

**Ziel:** Sub-Agents via Chat erstellen und verwalten.

```
Lies CLAUDE.md. Baue das Sub-Agent System:

1. src/subagents/manager.py: Sub-Agent CRUD
   - create(name, channel, kb_content) → SubAgent
   - Erstellt: KB namespace, system prompt, intent config, channel setup
   - list() → alle Sub-Agents des Users
   - delete(id) → cleanup
   - /subagent {name} status/pause/resume/kb/logs Commands

2. src/subagents/runtime.py: Sub-Agent Execution
   - Isolierter Kontext (eigene KB, eigener Prompt, STRICT grounding)
   - Shared LLM Gateway (LiteLLM) aber separates Cost-Tracking
   - Kann NICHT auf persönliche Plugins zugreifen (Gmail, Calendar etc.)
   - Nur: kb_search, human_escalation + konfigurierte Business-Tools

3. src/subagents/templates.py: Vorgefertigte Templates
   - "customer_service": FAQ + Beschwerden + Weiterleitung
   - "appointment_booking": Termine + Storno + Erinnerungen
   - "lead_capture": Kontaktdaten sammeln + CRM-Eintrag

4. src/subagents/models.py: SubAgent, SubAgentConfig

5. Telegram UX:
   - "Create a bot for my nail school" → interaktiver Setup-Flow
   - Nexus fragt: Name? Channel? Was soll er können? KB-Inhalt?
   - Erstellt Sub-Agent + gibt Management-Commands

6. Tests: test_subagents.py
   - Create sub-agent → isolierte KB erstellt
   - Sub-agent antwortet nur aus eigener KB (STRICT)
   - Sub-agent kann nicht auf Gmail zugreifen
   - Sub-agent hat eigenes Cost-Tracking
   - Delete → cleanup komplett

`python -m pytest tests/test_subagents.py`
```

-----

## Session 8: Golden Questions + Eval + Polish

**Ziel:** End-to-End Tests, CI/CD, Dokumentation.

```
Lies CLAUDE.md. Baue Eval-Framework + finaler Polish:

1. tests/golden_questions/questions.yaml: 40 Test Cases
   Personal Agent (25):
   - Mail: "Check my emails", "Send email to X", "Summarize inbox"
   - Calendar: "What's on tomorrow?", "Book meeting at 3"
   - Reminders: "Remind me at 9", "List my reminders", "Cancel reminder"
   - n8n: "List my workflows", "Run weekly report", "Create a workflow that..."
   - KB: "Remember that X", "What do you know about Y"
   - General: "Hello", "Help", "What can you do?"
   - Edge: prompt injection, gibberish, 10+ turns, mixed language

   Sub-Agent (15):
   - FAQ from KB only, no hallucination
   - Unknown question → honest "I don't know"
   - Attempted access to personal plugins → blocked
   - Citation present for all hard facts

2. tests/golden_questions/runner.py: Eval Runner
3. scripts/run_evals.py: CLI (--suite smoke/full)
4. scripts/calibrate.py: Weekly confidence calibration
5. .github/workflows/eval.yml: CI (smoke on push, full on release)

6. Polish:
   - README.md finalisieren (Screenshots, GIFs wenn möglich)
   - /help Command mit allen verfügbaren Features
   - Error handling: graceful failures mit hilfreichen Meldungen
   - Rate limiting: max 30 messages/minute

`python -m pytest tests/ -v`
```

-----

## Session 9+ (Later)

|Session|Modul                                      |Wann                   |
|-------|-------------------------------------------|-----------------------|
|9      |WhatsApp Channel (Baileys)                 |Wenn Telegram stabil   |
|10     |Web Chat (FastAPI WebSocket + React Widget)|Für Sub-Agent Embedding|
|11     |Notion Integration                         |Bei Bedarf             |
|12     |Filesystem Plugin (lokale Dateien)         |Bei Bedarf             |
|13     |Community Plugin SDK                       |Wenn Core stable       |
|14     |Admin Dashboard (Web)                      |Bei mehreren Sub-Agents|

-----

## Regeln für alle Sessions

1. **CLAUDE.md zuerst lesen** – immer
1. **Personal-first** – Core Use Case ist der persönliche Agent, nicht Business-Bots
1. **Plugins, nicht hardcoded** – Jede Integration ist ein MCP-Server
1. **Grounding-Mode beachten** – OPEN für Personal, STRICT für Sub-Agents
1. **Telegram ist primary channel** – alles muss in Telegram gut funktionieren
1. **Git Commit nach jedem Modul**
1. **Mocks für Tests** – kein echtes Gmail/Calendar/n8n in Unit-Tests
1. **n8n ist First-Class** – nicht als Afterthought, sondern als Kernfeature