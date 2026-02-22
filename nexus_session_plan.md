# Project Nexus – Session Plan (FINAL)

> **Workflow:** Claude orchestrates → you paste session prompt into Codex → Codex builds.
> Codex reads CLAUDE.md automatically from repo root.
> Each session prompt is self-contained: paste it, Codex executes.
> Git commit after each session.

---

## Session 0: Foundation Refactor

**Goal:** Migrate existing codebase from business-chatbot to personal-agent foundation.
No new features yet – just prepare the ground.

```
Read CLAUDE.md completely. This is a REFACTOR session for an existing codebase.
Do NOT delete working code. Extend and adapt.

TASK 1: Migrate src/config.py from dataclass + os.getenv to pydantic-settings.
- Keep all existing fields
- Add: TELEGRAM_BOT_TOKEN, N8N_URL, N8N_API_KEY, WHISPER_MODEL, DAILY_BUDGET_USD
- Add: RUNTIME_MODE validation (local|production) – already exists, keep it
- Strict validation for production mode (already exists, keep it)

TASK 2: Migrate all dataclasses in these files to Pydantic BaseModel:
- src/agent/structured.py (AgentResponse)
- src/routing/models.py (RoutingDecision, Tier, RiskLevel)
  - ADD: GroundingMode enum (strict, hybrid, open)
  - ADD: grounding_mode field to RoutingDecision
  - ADD: plugins_to_load: list[str] field
  - ADD: should_delegate: bool field
- src/channels/message.py (UnifiedMessage)
  - ADD: voice_audio: bytes | None = None
  - ADD: is_subagent_message: bool = False
  - ADD: subagent_id: str | None = None

TASK 3: Create configs/intents/personal.yaml with ALL intents from CLAUDE.md §9.
Keep configs/defaults/intents.yaml as-is (used by sub-agents later).

TASK 4: Create configs/nexus.yaml:
```yaml
agent:
  name: "Nexus"
  default_language: "both"  # de, en, both
  grounding_mode_default: "open"
  max_react_loops: 5
  react_timeout_seconds: 30

budget:
  daily_cap_usd: 2.00
  alert_threshold_pct: 80

multi_agent:
  enabled: true
  delegation_threshold: 0.6  # confidence below this → consider delegation
  max_specialists: 3         # max parallel specialist agents

plugins:
  builtin: [knowledge_base, reminders, web_search, human_escalation]
```

TASK 5: Create configs/policies/guardian.yaml:
```yaml
rules:
  shell_commands:
    blocked: [rm -rf, mkfs, dd, shutdown, reboot]
    require_confirmation: [apt install, pip install, docker, systemctl]
  http_requests:
    blocked_domains: []
    require_confirmation_for_new_domains: true
  file_operations:
    sandboxed_paths: [/home/nexus/workspace]
    blocked_paths: [/etc, /usr, /var, /root]
  risk_levels:
    low: auto_approve
    medium: log_and_approve
    high: require_user_confirmation
    critical: block_and_alert
```

TASK 6: Create configs/policies/budget.yaml:
```yaml
tiers:
  tier_1:
    models: [deepseek/deepseek-chat, google/gemini-2.0-flash-exp]
    max_tokens: 400
    cost_per_1k_tokens: 0.0001
  tier_2:
    models: [anthropic/claude-3-5-haiku-latest, openai/gpt-4.1-mini]
    max_tokens: 800
    cost_per_1k_tokens: 0.001
  tier_3:
    models: [anthropic/claude-sonnet-4-20250514, openai/gpt-4.1]
    max_tokens: 1500
    cost_per_1k_tokens: 0.005
daily_cap_usd: 2.00
```

TASK 7: Update configs/litellm_config.yaml to match budget.yaml model choices.

TASK 8: Create stub directories with __init__.py:
- src/orchestration/
- src/integrations/ (gmail/, gcalendar/, n8n/, notion/, github_plugin/, terminal/,
  home_assistant/, spotify/, todoist/, finance/, whatsapp_msg/, filesystem/)
- src/subagents/
- src/learning/

TASK 9: Update pyproject.toml – add dependencies:
- mcp, openai-whisper OR faster-whisper, edge-tts, structlog

TASK 10: Update README.md first line to:
"# Nexus – Your Personal AI Agent. Self-hosted, open-source, no limits."

TASK 11: Run ALL existing tests. They must still pass.
Fix any breakage caused by the migration (especially the dataclass → BaseModel change).

ACCEPTANCE: `python -m pytest tests/ -v` passes. New configs exist. No functionality lost.
```

---

## Session 1: Multi-Agent Orchestration + Real Agent Loop

**Goal:** The brain of Nexus. Multi-agent system + first real LLM calls.

```
Read CLAUDE.md §6 (Multi-Agent Orchestration) completely.

TASK 1: src/orchestration/messages.py
- Define inter-agent message types as Pydantic models:
  TaskRequest, TaskResult, SecurityReview, BudgetQuery, BudgetResponse
- Each has: task_id, from_agent, to_agent, payload, timestamp

TASK 2: src/orchestration/task_board.py
- TaskBoard class (in-memory for now, Redis-ready interface)
- Methods: create_task, update_status, get_task, list_tasks_for_request
- Task statuses: pending, running, completed, failed, vetoed

TASK 3: src/orchestration/guardian.py
- GuardianAgent class
- Method: review(tool_name, args, risk_level) → Approved | NeedsConfirmation | Blocked
- Loads rules from configs/policies/guardian.yaml
- Uses existing src/tools/firewall.py for injection detection
- Adds policy checks on top (blocked commands, path sandboxing, domain checks)
- Returns structured GuardianVerdict with reason

TASK 4: src/orchestration/budget.py
- BudgetAgent class
- Method: select_model(task_tier, task_description) → model_name, max_tokens
- Method: track_usage(model, tokens_in, tokens_out, cost)
- Method: get_daily_spend() → float
- Method: check_budget() → BudgetStatus (ok | warning | exceeded)
- Loads config from configs/policies/budget.yaml
- In-memory tracking (Redis-ready interface)

TASK 5: src/orchestration/specialists.py
- SpecialistAgent base class
- Subclasses: ResearchAgent, CoderAgent, WriterAgent, OpsAgent
- Each has: name, system_prompt_snippet, allowed_plugins
- Method: execute(task: TaskRequest, context: ContextBundle) → TaskResult
- Uses src/agent/loop.py for actual LLM calls

TASK 6: src/orchestration/coordinator.py
- Coordinator class: the entry point for all requests
- Method: process(message: UnifiedMessage) → AgentResponse
- Logic:
  1. Route message → RoutingDecision (uses existing routing pipeline)
  2. If simple (single intent, high confidence, no delegation needed):
     → Run single ReAct loop directly (fast path, ~70% of requests)
  3. If complex (should_delegate=True OR multiple tools):
     → Manager decomposes → TaskGraph → dispatch to specialists
  4. Budget Agent selects model for each task
  5. Guardian Agent reviews each tool call
  6. Assemble final response

TASK 7: src/orchestration/manager.py
- ManagerAgent class
- Method: decompose(message, routing_decision) → list[TaskRequest]
- Method: assemble(results: list[TaskResult]) → AgentResponse
- Uses tier_2/tier_3 LLM for decomposition (via LiteLLM)
- Simple requests: returns single task (self-handled)

TASK 8: REFACTOR src/agent/loop.py
- Make it actually call LiteLLM (not return hardcoded text)
- Async ReAct loop:
  1. Build system prompt (src/agent/prompt.py)
  2. Call LiteLLM with tier from RoutingDecision
  3. Parse response for tool calls
  4. If tool call: Guardian review → execute tool → feed result back
  5. Max loops: 5, timeout: 30s
  6. Return structured AgentResponse
- Handle LiteLLM errors gracefully (timeout, rate limit, budget exceeded)

TASK 9: REFACTOR src/agent/prompt.py
- build_system_prompt() for personal agent:
  "You are Nexus, a personal AI agent. You act on behalf of your user.
   You can read emails, manage calendars, create automations, search the web,
   control servers, and much more. Available tools: {plugin_schemas}.
   User facts: {personal_facts}. Language: {language}."
- Inject active plugin schemas dynamically
- Inject personal facts from memory
- Grounding mode instructions based on RoutingDecision

TASK 10: Wire it all together in src/main.py
- Coordinator replaces direct AgentLoop usage
- /chat/web endpoint uses Coordinator.process()

TASK 11: Tests in tests/test_orchestration.py:
- Guardian blocks "rm -rf /"
- Guardian approves "ls /home/nexus/workspace"
- Guardian requires confirmation for "apt install nginx"
- Budget Agent selects tier_1 for simple query
- Budget Agent blocks when daily cap exceeded
- Coordinator routes simple "hello" directly (no delegation)
- Coordinator delegates "check mails and create workflow" to specialists
- Manager decomposes multi-step task into TaskGraph

TASK 12: Update tests/test_agent.py for new loop (mock LiteLLM calls).

ACCEPTANCE: `python -m pytest tests/ -v` passes. Agent makes real LLM calls
(mocked in tests). Multi-agent orchestration works end-to-end.
```

---

## Session 2: Telegram Bot + Voice + Onboarding

**Goal:** Nexus comes alive in Telegram. Voice support. Chat-based setup.

```
Read CLAUDE.md §12 (Channels & Voice) and §15 (Onboarding).

TASK 1: src/channels/telegram.py – FULL aiogram 3.x implementation
- Bot startup in src/main.py (webhook or polling mode)
- /start → onboarding flow
- /help → feature overview
- /connect {plugin} → plugin management
- /subagents → sub-agent management
- /costs → budget report (from Budget Agent)
- /facts → personal facts CRUD
- Text messages → UnifiedMessage → Coordinator.process() → reply
- Inline keyboards for confirmation gates (Guardian Agent confirmations)
- Error handling: graceful messages, not stack traces

TASK 2: src/channels/voice.py – Voice pipeline
- receive_voice(audio_bytes) → text (Whisper STT)
- synthesize_voice(text) → audio_bytes (Edge-TTS)
- Integration with Telegram: voice message received → STT → process → TTS → voice reply
- Fallback: if STT fails, ask user to type instead
- Use faster-whisper (local, free) or OpenAI Whisper API (configurable)

TASK 3: src/onboarding/flow.py – REWRITE as Telegram interactive flow
- Step 1: LLM provider selection (inline keyboard)
- Step 2: Name input (text message)
- Step 3: Language selection (inline keyboard)
- Step 4: Save preferences to DB/config
- Step 5: Welcome message with available commands and /connect hints
- State machine pattern (track onboarding step per user in Redis/memory)

TASK 4: src/channels/message.py – Update from_telegram_payload()
- Handle voice messages (download audio, set voice_audio field)
- Handle media (photos, documents)
- Handle callback queries (inline keyboard responses)

TASK 5: Update src/main.py
- Start aiogram bot alongside FastAPI
- Route Telegram updates through Coordinator

TASK 6: Tests in tests/test_telegram.py (mock aiogram):
- /start triggers onboarding
- Text message gets agent response
- Voice message gets STT → response → TTS
- Inline keyboard confirmation works
- /connect shows plugin list

ACCEPTANCE: Bot responds in Telegram. Voice works. Onboarding flow completes.
```

---

## Session 3: Plugin System + Built-in Plugins

**Goal:** MCP-based plugin system. Built-in plugins fully functional.

```
Read CLAUDE.md §8 (Plugin System).

TASK 1: src/plugins/manager.py – Plugin Manager
- discover() → list all plugins from configs/plugins/available.yaml
- install(plugin_id) → enable plugin for user
- uninstall(plugin_id) → disable
- get_enabled() → list of active plugins
- /connect {name} handler: check if plugin exists, guide auth if needed
- /disconnect {name} handler

TASK 2: src/plugins/registry.py – REFACTOR for MCP awareness
- get_plugins_for_intent(intent) → only relevant plugin schemas
- get_all_schemas() → for system prompt injection
- Dynamic loading: only load schemas the current intent needs
- Measure schema token cost (for Budget Agent)

TASK 3: configs/plugins/available.yaml – All plugins with metadata:
```yaml
plugins:
  knowledge_base:
    type: builtin
    description: "Personal knowledge base"
    auth: none
    always_loaded: true
  reminders:
    type: builtin
    description: "Time-based reminders"
    auth: none
    always_loaded: true
  web_search:
    type: builtin
    description: "Web search via SearXNG/DuckDuckGo"
    auth: none
    always_loaded: true
  gmail:
    type: first_party
    description: "Read, search, send emails"
    auth: oauth2
    oauth_scopes: ["gmail.readonly", "gmail.send"]
  gcalendar:
    type: first_party
    description: "Manage Google Calendar"
    auth: oauth2
  n8n:
    type: first_party
    description: "Manage n8n workflows"
    auth: api_key
  # ... all others from CLAUDE.md §8
```

TASK 4: src/plugins/builtin/knowledge_base.py – UPGRADE
- search(query) → chunks with citations and scores
- add(content, category) → new KB entry (extract facts automatically)
- remove(entry_id)
- list(category?) → all entries
- Auto-fact extraction: when user says "remember that X", extract structured fact

TASK 5: src/plugins/builtin/reminders.py – NEW
- set(text, datetime, recurring?) → create reminder
- list() → all active reminders
- cancel(id)
- APScheduler integration: fires at correct time
- Sends reminder via Telegram message
- Recurring reminders: daily, weekly, monthly

TASK 6: src/plugins/builtin/web_search.py – NEW
- search(query, max_results=5) → results with title, snippet, URL
- Use DuckDuckGo Instant Answer API (free, no key needed)
- OR SearXNG instance (self-hosted, configurable)
- Anonymous: no tracking, no API key needed

TASK 7: Tests in tests/test_plugins.py:
- Plugin manager discovers all plugins
- Install/uninstall works
- KB: add entry → search returns it with citation
- Reminders: set → fires at correct time (mock clock)
- Web search: returns results (mock HTTP)
- Dynamic loading: mail intent loads gmail schema only
- Guardian integration: plugin calls go through Guardian review

ACCEPTANCE: Plugin system works. Built-in plugins functional. /connect flow works in Telegram.
```

---

## Session 4: Gmail + Calendar + n8n Integration

**Goal:** The three core first-party plugins. n8n workflow CREATION is the killer feature.

```
Read CLAUDE.md §8 (Plugin System, especially n8n section).

TASK 1: src/integrations/gmail/server.py
- list_unread(max=10) → subjects, senders, preview
- search(query) → filtered results
- read(message_id) → full message body
- send(to, subject, body) → REQUIRES Guardian confirmation
- summarize_inbox() → AI-powered summary (uses agent LLM)
- All via Google Gmail API (google-auth, google-api-python-client)

TASK 2: src/integrations/gmail/auth.py
- OAuth2 flow triggered by /connect gmail
- Generates OAuth URL → user clicks → callback saves token
- Token refresh logic
- Tokens stored encrypted (Supabase or local file in dev mode)

TASK 3: src/integrations/gcalendar/server.py
- list_events(date_range) → upcoming events
- create_event(title, date, time, duration) → requires confirmation
- update_event(id, changes) → requires confirmation
- delete_event(id) → requires DOUBLE confirmation (critical risk)
- find_free_time(date_range) → available slots

TASK 4: src/integrations/gcalendar/auth.py
- Shared Google OAuth2 with Gmail (same credentials, additional scope)

TASK 5: src/integrations/n8n/server.py
- list_workflows() → name, active status, last run time
- get_workflow(id) → full workflow details
- trigger_workflow(id, data?) → execute and return result
- create_workflow(spec) → creates via n8n REST API
- update_workflow(id, changes) → modify existing
- activate_workflow(id) / deactivate_workflow(id)
- All via n8n REST API (https://docs.n8n.io/api/api-reference/)

TASK 6: src/integrations/n8n/builder.py – THE KILLER FEATURE
- User describes workflow in natural language
- Nexus generates n8n-compatible workflow JSON
- MUST know n8n node types: Cron/Schedule, Gmail, HTTP Request, Code,
  Telegram, Notion, Google Drive, Webhook, IF, Switch, Merge
- Generation via tier_2/tier_3 LLM with structured output
- Validates generated JSON against n8n schema before sending
- Preview flow: show numbered steps → inline keyboard [✅ Create] [✏️ Modify] [❌ Cancel]
- "Modify" → follow-up conversation → regenerate

TASK 7: src/integrations/n8n/auth.py
- /connect n8n → asks for n8n URL + API key via Telegram
- Validates connection (calls n8n API to test)
- Stores encrypted

TASK 8: Tests:
- tests/test_gmail.py: list_unread, search, send (mocked Google API)
- tests/test_calendar.py: list_events, create, find_free_time (mocked)
- tests/test_n8n.py:
  - list_workflows returns formatted list
  - trigger_workflow executes and returns result
  - builder: "Send Telegram message every day at 8am"
    → generates valid n8n JSON with Schedule + Telegram nodes
  - builder: "Monitor Gmail for invoices, save to Drive"
    → generates valid JSON with Gmail + Google Drive nodes
  - Guardian confirms create/delete, blocks without confirmation
- OAuth flow: token saved and refreshed (mocked)

ACCEPTANCE: Gmail, Calendar, n8n all work end-to-end (with mocks).
n8n workflow CREATION generates valid JSON. Telegram UX for all three works.
```

---

## Session 5: Grounding Refactor + Memory Upgrade + Personal Facts

**Goal:** Mode-aware grounding. Personal facts auto-extraction. Memory upgrade.

```
Read CLAUDE.md §7 (Grounding) and §10 (Memory).

TASK 1: REFACTOR src/grounding/validator.py
- Accept grounding_mode parameter (from RoutingDecision)
- STRICT mode: existing behavior (citation required, repair-or-fallback)
- HYBRID mode: if KB hit exists → validate + cite. If no KB hit → allow, mark "[unverified]"
- OPEN mode: skip validation entirely, return passed=True always
- The Guardian Agent should call this AFTER tool execution for response validation

TASK 2: src/memory/personal.py – NEW
- PersonalFactsStore class
- Auto-extract facts from conversations:
  "My name is Jerome" → store: {fact: "User's name is Jerome", source: "conversation"}
  "My n8n is on localhost:5678" → store: {fact: "n8n URL: localhost:5678"}
- Extraction via tier_1 LLM (cheap, runs after each conversation)
- CRUD: /facts list, /facts add "...", /facts remove {id}
- Inject top relevant facts into system prompt (max ~100 tokens)
- Storage: Supabase in production, in-memory dict in local mode

TASK 3: UPGRADE src/memory/semantic.py
- Replace lexical overlap with actual sentence-transformers embeddings
  (paraphrase-multilingual-MiniLM-L12-v2)
- Use numpy cosine similarity (no pgvector yet, that's production adapter)
- Keep the same interface: upsert(id, text), search(query, top_k)

TASK 4: Update src/memory/context.py
- Add personal_facts to ContextPackage
- Budget: working_turns (~400 tok) + summary (~200) + semantic (~300) + facts (~100) = ~1,000
- Hard cap at 1,200 tokens (use tiktoken to count)

TASK 5: Update src/routing/__init__.py
- Set grounding_mode automatically based on intent (see CLAUDE.md §7 table)
- Set should_delegate based on confidence + intent complexity

TASK 6: Tests:
- test_grounding.py: add OPEN mode test (always passes), HYBRID test (KB hit vs no hit)
- test_memory.py: personal facts extraction, injection into context, token budget
- test_routing.py: grounding_mode correctly set per intent

ACCEPTANCE: Grounding modes work. Personal facts extracted and injected.
Semantic search uses real embeddings. Token budget enforced.
```

---

## Session 6: Sub-Agent Factory

**Goal:** Create any sub-agent via chat. No templates.

```
Read CLAUDE.md §10 (Sub-Agent System).

TASK 1: src/subagents/models.py
- SubAgent (Pydantic BaseModel): id, name, owner_id, grounding_mode="strict",
  channels, kb_namespace, system_prompt, intents, plugins_enabled, active, cost_tracking

TASK 2: src/subagents/configurator.py – Interactive self-configuration
- StateMachine for sub-agent creation via Telegram:
  1. Ask: business name?
  2. Ask: what should the bot handle? (free text → Nexus extracts intents)
  3. Ask: which channels? (inline keyboard)
  4. Ask: share knowledge (text/file/link → build KB)
  5. Ask: should bot use n8n? (if yes, connect workflows)
  6. Generate: system_prompt, intents config, KB entries
  7. Confirm with user → create sub-agent
- Generation uses tier_2 LLM (structured output for intents + prompt)

TASK 3: src/subagents/manager.py – CRUD
- create(config: SubAgentConfig) → SubAgent
- Creates: KB namespace, system prompt, intent config
- list() → all user's sub-agents
- get(id) → sub-agent details + stats
- delete(id) → cleanup all resources
- pause(id) / resume(id)
- Telegram commands: /subagents, /subagent {name} status/pause/resume/kb/logs

TASK 4: src/subagents/runtime.py – Isolated execution
- Process message for sub-agent (own KB, own prompt, STRICT grounding)
- Shared LLM gateway (LiteLLM) but separate cost tracking
- CANNOT access personal plugins (gmail, calendar, etc.)
- CAN access: kb_search, human_escalation, n8n (if configured)
- Route incoming channel messages to correct sub-agent by channel config

TASK 5: Tests in tests/test_subagents.py:
- Create sub-agent via configurator → KB created, prompt generated
- Sub-agent answers from own KB only (STRICT grounding)
- Sub-agent cannot access gmail plugin → blocked
- Sub-agent has separate cost tracking
- Delete → complete cleanup
- Multiple sub-agents: isolated from each other

ACCEPTANCE: Sub-agents created interactively. Isolated execution works.
STRICT grounding enforced. Cost tracking separate.
```

---

## Session 7: Learning & Evolution + Observability Upgrade

**Goal:** Nexus gets smarter over time. Full observability.

```
Read CLAUDE.md §11 (Learning & Evolution).

TASK 1: src/learning/tracker.py
- PerformanceTracker class
- Log per task: success, user_corrections, iterations, cost, latency,
  model_used, intent_predicted, intent_actual, tools_used
- Success heuristic: no user correction within 2 messages = success
- Storage: append-only log (JSON lines file in local, Supabase in prod)

TASK 2: src/learning/analyzer.py
- Analyze performance logs (batch, runs periodically)
- Identify patterns:
  - Intents frequently misrouted
  - Tools that often fail
  - Models that are over/under-used
  - Average cost per intent type
- Output: AnalysisReport with recommendations

TASK 3: src/learning/tuner.py
- Based on AnalysisReport, generate updated configs:
  - Adjust routing confidence thresholds
  - Update intent keyword lists
  - Adjust default tiers for intents
  - Update prompt snippets
- Auto-apply non-breaking changes (keyword additions, threshold tweaks)
- Require user approval for major changes (prompt rewrites, tier changes)
- Store tuning history for rollback

TASK 4: src/learning/competition.py (optional, lower priority)
- For ambiguous requests: multiple specialists propose answers
- Evaluator picks best one based on: confidence, cost, relevance
- Winning agent's approach gets boosted in future routing

TASK 5: UPGRADE src/observability/langfuse.py
- Add new decision log fields from CLAUDE.md §14:
  delegated_to_specialists, guardian_vetoes, budget_overrides, learning_score
- Ensure all Coordinator decisions are logged

TASK 6: Wire learning into Coordinator:
- After each response: PerformanceTracker.log()
- Periodic job (proactive scheduler): Analyzer.run() → Tuner.apply()

TASK 7: Tests in tests/test_learning.py:
- Tracker logs success/failure correctly
- Analyzer identifies misrouted intents
- Tuner generates valid config updates
- Tuning history stored for rollback

ACCEPTANCE: Performance tracking works. Analysis identifies patterns.
Auto-tuning adjusts configs. Decision logs have all fields.
```

---

## Session 8: Golden Questions + Eval + Polish

**Goal:** End-to-end testing. Production readiness. Documentation.

```
Read CLAUDE.md completely for final verification.

TASK 1: Update tests/golden_questions/questions.yaml – 50 test cases:

Personal Agent (35):
- Mail: "Check my emails", "Send email to X about Y", "Summarize inbox"
- Calendar: "What's on tomorrow?", "Book meeting at 3", "Find free time this week"
- Reminders: "Remind me at 9", "List reminders", "Cancel reminder X"
- n8n: "List workflows", "Run weekly report", "Create a workflow that sends me
  a daily summary of unread mails via Telegram"
- KB: "Remember that my birthday is July 18", "What do you know about me?"
- Web: "Search for latest AI news", "What is quantum computing?"
- General: "Hello", "Help", "What can you do?", "How much did I spend today?"
- Voice: (test STT/TTS pipeline with mock audio)
- Multi-agent: "Check mails AND create a workflow" (tests delegation)
- Server: "Run ls on my server" (tests Guardian confirmation)
- Edge cases: prompt injection attempt, gibberish, very long message,
  mixed DE/EN, 10+ turn conversation, budget exceeded scenario

Sub-Agent (15):
- FAQ from KB only, no hallucination
- Unknown question → "I don't know, let me forward to a human"
- Attempted access to personal plugins → blocked
- Citation present for all hard facts
- Sub-agent with n8n: triggers booking workflow
- Sub-agent isolation: can't see other sub-agent's KB

TASK 2: Update tests/golden_questions/runner.py
- Run against live Coordinator (not just keyword routing)
- Measure: intent accuracy, grounding pass rate, cost, latency
- Generate report with pass/fail per test + aggregated metrics

TASK 3: Update scripts/run_evals.py for new test structure
TASK 4: Update .github/workflows/eval.yml (smoke on push, full on release)

TASK 5: README.md – Complete rewrite:
- Hero section: "Nexus – Your Personal AI Agent"
- 30-second pitch (what it does, why it's better)
- Quick Start (docker compose up + /start in Telegram)
- Feature overview with examples
- Plugin connection guide
- Sub-agent creation guide
- Architecture overview (simplified diagram)
- Contributing guide
- License (MIT)

TASK 6: Polish:
- /help command shows all features with examples
- Error handling: every exception → graceful user-facing message
- Rate limiting: max 30 messages/minute per user
- Startup validation: check all required configs exist
- Health endpoint: /health shows connected plugins + budget status

ACCEPTANCE: All 50 golden questions pass. README is complete.
Bot handles errors gracefully. Rate limiting works.
```

---

## Session 9+: Future Extensions

| Session | Feature | When |
|---------|---------|------|
| 9 | Notion integration | After core stable |
| 10 | GitHub integration | After core stable |
| 11 | Terminal/SSH plugin | After Guardian hardened |
| 12 | Home Assistant plugin | On demand |
| 13 | Spotify plugin | On demand |
| 14 | Todoist plugin | On demand |
| 15 | Finance plugin (read-only) | When secure |
| 16 | WhatsApp channel (Baileys) | When Telegram stable |
| 17 | Discord channel | On demand |
| 18 | Web Chat (React widget) | For sub-agent embedding |
| 19 | WhatsApp message plugin | When Baileys stable |
| 20 | Community plugin SDK | When plugin system proven |
| 21 | Admin Dashboard (web) | When multiple sub-agents |
| 22 | Multi-user support | When single-user stable |

---

## Rules for ALL Sessions (Codex MUST follow)

1. **Read CLAUDE.md first** – always, completely
2. **Extend, don't rewrite** – existing working code stays unless explicitly marked [REFACTOR]
3. **All existing tests must keep passing** after every session
4. **Pydantic BaseModel** for all data structures (never dataclasses for new code)
5. **No LangChain, no LangGraph, no CrewAI** – custom code only
6. **Mock external services in tests** – no real Gmail/Calendar/n8n API calls in tests
7. **Guardian Agent reviews every tool call** – no exceptions
8. **Budget Agent tracks every LLM call** – no exceptions
9. **Git commit after each completed TASK** within a session
10. **Telegram is primary channel** – everything must work there first
11. **Error messages to users must be helpful**, not stack traces
12. **Comments in English**, user-facing text follows configured language
13. **n8n is first-class** – not an afterthought, as important as Gmail
