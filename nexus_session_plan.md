Project Nexus – Claude Code Session Plan
Für jede Session: Öffne Claude Code im Projekt-Root und paste den Prompt. Claude
Code liest automatisch CLAUDE.md als Kontext.
Session 0: Repository Setup
Ziel: Leeres Repo mit kompletter Struktur, Configs, Docker, CI/CD.
Lies CLAUDE.md. Erstelle die komplette Projektstruktur:
1. pyproject.toml mit allen Dependencies (siehe CLAUDE.md Key Libraries)
2. docker-compose.yml: services für agent (Python), litellm (proxy), redis
3. .env.example mit allen nötigen Environment-Variablen
4. src/ Verzeichnisstruktur mit __init__.py in jedem Package (inkl. tenant/ Package)
5. src/config.py: Pydantic Settings Klasse die .env liest
6. configs/litellm_config.yaml: 3-Tier Model Config mit Fallbacks und Budget-Limits
7. configs/defaults/intents.yaml: Generische Intent-Cluster (faq, booking, cancellation, comp
8. configs/defaults/tools.yaml: Tool-Registry mit Default-Permissions, Trimming-Limits, Chann
9. configs/defaults/channels.yaml: Channel-Konfiguration
10. configs/defaults/prompt_template.yaml: Base System-Prompt Template mit {tenant_variables}
11. configs/tenants/example_tenant/: Komplettes Beispiel-Tenant-Verzeichnis (tenant.yaml, int
12. src/tenant/models.py: Pydantic Models für Tenant, TenantMembership, TenantConfig
13. tests/conftest.py mit Basis-Fixtures (mock tenant, mock config)
14. .github/workflows/eval.yml: GitHub Action für Golden Questions
15. README.md: Setup-Anleitung + "Wie lege ich einen neuen Tenant an?"
16. .gitignore
Kein Anwendungscode – nur Struktur und Config. `docker compose up` soll ohne Fehler starten.
Session 1: Tenant System + Core Agent Loop
Ziel: Tenant Resolution + funktionierender ReAct Agent.
Lies CLAUDE.md. Baue Tenant-System und Core Agent:
1. src/tenant/manager.py: TenantManager
- load_tenant(tenant_id) → TenantContext
- Lädt Config aus configs/tenants/{id}/ mit Fallback auf configs/defaults/
- resolve_tenant(channel, sender_id) → tenant_id (DB lookup oder Config-Mapping)
- Cacht geladene TenantContexts in-memory (refresh alle 5 min)
2. src/tenant/onboarding.py: Tenant Onboarding
- create_tenant(name, config) → erstellt DB-Einträge + Config-Verzeichnis
- Validiert Config gegen TenantConfig Schema
3. src/agent/loop.py: Async ReAct Loop
- Nimmt UnifiedMessage + ContextBundle + RoutingDecision + TenantContext
- Baut System Prompt dynamisch (Base Template + Tenant Variables + Tool Schemas)
- Ruft LiteLLM an (model aus RoutingDecision.tier)
- Parsed Structured Output (AgentResponse Schema)
- Max 3 Agent-Loops, Timeout: 30s
4. src/agent/prompt.py: System Prompt Builder
- load_base_template() aus configs/defaults/prompt_template.yaml
- inject_tenant_variables(template, tenant_context) → personalisierter Prompt
- inject_tools(prompt, tool_schemas) → Tools im Prompt
- inject_context(prompt, context_bundle) → Memory im Prompt
5. src/agent/structured.py: Alle Pydantic Schemas
- AgentResponse, Citation, UIComponent, DecisionLog, Turn, Chunk
- TenantContext (import from tenant/models.py)
6. src/main.py: FastAPI App
- POST /chat: nimmt {"text": "...", "channel": "web", "sender_id": "...", "tenant_id": "..
- Resolves tenant → loads config → routes → agent → response
- Vorerst: kein Routing, kein Memory – direkt Tier 2
7. Tests: test_agent.py + test_tenant.py
- TenantManager: lädt example_tenant Config korrekt
- TenantManager: Fallback auf Defaults wenn Tenant-Config fehlt
- Agent: beantwortet "Hallo" freundlich
- Agent: gibt valid AgentResponse zurück
- Agent: System Prompt enthält Tenant Business-Name
- Agent: hält sich an max 3 Loops
Teste mit: `python -m pytest tests/test_agent.py tests/test_tenant.py`
Session 2: Routing Engine
Ziel: 4-stufige Routing-Pipeline, tenant-aware.
Lies CLAUDE.md. Baue das Routing Modul:
1. src/routing/models.py: RoutingDecision, Tier, RiskLevel
2. src/routing/keyword.py: Keyword Pre-Filter
- Lädt Keywords aus tenant config (mit Fallback auf defaults)
- Returns RoutingDecision | None
3. src/routing/semantic.py: Semantic Router
- Lädt Intent-Cluster pro Tenant aus configs/
- sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- Per-intent Confidence-Schwellen (konfigurierbar)
- Unknown-Intent Bucket Logging (für Drift-Handling)
- Returns RoutingDecision | None
4. src/routing/llm_classifier.py: LLM Fallback
- Structured Output: {tier, risk_level, requires_confirmation, intent}
- Nur wenn Keyword + Semantic Router None
5. src/routing/confidence.py: Heuristic Confidence
- Formel: 0.30*rag + 0.10*coverage + 0.20*tool + 0.25*validator + 0.15*citation
- Gewichte konfigurierbar pro Tenant
- Auto-low: hard facts without citations → 0.3
- Eskalations-Logik
6. src/routing/__init__.py: route(message, tenant_context) → RoutingDecision
- Pipeline: keyword → semantic → llm_classifier
- Fügt tools_to_load hinzu (aus Tenant tool-config)
- Appliziert tenant-spezifisches risk_mapping
7. Tests: test_routing.py
- Generische Tests (nicht business-spezifisch):
- Keyword "price" → Tier 1
- Keyword "cancel" → Tier 2, risk=high
- "Hello" → Tier 1, smalltalk
- Gibberish → LLM Fallback triggered
- Confidence Calculator: alle Schwellen
- Tenant A hat "cancel"=high risk, Tenant B hat "cancel"=low risk → unterschiedliches Ro
Teste mit: `python -m pytest tests/test_routing.py`
Session 3: Memory System
Ziel: 3-Layer Memory mit Token-Budget, tenant-scoped.
Lies CLAUDE.md. Baue das Memory Modul:
1. src/memory/working.py: Working Memory (Redis)
- Key: tenant:{tenant_id}:conv:{conversation_id}:turns
- FIFO, Token-counting via tiktoken
2. src/memory/summary.py: Running Summary
- Komprimiere alle 3 Messages via Tier-1 Model
- Summary-Prompt ist generisch (kein Business-Kontext hardcoded)
- Key: tenant:{tenant_id}:conv:{conversation_id}:summary
3. src/memory/semantic.py: RAG Snippets
- pgvector similarity search, WHERE tenant_id = {tenant_id}
- Returns chunks mit score + source_id (für Citations)
4. src/memory/context.py: Context Assembler
- Budget: max 1,200 tokens total (konfigurierbar pro Tenant)
- Priority: RAG > Last 2 turns > Summary > Older turns
- Returns ContextBundle
5. src/db/models.py: KB-Entry Model
- id, tenant_id, category, content, embedding (vector), source, updated_at
6. scripts/seed_kb.py: KB Seeder
- Liest kb_seed.yaml aus Tenant-Config
- Generiert Embeddings, speichert in Supabase
- `python scripts/seed_kb.py --tenant example_tenant`
7. Tests: test_memory.py
- Working Memory: FIFO, Token-Limit
- Summary: wird erstellt, <200 Tokens
- RAG: tenant-scoped (Tenant A sieht nicht Tenant B's KB)
- Context Assembler: 1,200 Token Budget nie überschritten
Teste mit: `python -m pytest tests/test_memory.py`
Session 4: Grounding & Validator
Ziel: Deterministische Fakten-Prüfung mit Citations, tenant-aware.
Lies CLAUDE.md. Baue das Grounding Modul:
1. src/grounding/entity_registry.py: Entity Registry
- Lädt entities aus Tenant's KB (auto-sync bei KB-Update)
- Redis-cached pro Tenant, refresh alle 5 Min
- Generisch: entities = {type: [values]} – z.B. {"service": [...], "price": [...]}
2. src/grounding/validator.py: Deterministic Validator
- Hard-Fact Detection: Regex (Preise, Zeiten, Telefon, Adressen) + Entity-Liste
- Citation Check: citation-ID vorhanden? Existiert in KB? Wert stimmt?
- Returns GroundingResult
3. src/grounding/citations.py: Citation Engine
- Generiert citation-IDs: KB-{CATEGORY}-{ID}
- Validiert gegen Supabase (tenant-scoped)
4. src/grounding/repair.py: Repair Logic
- 1 retry max, dann fail-fast mit "Kann ich nicht zuverlässig beantworten"
5. Tests: test_grounding.py
- Fact mit citation → PASS
- Fact ohne citation → FAIL + repair
- Falsche citation → FAIL
- Soft content (keine Facts) → PASS
- Tenant-scoped: Entity Registry lädt nur eigene Entities
Teste mit: `python -m pytest tests/test_grounding.py`
Session 5: MCP Tools Layer
Ziel: Dynamic Loading, Trimming, Firewall, Permissions – alles per-tenant
konfigurierbar.
Lies CLAUDE.md. Baue das Tools Modul:
1. src/tools/registry.py: Tool Registry
- Lädt Tool-Definitionen aus Tenant config (Fallback auf Defaults)
- get_tools_for_intent(intent, tenant_context) → nur relevante Schemas
- Core tools immer geladen: human_escalation, kb_search
2. src/tools/trimming.py: Result Trimming
- Per-tool config (max_bytes, top_n, field_whitelist) aus Tenant tools.yaml
- Global cap: 4,096 bytes
- trim_result(tool_name, raw_result, tenant_config) → trimmed
3. src/tools/firewall.py: Tool Firewall
- validate_tool_call(tool_name, args, tenant_context) → bool
- Registry whitelist, Pydantic schema validation, injection detection
4. src/tools/permissions.py: Permission System
- check_scope, check_channel, check_confirmation – all tenant-configurable
5. src/tools/servers/knowledge_base.py: KB Search (tenant-scoped)
6. src/tools/servers/calendar.py: Calendar (MOCK, generic interface)
7. src/tools/servers/human_escalation.py: Escalation (sends to tenant's contact)
7. Tests: test_tools.py
- Dynamic loading per intent
- Trimming respects per-tool + global cap
- Firewall rejects injection
- Permissions differ per tenant config
- Tenant A's tools ≠ Tenant B's tools
Teste mit: `python -m pytest tests/test_tools.py`
Session 6: Channels (Telegram + Web)
Ziel: Telegram Bot + Web Chat, tenant-aware.
Lies CLAUDE.md. Baue das Channels Modul:
1. src/channels/message.py: UnifiedMessage + adapters
- Tenant resolution: sender_id → tenant_id mapping
2. src/channels/base.py: Abstract Channel
- receive → UnifiedMessage, send → channel delivery
- KI-Disclosure aus Tenant config
3. src/channels/telegram.py: Telegram Bot (aiogram 3.x)
- Multi-tenant: ein Bot kann mehrere Tenants bedienen (via Group/Chat Mapping)
- Oder: separater Bot-Token pro Tenant (konfigurierbar)
- /start mit tenant-spezifischer KI-Disclosure
- Admin-Commands: /pause_proactive, /status
4. src/channels/web.py: FastAPI WebSocket
- tenant_id als Query-Parameter oder aus Auth-Token
- Streaming, Generative UI components, fallback_text
5. Tests: test_channels.py
- Message parsing pro Channel
- Tenant resolution korrekt
- KI-Disclosure enthält tenant's business_name
- Response formatting pro Channel
Teste mit: `python -m pytest tests/test_channels.py`
Session 7: Observability & Alerts
Ziel: Langfuse + Decision Logs + PII Redaction + Alerts, tenant-scoped.
Lies CLAUDE.md. Baue das Observability Modul:
1. src/observability/langfuse.py: Langfuse Client
- Decision Logs: 18 Felder inkl. tenant_id
- Span-based tracing per module
- Cost tracking per request + per tenant
2. src/observability/pii.py: PII Redaction
- Synthetic replacement (Faker, locale aus Tenant config)
- Applied before logging
3. src/observability/alerts.py: Alert System
- Telegram webhook (alert channel konfigurierbar pro Tenant)
- Thresholds konfigurierbar
4. Integration in agent/loop.py
5. Tests: test_observability.py
- PII redaction works
- Decision Log has all 18 fields
- tenant_id in every log entry
Teste mit: `python -m pytest tests/test_observability.py`
Session 8: Golden Questions & Eval
Ziel: Generisches Eval-Framework, per-tenant test suites.
Lies CLAUDE.md. Baue das Eval Framework:
1. tests/golden_questions/questions.yaml: Template mit 30 generischen Tests
Kategorien: FAQ, Booking, Cancellation, Consultation, Complaint, Edge Cases
Jeder Test: input, expected_intent, expected_tier, must_have_citations, max_tokens, max_la
2. tests/golden_questions/runner.py: Eval Runner
- Lädt Fragen (generisch oder tenant-spezifisch)
- Führt gegen Live-Agent aus
- Führt gegen Live-Agent aus
- Prüft: Korrektheit, Routing, Grounding, Tokens, Latenz
- Prüft: Korrektheit, Routing, Grounding, Tokens, Latenz
- Output: JSON Report
- Output: JSON Report
3. scripts/run_evals.py: CLI
- `python scripts/run_evals.py --tenant example_tenant --suite golden`
- `python scripts/run_evals.py --tenant example_tenant --suite smoke`
4. scripts/calibrate.py: Confidence Calibration
- Liest Decision Logs aus Langfuse
- Pro Tenant: False Escalations / False Passes analysieren
- Output: empfohlene neue Gewichte + Before/After KPIs
5. .github/workflows/eval.yml: CI
- Smoke suite bei push, full bei release
6. scripts/onboard_tenant.py: Tenant Onboarding CLI
- `python scripts/onboard_tenant.py --name "New Business" --language de`
- Erstellt Tenant-Config Verzeichnis aus Template
- Erstellt DB-Einträge (tenant, membership)
- Seeded KB aus kb_seed.yaml
- Gibt Checkliste aus: "Nächste Schritte: Intents anpassen, KB füllen, Channels konfigurie
Teste mit: `python -m pytest tests/ -v`
Session 9+ (Optional / Later)
Session Modul Wann
9 WhatsApp (Baileys Node.js Bridge) Wenn Telegram stabil
10 Proactive Jobs (Cron, per tenant) Nach 2 Wochen Live
11 Generative UI (React Web Widget) Wenn Web-Channel aktiv
12 Admin Dashboard (Tenant Management) Bei 3+ Tenants
Regeln für alle Sessions
1. Immer CLAUDE.md zuerst lesen
2. Kein Business-spezifischer Code – alles über Tenant-Config
3. TenantContext durchreichen – jede Funktion die Business-Logik braucht bekommt
TenantContext
4. Tests mit Mock-Tenant – conftest.py hat einen “example_
tenant” Fixture
5. Git Commit nach jedem Modul
6. Mocks für externe Services – kein echtes LLM/Supabase/Redis in Unit-Tests
7. Config-Vererbung – Tenant-Config überschreibt Defaults, fehlende Keys fallen
zurück
8. Generische Beispiele – Intent-Beispiele, KB-Seeds in
configs/tenants/example_tenant/ als Vorlag