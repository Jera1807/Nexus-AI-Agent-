# Project Nexus – CLAUDE.md (FINAL)

> **THIS IS THE SINGLE SOURCE OF TRUTH.** Read this file FIRST before any code change.
> Written for ChatGPT Codex as executor. Claude orchestrates, Codex builds.
> All architecture decisions are FINAL. Do not deviate without explicit instruction.

---

## 1. What is Nexus?

A **self-hosted, open-source Personal AI Agent** that lives in Telegram (and other channels).
It ACTS on your behalf: reads emails, manages calendars, builds n8n automations, controls
your server, manages smart home devices, does research, tracks finances – and creates &
manages **sub-agents** on demand for any purpose.

- **Primary:** Personal AI Agent (your entire digital life, no artificial limits)
- **Secondary:** Sub-Agent Factory (spin up any bot via chat – business, personal, anything)
- **Philosophy:** "Die Welt steht offen" – no limits, maximum capability, the agent can do
  anything the user connects it to
- **Open Source:** Self-hosted, community-extensible, your data stays yours

## 2. Why Nexus Beats Everything Else

Nexus is designed to address the specific weaknesses of OpenClaw and other agent frameworks:

| Problem (OpenClaw/others) | Nexus Solution |
|---------------------------|----------------|
| 300k+ tokens/msg, €50-100/mo uncontrolled costs | 3-Tier routing + Budget-Agent: €5-15/mo |
| Free hallucination, no fact checking | Grounding-Validator with 3 modes (STRICT/HYBRID/OPEN) |
| No security layer, basic whitelists only | Guardian-Agent reviews every tool call + Firewall |
| No cost awareness per task | Budget-Agent tracks every LLM call, picks cheapest capable model |
| No learning, repeats mistakes | Performance tracking + automatic prompt/config tuning |
| Hardcoded tools, no plugin ecosystem | MCP-based plugin system, `/connect` any service |
| No n8n integration | n8n is first-class: read, trigger, CREATE workflows via chat |
| Complex setup (config files, CLI) | Chat-based onboarding in Telegram |
| No anonymous/cheap web search | SearXNG / DuckDuckGo built-in |
| Basic sub-agents | Self-configuring sub-agents created interactively via chat |
| No voice support | Speech-to-text + text-to-speech in Telegram |
| Single-agent architecture | Multi-agent: Orchestrator + Guardian + Budget + Specialists |

**USP in one sentence:** Open-source personal AI agent that efficiently ACTS in your
digital life through multi-agent coordination, MCP plugins, and n8n automations –
self-hosted, cost-optimized, grounded, learning, no limits.

---

## 3. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  USER (Telegram / WhatsApp / Web / Discord / Voice / ...)    │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│  NEXUS CORE                                                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Multi-Agent Orchestration Layer                       │  │
│  │                                                        │  │
│  │  👔 Manager Agent                                      │  │
│  │     Receives user request, decomposes complex tasks    │  │
│  │     into sub-tasks, delegates to specialists,          │  │
│  │     monitors progress, assembles final response.       │  │
│  │     Simple tasks: handles directly (no delegation).    │  │
│  │                                                        │  │
│  │  🛡️ Guardian Agent                                     │  │
│  │     Reviews EVERY tool call before execution.          │  │
│  │     Policy engine: whitelists, risk scoring,           │  │
│  │     injection detection, confirmation gates.           │  │
│  │     Can VETO any action.                               │  │
│  │                                                        │  │
│  │  💰 Budget Agent                                       │  │
│  │     Tracks token usage + cost per task.                │  │
│  │     Decides: cheap model vs expensive model.           │  │
│  │     Enforces daily budget cap.                         │  │
│  │     Reports cost summaries on request.                 │  │
│  │                                                        │  │
│  │  🔬 Specialist Pool (activated on demand)              │  │
│  │     Research Agent: web search, RAG, source synthesis  │  │
│  │     Coder Agent: code generation, debugging, git ops   │  │
│  │     Writer Agent: emails, documents, creative writing  │  │
│  │     Ops Agent: server commands, n8n workflows, cron    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐       │
│  │ Router   │ │ Memory   │ │ Grounding │ │ Prompt   │       │
│  │ 3-Tier   │ │ 3-Layer  │ │ 3-Mode    │ │ Builder  │       │
│  │ + Budget │ │ +Personal│ │ adaptive  │ │ dynamic  │       │
│  └──────────┘ └──────────┘ └───────────┘ └──────────┘       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  MCP Plugin System (/connect to install)               │  │
│  │                                                        │  │
│  │  BUILT-IN (always available):                          │  │
│  │  📚 Knowledge Base  ⏰ Reminders  🔍 Web Search       │  │
│  │  🆘 Human Escalation                                  │  │
│  │                                                        │  │
│  │  FIRST-PARTY (one-command install):                    │  │
│  │  📧 Gmail          📅 Google Calendar   🔧 n8n        │  │
│  │  📝 Notion         📋 Todoist           🐙 GitHub     │  │
│  │  💬 WhatsApp Msg   🖥️ Terminal/SSH      📁 Filesystem │  │
│  │  🏠 Home Assistant 🎵 Spotify           📊 Finance    │  │
│  │  🔌 Any MCP Server (community plugins)                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Sub-Agent Manager                                     │  │
│  │  User says "Create a bot for X" → Nexus asks           │  │
│  │  questions interactively → self-configures the bot     │  │
│  │  No templates. No config files. Pure conversation.     │  │
│  │  Sub-agents can use n8n + their own plugins.           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Learning & Evolution Layer                            │  │
│  │  📈 Tracks success/failure per task                    │  │
│  │  🔄 Periodic offline analysis of logs (batch LLM)      │  │
│  │  🎯 Auto-updates prompt templates + routing configs    │  │
│  │  🏆 Optional: agent competition (best response wins)   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python 3.12+ (async) | Ecosystem + performance |
| Agent Loop | Custom ReAct (NO LangChain/LangGraph) | Simple, debuggable, fewer deps |
| LLM Gateway | LiteLLM Proxy | Unified API, any provider, budget caps |
| Database | Supabase (Postgres + pgvector) | Free tier, managed, RLS |
| Cache | Redis (Upstash free or local) | Session state, response cache |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 (local) | Multilingual, zero cost |
| Observability | Langfuse Cloud (free tier) | 50k observations/mo |
| Plugins | MCP Protocol (Model Context Protocol) | Industry standard, huge ecosystem |
| Primary Channel | Telegram (aiogram 3.x) | Best bot API, inline UI, voice, free |
| Voice | Whisper (STT) + Edge-TTS or gTTS (TTS) | Free/cheap, good quality |
| Alt Channels | WhatsApp (Baileys), Web (FastAPI WS), Discord | Optional per /connect |
| Automation | n8n (API integration) | Force multiplier, visual workflows |
| Hosting | Hetzner CX11 or local Docker | €3.29/mo or free |

---

## 5. Project Structure

> **IMPORTANT FOR CODEX:** This structure EXTENDS the existing codebase.
> Files marked [EXISTS] are already implemented and should be refactored, not rewritten.
> Files marked [NEW] must be created. Files marked [REFACTOR] need significant changes.

```
project-nexus/
├── CLAUDE.md                        # THIS FILE
├── README.md                        # [REFACTOR] Rewrite as Personal Agent pitch
├── pyproject.toml                   # [REFACTOR] Add new deps (whisper, mcp, etc.)
├── docker-compose.yml               # [REFACTOR] Add n8n service
├── .env.example                     # [REFACTOR] Add new vars
├── .github/workflows/eval.yml       # [EXISTS] Keep
│
├── src/
│   ├── __init__.py                  # [EXISTS]
│   ├── main.py                      # [REFACTOR] Add Telegram bot startup, multi-agent init
│   ├── config.py                    # [REFACTOR] Migrate to pydantic-settings
│   │
│   ├── orchestration/               # [NEW] Multi-Agent Orchestration Layer
│   │   ├── __init__.py
│   │   ├── manager.py               # Manager Agent: task decomposition, delegation
│   │   ├── guardian.py              # Guardian Agent: security review, policy enforcement
│   │   ├── budget.py                # Budget Agent: cost tracking, model selection
│   │   ├── specialists.py           # Specialist pool: research, coder, writer, ops
│   │   ├── task_board.py            # Shared task state (Redis-backed)
│   │   ├── messages.py              # Inter-agent message types (REQUEST, RESULT, CRITIQUE)
│   │   └── coordinator.py           # Coordination logic: simple=direct, complex=delegate
│   │
│   ├── agent/                       # [REFACTOR] Core agent logic
│   │   ├── __init__.py              # [EXISTS]
│   │   ├── loop.py                  # [REFACTOR] Real async ReAct with LiteLLM calls
│   │   ├── prompt.py                # [REFACTOR] Dynamic prompt for personal agent
│   │   └── structured.py            # [REFACTOR] Pydantic BaseModel (not dataclass)
│   │
│   ├── routing/                     # [REFACTOR] Add personal intents + grounding mode
│   │   ├── __init__.py              # [REFACTOR] Add grounding_mode to pipeline
│   │   ├── keyword.py               # [EXISTS] Keep, update intents
│   │   ├── semantic.py              # [EXISTS] Keep, update intents
│   │   ├── llm_classifier.py        # [REFACTOR] Real LLM call instead of placeholder
│   │   ├── confidence.py            # [EXISTS] Keep
│   │   └── models.py                # [REFACTOR] Pydantic BaseModel, add GroundingMode
│   │
│   ├── memory/                      # [REFACTOR] Add personal facts store
│   │   ├── __init__.py              # [EXISTS]
│   │   ├── working.py               # [EXISTS] Keep (Redis adapter later)
│   │   ├── summary.py               # [EXISTS] Keep
│   │   ├── semantic.py              # [EXISTS] Keep (pgvector adapter later)
│   │   ├── context.py               # [EXISTS] Keep
│   │   └── personal.py              # [NEW] Long-term personal facts extraction + storage
│   │
│   ├── grounding/                   # [REFACTOR] Add mode-aware validation
│   │   ├── __init__.py              # [EXISTS]
│   │   ├── validator.py             # [REFACTOR] Mode-aware: STRICT/HYBRID/OPEN
│   │   ├── citations.py             # [EXISTS] Keep
│   │   ├── entity_registry.py       # [EXISTS] Keep
│   │   └── repair.py                # [EXISTS] Keep
│   │
│   ├── plugins/                     # [REFACTOR] MCP-based plugin system
│   │   ├── __init__.py
│   │   ├── manager.py               # [NEW] Plugin discovery, install, enable/disable via /connect
│   │   ├── registry.py              # [REFACTOR] MCP-aware dynamic tool loading
│   │   ├── trimming.py              # [EXISTS] Keep
│   │   ├── firewall.py              # [EXISTS] Keep (Guardian Agent uses this)
│   │   ├── permissions.py           # [EXISTS] Keep
│   │   └── builtin/                 # [REFACTOR] Upgrade built-in plugins
│   │       ├── knowledge_base.py    # [REFACTOR] From tool server to MCP plugin
│   │       ├── reminders.py         # [NEW] APScheduler + Redis, Telegram notifications
│   │       ├── web_search.py        # [NEW] SearXNG / DuckDuckGo (anonymous, free)
│   │       └── human_escalation.py  # [EXISTS] Keep
│   │
│   ├── integrations/                # [NEW] First-party MCP server implementations
│   │   ├── gmail/
│   │   │   ├── server.py            # list_unread, search, read, send, summarize
│   │   │   └── auth.py              # OAuth2 flow via Telegram
│   │   ├── gcalendar/
│   │   │   ├── server.py            # list_events, create, update, delete, find_free_time
│   │   │   └── auth.py              # Shared Google OAuth2
│   │   ├── n8n/
│   │   │   ├── server.py            # list, trigger, create, update, delete workflows
│   │   │   ├── builder.py           # AI-powered workflow JSON generation
│   │   │   └── auth.py              # API key auth
│   │   ├── notion/
│   │   │   ├── server.py            # read/write pages, query databases
│   │   │   └── auth.py              # OAuth2
│   │   ├── github_plugin/
│   │   │   ├── server.py            # repos, issues, PRs, code push
│   │   │   └── auth.py              # Personal access token
│   │   ├── terminal/
│   │   │   └── server.py            # Execute shell commands (sandboxed), SSH to remote
│   │   ├── home_assistant/
│   │   │   └── server.py            # Lights, heating, sensors, automations
│   │   ├── spotify/
│   │   │   └── server.py            # Play, pause, queue, playlists
│   │   ├── todoist/
│   │   │   └── server.py            # Tasks CRUD, projects, labels
│   │   ├── finance/
│   │   │   └── server.py            # Account balances, expense tracking
│   │   ├── whatsapp_msg/
│   │   │   └── server.py            # Read/send WhatsApp messages to contacts
│   │   └── filesystem/
│   │       └── server.py            # Sandboxed local file read/write
│   │
│   ├── channels/                    # [REFACTOR] Real implementations
│   │   ├── __init__.py              # [EXISTS]
│   │   ├── base.py                  # [EXISTS] Keep
│   │   ├── telegram.py              # [REFACTOR] Real aiogram 3.x bot with all features
│   │   ├── web.py                   # [EXISTS] Keep for now
│   │   ├── whatsapp.py              # [EXISTS] Keep stub
│   │   ├── discord.py               # [NEW] Discord bot (optional)
│   │   ├── voice.py                 # [NEW] Whisper STT + TTS pipeline
│   │   └── message.py              # [REFACTOR] Add voice, media, confirmation fields
│   │
│   ├── subagents/                   # [NEW] Sub-Agent Factory
│   │   ├── __init__.py
│   │   ├── manager.py               # Create, configure, deploy sub-agents via chat
│   │   ├── runtime.py               # Isolated execution (own KB, own prompt, STRICT)
│   │   ├── configurator.py          # Interactive self-configuration (no templates!)
│   │   └── models.py                # SubAgent, SubAgentConfig
│   │
│   ├── learning/                    # [NEW] Learning & Evolution Layer
│   │   ├── __init__.py
│   │   ├── tracker.py               # Log success/failure/user corrections per task
│   │   ├── analyzer.py              # Periodic batch analysis of performance logs
│   │   ├── tuner.py                 # Auto-update prompt templates + routing configs
│   │   └── competition.py           # Optional: multiple agents propose, evaluator picks
│   │
│   ├── onboarding/                  # [REFACTOR] Chat-based setup
│   │   ├── __init__.py              # [EXISTS]
│   │   └── flow.py                  # [REFACTOR] Telegram interactive setup (not CLI)
│   │
│   ├── observability/               # [EXISTS] Extend
│   │   ├── __init__.py              # [EXISTS]
│   │   ├── langfuse.py              # [EXISTS] Keep
│   │   ├── pii.py                   # [EXISTS] Keep
│   │   ├── alerts.py                # [EXISTS] Keep
│   │   └── client.py                # [EXISTS] Keep
│   │
│   ├── proactive/                   # [EXISTS] Keep
│   │   ├── __init__.py
│   │   ├── consent.py               # [EXISTS]
│   │   ├── jobs.py                  # [EXISTS]
│   │   └── scheduler.py             # [EXISTS]
│   │
│   ├── tenant/                      # [REFACTOR] Rename concept: tenant → user context
│   │   ├── __init__.py              # [EXISTS]
│   │   ├── manager.py               # [REFACTOR] User context loading (personal + sub-agent)
│   │   ├── models.py                # [REFACTOR] UserContext replaces TenantContext for personal
│   │   └── onboarding.py            # [EXISTS] Keep scaffold utility
│   │
│   ├── tools/                       # [EXISTS] Keep as internal utilities
│   │   ├── __init__.py
│   │   ├── firewall.py              # [EXISTS] Keep (Guardian Agent wraps this)
│   │   ├── permissions.py           # [EXISTS] Keep
│   │   ├── registry.py              # [EXISTS] Keep
│   │   ├── trimming.py              # [EXISTS] Keep
│   │   └── servers/                 # [EXISTS] Keep as legacy, migrate to plugins/
│   │       ├── calendar.py
│   │       ├── customer.py
│   │       └── knowledge_base.py
│   │
│   └── db/                          # [EXISTS] Extend
│       ├── __init__.py
│       ├── client.py                # [EXISTS] Keep adapter pattern
│       ├── supabase.py              # [EXISTS] Keep
│       ├── models.py                # [REFACTOR] Add user, plugin, sub-agent models
│       └── migrations/
│
├── tests/                           # [REFACTOR] Update all tests for new architecture
│   ├── conftest.py                  # [REFACTOR] Add personal agent fixtures
│   ├── golden_questions/
│   │   ├── questions.yaml           # [REFACTOR] Personal agent questions (see Session 8)
│   │   └── runner.py                # [EXISTS] Keep
│   ├── test_agent.py                # [REFACTOR]
│   ├── test_orchestration.py        # [NEW]
│   ├── test_routing.py              # [EXISTS] Update intents
│   ├── test_memory.py               # [EXISTS] Keep
│   ├── test_grounding.py            # [EXISTS] Add mode tests
│   ├── test_plugins.py              # [NEW]
│   ├── test_subagents.py            # [NEW]
│   ├── test_n8n.py                  # [NEW]
│   ├── test_learning.py             # [NEW]
│   ├── test_voice.py                # [NEW]
│   └── ... (existing tests kept)
│
├── configs/
│   ├── litellm_config.yaml          # [REFACTOR] Better model choices, budget
│   ├── nexus.yaml                   # [NEW] Core personal agent settings
│   ├── intents/
│   │   ├── personal.yaml            # [NEW] Personal assistant intents (see §7)
│   │   └── subagent_base.yaml       # [NEW] Base intents for sub-agents
│   ├── plugins/
│   │   ├── available.yaml           # [NEW] All known plugins with metadata
│   │   └── enabled.yaml             # [NEW] User's active plugins
│   ├── policies/
│   │   ├── guardian.yaml            # [NEW] Guardian agent rules
│   │   └── budget.yaml              # [NEW] Budget limits and model preferences
│   ├── defaults/                    # [EXISTS] Keep for sub-agent defaults
│   │   ├── channels.yaml
│   │   ├── intents.yaml
│   │   ├── prompt_template.yaml
│   │   └── tools.yaml
│   └── tenants/                     # [EXISTS] Keep for sub-agent configs
│       └── example_tenant/
│
├── scripts/
│   ├── setup.sh                     # [REFACTOR] One-command setup
│   ├── run_evals.py                 # [EXISTS] Keep
│   ├── calibrate.py                 # [EXISTS] Keep
│   └── onboard_tenant.py            # [EXISTS] Keep for sub-agent CLI
│
└── docs/
    └── architecture_rebuild_plan.md # [EXISTS] Superseded by this CLAUDE.md
```

---

## 6. Multi-Agent Orchestration (Core Innovation)

This is what sets Nexus apart from OpenClaw and every other open-source agent.

### 6.1 Manager Agent

```python
class ManagerAgent:
    """
    Entry point for every user message. Decides:
    - Simple request → handle directly via single ReAct loop
    - Complex request → decompose into TaskGraph, delegate to specialists
    
    Decision criteria for delegation:
    - Multiple distinct steps needed (e.g., "check mails AND create n8n workflow")
    - Multiple tools/domains involved
    - Requires research + synthesis
    - User explicitly asks for multi-step task
    
    For simple requests (greetings, single-tool queries, KB lookups):
    - Skips delegation overhead
    - Runs single ReAct loop directly
    - This handles ~70% of all requests efficiently
    """
```

### 6.2 Guardian Agent

```python
class GuardianAgent:
    """
    Reviews EVERY tool call before execution. Zero-trust approach.
    
    Policy layers:
    1. Whitelist/Blacklist: allowed commands, paths, domains (from guardian.yaml)
    2. Risk scoring: each tool call gets a risk score (low/medium/high/critical)
    3. Injection detection: prompt injection patterns in arguments
    4. Confirmation gates:
       - Low risk: auto-approve
       - Medium risk: log + approve
       - High risk: require user confirmation via inline keyboard
       - Critical risk: BLOCK + alert user
    
    The Guardian wraps src/tools/firewall.py (existing code) with the
    additional policy engine and confirmation flow.
    """
```

### 6.3 Budget Agent

```python
class BudgetAgent:
    """
    Tracks every LLM call's token usage and cost.
    
    Responsibilities:
    - Select cheapest model that can handle the task (based on routing tier)
    - Track cumulative daily spend
    - Enforce daily budget cap (configurable, default $2.00)
    - Provide cost reports on request ("/costs today", "/costs this month")
    - Alert if approaching budget limit
    - Cache responses to avoid duplicate LLM calls
    
    Model selection override:
    - If Budget Agent says "use tier_1" but task needs tier_3,
      Manager Agent can escalate (Budget Agent logs the override)
    """
```

### 6.4 Specialist Agents

Activated only when Manager Agent delegates. Each specialist:
- Has a focused system prompt
- Has access to specific plugins only
- Returns structured results to Manager Agent

| Specialist | Focus | Plugins Access |
|-----------|-------|---------------|
| Research Agent | Web search, RAG, source synthesis | web_search, knowledge_base |
| Coder Agent | Code generation, debugging, git ops | github, terminal, filesystem |
| Writer Agent | Emails, documents, creative writing | gmail, notion, filesystem |
| Ops Agent | Server management, n8n workflows | n8n, terminal, home_assistant |

### 6.5 Task Board (Inter-Agent Communication)

```python
class TaskBoard:
    """
    Shared state between agents. Redis-backed.
    
    Message types:
    - REQUEST: Manager → Specialist (task assignment)
    - RESULT: Specialist → Manager (completed work)
    - CRITIQUE: Guardian → Manager (security concern)
    - BUDGET_CHECK: Manager → Budget (cost query)
    - BUDGET_RESPONSE: Budget → Manager (approved/denied + model)
    
    Each task has: id, status (pending/running/done/failed),
    assigned_agent, result, cost, tokens_used
    """
```

### 6.6 Coordination Flow

```
User: "Check my unread mails and create an n8n workflow that 
       forwards invoices to my Google Drive"

Manager Agent:
  → Analyzes: 2 distinct tasks + 2 domains (mail, automation)
  → Creates TaskGraph:
     Task 1: [Research Agent] Check unread mails, find invoices
     Task 2: [Ops Agent] Create n8n workflow (depends on Task 1 output)
  
  → Budget Agent: "Task 1 = tier_1 ($0.001), Task 2 = tier_2 ($0.01)"
  → Dispatches Task 1 to Research Agent

Research Agent:
  → Guardian Agent reviews: gmail.list_unread → LOW risk → approved
  → Calls gmail plugin → returns 3 invoices found
  → RESULT → Manager

Manager Agent:
  → Dispatches Task 2 to Ops Agent with invoice patterns

Ops Agent:
  → Generates n8n workflow JSON (Gmail trigger → filter → Google Drive)
  → Guardian Agent reviews: n8n.create_workflow → MEDIUM risk
  → Sends preview to user via Telegram inline keyboard
  
User: [✅ Create & Activate]

Ops Agent:
  → Guardian Agent reviews: n8n.activate → HIGH risk → confirms with user
  → Creates and activates workflow
  → RESULT → Manager

Manager Agent:
  → Assembles final response: "Found 3 invoices. Created workflow
     'Invoice to Drive' – runs on every new mail with invoice attachment."
```

---

## 7. Grounding Modes

```python
class GroundingMode(str, Enum):
    STRICT = "strict"    # Sub-agents: ONLY KB facts, citations mandatory
    HYBRID = "hybrid"    # Personal with KB: KB preferred, LLM knowledge allowed (marked)
    OPEN = "open"        # Personal general: Full LLM capabilities, no grounding needed
```

**Automatic mode selection by the Router:**

| Intent Category | Grounding Mode | Why |
|----------------|---------------|-----|
| mail, calendar, reminder, automation | OPEN | Tool results are ground truth |
| knowledge (user has KB) | HYBRID | Check KB first, allow LLM fallback |
| general, smalltalk, web_search | OPEN | LLM knowledge is fine |
| sub-agent messages | STRICT | Business bots must only state KB facts |
| terminal, server ops | OPEN | Command output is ground truth |

**Grounding Validator behavior per mode:**
- **STRICT:** Hard-fact detection → citation check → repair-or-fallback. No citation = no answer.
- **HYBRID:** Check KB. If KB hit: validate + cite. If no KB hit: allow LLM answer, mark as "[unverified]".
- **OPEN:** Skip grounding entirely. Tool results and LLM knowledge are accepted as-is.

---

## 8. Plugin System (MCP-based)

Every integration is an MCP (Model Context Protocol) server. Users install what they need via `/connect`.

### Built-in Plugins (always loaded, ship with Nexus)

| Plugin | Capabilities |
|--------|-------------|
| `knowledge_base` | Search personal KB, add/remove entries, auto-extract facts |
| `reminders` | Set/list/cancel reminders (Redis + APScheduler), Telegram notifications |
| `web_search` | Anonymous search via SearXNG or DuckDuckGo API (free) |
| `human_escalation` | "I don't know" fallback, route to human |

### First-Party Plugins (install via `/connect {name}`)

| Plugin | Capabilities | Auth |
|--------|-------------|------|
| `gmail` | Read, search, send, label, summarize emails | OAuth2 |
| `gcalendar` | Read, create, update, delete events; find free time | OAuth2 |
| `n8n` | List, trigger, CREATE, edit, delete workflows | API Key |
| `notion` | Read/write pages, query databases | OAuth2 |
| `todoist` | Tasks CRUD, projects, labels | API Key |
| `github` | Repos, issues, PRs, code push | PAT |
| `terminal` | Shell commands (sandboxed), SSH to remote servers | Key-based |
| `home_assistant` | Lights, heating, sensors, automations | API Key |
| `spotify` | Play, pause, queue, search, playlists | OAuth2 |
| `finance` | Account balances, expense tracking (read-only!) | API Key |
| `whatsapp_msg` | Read/send WhatsApp messages to contacts | Baileys bridge |
| `filesystem` | Read/write local files (sandboxed directory) | None |

### n8n Integration (FIRST-CLASS – Nexus Killer Feature)

n8n is the force multiplier. If Nexus can create n8n workflows, it can indirectly do ANYTHING.

**Three levels:**
1. **Read:** "What workflows do I have?" → `n8n.list_workflows()`
2. **Trigger:** "Run my weekly report" → `n8n.trigger_workflow(id)`
3. **Create:** "Build a workflow that..." → AI generates n8n JSON → validates → deploys

**n8n workflow creation flow:**
```
User: "Create a workflow that checks Gmail every morning for newsletters
       and summarizes them in Notion"

Ops Agent (via n8n plugin):
  1. Generates workflow spec:
     - Cron trigger: every day 08:00
     - Gmail node: search label:newsletter, newer_than:1d
     - AI node: summarize (using Nexus's LLM via HTTP)
     - Notion node: create page in "Newsletter Summaries"
  
  2. Converts to n8n-compatible JSON
  3. Validates JSON structure
  4. Sends preview to user:
     📋 "Daily Newsletter Digest"
     1. ⏰ Every day at 08:00
     2. 📧 Fetch newsletters from Gmail
     3. 🤖 Summarize with AI
     4. 📝 Save to Notion
     [✅ Create & Activate] [✏️ Modify] [❌ Cancel]
  
  5. On confirm → n8n API create + activate
```

### Community Plugins (future)

Any MCP server can be added. Nexus discovers and installs via URL or registry.

---

## 9. Personal Intents (configs/intents/personal.yaml)

These replace the old business-focused intents:

```yaml
intents:
  mail:
    keywords: [mail, email, inbox, send, nachricht, postfach]
    examples: ["check my mails", "send email to X", "summarize inbox"]
    default_tier: tier_1
    risk_level: low
    grounding_mode: open
    plugins: [gmail]

  calendar:
    keywords: [calendar, termin, meeting, schedule, kalender, event]
    examples: ["what's on tomorrow", "book meeting at 3", "find free time"]
    default_tier: tier_1
    risk_level: medium
    grounding_mode: open
    plugins: [gcalendar]

  reminder:
    keywords: [remind, erinner, todo, aufgabe, reminder]
    examples: ["remind me at 9", "list reminders", "cancel reminder"]
    default_tier: tier_1
    risk_level: low
    grounding_mode: open
    plugins: [reminders, todoist]

  automation:
    keywords: [workflow, automation, n8n, automate, automatisier]
    examples: ["create workflow", "list workflows", "run weekly report"]
    default_tier: tier_2
    risk_level: medium
    grounding_mode: open
    plugins: [n8n]

  knowledge:
    keywords: [remember, merke, wissen, know, fact, speicher]
    examples: ["remember that X", "what do you know about Y"]
    default_tier: tier_1
    risk_level: low
    grounding_mode: hybrid
    plugins: [knowledge_base]

  subagent:
    keywords: [create bot, erstelle bot, sub-agent, chatbot]
    examples: ["create a bot for my business", "manage my bots"]
    default_tier: tier_2
    risk_level: medium
    grounding_mode: open
    plugins: []

  web_search:
    keywords: [search, suche, google, look up, find, news]
    examples: ["search for X", "what is Y", "latest news about Z"]
    default_tier: tier_1
    risk_level: low
    grounding_mode: open
    plugins: [web_search]

  server:
    keywords: [terminal, server, ssh, install, command, shell, deploy]
    examples: ["run command X", "install Y on server", "check server status"]
    default_tier: tier_2
    risk_level: critical
    grounding_mode: open
    plugins: [terminal]

  smart_home:
    keywords: [light, licht, heizung, heating, temperature, home]
    examples: ["turn on lights", "set temperature to 21", "home status"]
    default_tier: tier_1
    risk_level: medium
    grounding_mode: open
    plugins: [home_assistant]

  music:
    keywords: [play, musik, song, spotify, playlist, pause]
    examples: ["play something chill", "what's playing", "next song"]
    default_tier: tier_1
    risk_level: low
    grounding_mode: open
    plugins: [spotify]

  finance:
    keywords: [balance, kontostand, ausgaben, expenses, money, budget]
    examples: ["what's my balance", "expenses this month"]
    default_tier: tier_1
    risk_level: high
    grounding_mode: open
    plugins: [finance]

  code:
    keywords: [code, programming, debug, git, repo, commit, push]
    examples: ["create issue on repo X", "push code", "debug this"]
    default_tier: tier_2
    risk_level: medium
    grounding_mode: open
    plugins: [github, terminal]

  general:
    keywords: [hello, hallo, hi, danke, thanks, help, hilfe]
    examples: ["hello", "what can you do", "help"]
    default_tier: tier_1
    risk_level: low
    grounding_mode: open
    plugins: []

  unknown:
    keywords: []
    default_tier: tier_2
    risk_level: low
    grounding_mode: open
    plugins: [web_search]
```

---

## 10. Sub-Agent System

Sub-agents are NOT created from templates. Nexus asks the user interactively what the bot should do and configures itself.

```python
class SubAgent(BaseModel):
    id: str
    name: str
    owner_id: str                     # Nexus user who created it
    grounding_mode: str = "strict"    # Always strict for business bots
    channels: list[str]               # ["whatsapp", "telegram", "web"]
    channel_configs: dict             # Bot tokens, phone numbers, etc.
    kb_namespace: str                 # Isolated KB partition
    system_prompt: str                # Generated by Nexus during setup
    intents: dict                     # Generated based on conversation
    plugins_enabled: list[str]        # Can include n8n!
    active: bool
    cost_tracking: dict               # Separate from personal costs
```

**Interactive creation flow:**
```
User: "Create a customer service bot for my nail school"

Nexus: Let me set that up. A few questions:

  What's the business name?
User: Beauty & Nailschool Bochum

  What should the bot handle? Tell me in your own words.
User: Answer questions about prices, courses, opening hours.
      Also handle appointment bookings and cancellations.

  Got it. I'll set up:
  - FAQ capability (prices, courses, hours)
  - Appointment booking
  - Cancellation handling
  - Complaint escalation to you

  Which channels?
  [Telegram] [WhatsApp] [Web Widget] [All]
User: WhatsApp

  Can you share your price list and business info?
  (Send text, file, or link – I'll build the knowledge base)
User: [sends PDF]

Nexus: ✅ Bot "Nailschool Bot" created!
  📋 KB: 24 entries extracted from your PDF
  💬 Channel: WhatsApp (setup link: ...)
  🧠 Mode: Strict (only answers from verified KB)
  🔧 Plugins: kb_search, human_escalation

  Should this bot also handle bookings via n8n?
User: Yes

Nexus: I'll connect n8n. The bot can now trigger your
       booking workflow when customers want appointments.
```

**Sub-agent isolation rules:**
- Own KB namespace (cannot see personal KB)
- Own system prompt and intents
- STRICT grounding always
- Shared LLM gateway but separate cost tracking
- Can use: kb_search, human_escalation, n8n (if enabled)
- CANNOT use: personal plugins (gmail, calendar, spotify, etc.)

---

## 11. Learning & Evolution Layer

```python
class PerformanceTracker:
    """
    For every completed task, logs:
    - success: bool (user satisfied? no corrections needed?)
    - corrections: int (how many times user corrected the agent)
    - iterations: int (ReAct loops needed)
    - cost: float
    - latency_ms: int
    - model_used: str
    - intent_predicted vs intent_actual
    """

class PolicyTuner:
    """
    Runs periodically (cron, e.g., weekly):
    1. Batch-analyzes performance logs
    2. Identifies patterns (e.g., "mail intent often misrouted")
    3. Generates updated prompt snippets / routing configs
    4. Applies updates (with user approval for major changes)
    
    Uses a cheap batch LLM call (tier_1) for analysis.
    Stores tuning history for rollback.
    """
```

---

## 12. Channels & Voice

### Telegram (Primary)

Full aiogram 3.x implementation:
- Text messages → UnifiedMessage → Agent pipeline
- `/start` → Onboarding flow
- `/connect {plugin}` → Plugin installation
- `/subagents` → Sub-agent management
- `/costs` → Budget report
- `/facts` → Personal facts CRUD
- `/help` → Feature overview
- Inline keyboards for confirmations
- Voice messages → Whisper STT → process → TTS → voice reply

### Voice Pipeline

```
Voice message (Telegram/WhatsApp)
  → Download audio file
  → Whisper STT (local or API) → text
  → Normal agent pipeline → response text
  → Edge-TTS / gTTS → audio file
  → Send voice reply
```

### Other Channels (later sessions)

- WhatsApp (Baileys bridge)
- Web Chat (FastAPI WebSocket)
- Discord (discord.py)
- All via same UnifiedMessage → Agent pipeline

---

## 13. Architecture Rules (for Codex)

### Rule 1: Three-Tier Model Routing
```
Tier 1 (70% of requests): DeepSeek V3 / Gemini 2.0 Flash → cheapest
Tier 2 (25% of requests): Claude Haiku / GPT-4.1-mini → balanced
Tier 3 (5% of requests):  Claude Sonnet / GPT-4.1 → most capable
```
Budget Agent can override tier selection. Daily cap: configurable (default $2.00).

### Rule 2: Memory Budget
```
Layer 1: Working memory (last N turns) → ~400 tokens (Redis)
Layer 2: Running summary → ~200 tokens (compressed every 3 msgs)
Layer 3: Semantic recall → ~300 tokens (pgvector personal KB)
Layer 4: Personal facts → ~100 tokens (long-term user facts)
Total hard limit: ~1,200 tokens context injection
```

### Rule 3: Plugin Security (Guardian Agent enforces)
- Tool Firewall: structured calls only, Pydantic validation
- Injection detection on all string arguments
- Permission scopes: read/write per plugin
- Confirmation gates: low=auto, medium=log, high=confirm, critical=block
- User text NEVER passed directly as tool argument
- All actions logged for audit

### Rule 4: Dynamic Tool Loading
- Only load plugin schemas relevant to detected intent
- Built-in plugins always loaded (~400 tokens)
- Saves 60-80% tool tokens per request

### Rule 5: Tool-Result Trimming
- Per-plugin byte limits (configurable)
- Global cap: 4,096 bytes across all tool results per ReAct loop

### Rule 6: Sub-Agent Isolation
- Each sub-agent: own KB, own prompt, own intents, STRICT grounding
- Shared LLM gateway, separate cost tracking
- Cannot access personal plugins
- Conversations private (not visible to personal agent)

### Rule 7: PII Handling
- Personal data encrypted at rest (Supabase)
- Log redaction before Langfuse (existing pii.py)
- Sub-agent conversations: PII minimized

### Rule 8: EU AI Act Compliance
- KI-Disclosure on all channels (configurable text)
- Sub-agents: mandatory disclosure in first message

---

## 14. Decision Logs (every request)

Fields: `request_id`, `user_id`, `is_subagent`, `subagent_id`, `intent`,
`router_confidence`, `tier`, `risk_level`, `tools_called`, `tools_success`,
`rag_top_score`, `cache_hit`, `grounding_mode`, `validator_pass`,
`citation_count`, `confidence_score`, `agent_loops`, `total_tokens`,
`cost_usd`, `latency_ms`, `delegated_to_specialists`, `guardian_vetoes`,
`budget_overrides`, `learning_score`

---

## 15. Onboarding Flow (Telegram)

```
/start →

Nexus: 👋 Hey! I'm Nexus, your personal AI agent.
       I can manage your mails, calendar, automations, and much more.

       Quick setup (2 minutes):

       1. Which LLM provider?
       [OpenRouter] [OpenAI Key] [Anthropic Key] [Local/Ollama]

User: OpenRouter

       2. What should I call you?
User: Jerome

       3. Preferred language?
       [Deutsch] [English] [Both]
User: Both

       ✅ Ready, Jerome!

       Built-in capabilities:
       ✅ Reminders & To-Dos
       ✅ Web Search
       ✅ Personal Knowledge Base
       ✅ Voice Messages

       Connect more:
       /connect gmail     📧 Emails
       /connect calendar  📅 Schedule
       /connect n8n       🔧 Automations
       /connect notion    📝 Notes
       /connect terminal  🖥️ Server
       /connect github    🐙 Code
       /connect spotify   🎵 Music
       /connect home      🏠 Smart Home

       Or just talk to me! Try:
       "Remind me to buy milk tomorrow at 9"
       "What's the latest AI news?"
       "Create a customer service bot for my shop"
```

---

## 16. Cost Targets

- Self-hosted: only LLM API costs
- Light personal use: €5-10/mo (mostly tier_1)
- Heavy use + n8n + sub-agents: €15-25/mo
- Per sub-agent: +€5-10/mo (depending on usage)
- Daily cap: configurable (default $2.00)
- OpenRouter free tier: works for testing

---

## 17. Key Libraries

```
# Core
litellm, fastapi, uvicorn, pydantic>=2.0, pydantic-settings, httpx, orjson

# Agent
aiogram>=3.10, sentence-transformers, tiktoken, apscheduler

# Database
supabase-py, redis, sqlalchemy, psycopg[binary]

# Observability
langfuse, structlog, faker

# Voice
openai-whisper OR faster-whisper, edge-tts OR gtts

# MCP
mcp (Model Context Protocol SDK)

# Utilities
pyyaml, python-dotenv

# Dev
pytest, pytest-asyncio, ruff, mypy
```

---

## 18. Interfaces Between Modules

### UnifiedMessage (channels → orchestration)
```python
class UnifiedMessage(BaseModel):
    id: str
    channel: str                              # "telegram", "whatsapp", "web", "discord"
    sender_id: str
    text: str | None = None
    voice_audio: bytes | None = None          # Raw audio if voice message
    media: list[MediaAttachment] | None = None
    timestamp: datetime
    is_subagent_message: bool = False
    subagent_id: str | None = None
    metadata: dict = {}
```

### RoutingDecision (routing → orchestration)
```python
class RoutingDecision(BaseModel):
    intent: str
    tier: Literal["tier_1", "tier_2", "tier_3"]
    risk_level: Literal["low", "medium", "high", "critical"]
    confidence: float
    grounding_mode: Literal["strict", "hybrid", "open"]
    plugins_to_load: list[str]
    requires_confirmation: bool
    should_delegate: bool                     # True if multi-agent needed
    source: Literal["keyword", "semantic", "llm_classifier"]
```

### AgentResponse (orchestration → channels)
```python
class AgentResponse(BaseModel):
    text: str
    citations: list[Citation] = []
    voice_audio: bytes | None = None          # TTS output if voice request
    ui_actions: list[UIAction] | None = None  # Inline keyboard buttons
    fallback_text: str
    confidence: float
    decision_log: DecisionLog
```

### ContextBundle (memory → agent)
```python
class ContextBundle(BaseModel):
    last_turns: list[Turn]
    summary: str
    rag_snippets: list[Chunk]
    personal_facts: list[str]
    total_tokens: int                         # Must be ≤ 1,200
```

---

## 19. Code Style Rules (for Codex)

1. Python 3.12+, async/await everywhere
2. Type hints mandatory, Pydantic BaseModel for all data structures (NOT dataclasses)
3. No hardcoded business logic – everything via config/plugins
4. No LangChain, no LangGraph, no CrewAI – custom ReAct only
5. Tests: pytest + pytest-asyncio, mocks for all external services
6. Logging: structlog (JSON format)
7. Every module must be independently testable
8. Git commit after every completed module
9. Existing tests must keep passing after refactors
10. Comments in English, user-facing text in configured language (default: both DE/EN)
