# Project Nexus – CLAUDE.md

> Single source of truth for Claude Code sessions. Read FIRST.

## What is Nexus?

A **self-hosted, open-source Personal AI Agent** that lives in your Telegram (or other channels).
It can act on your behalf: read emails, manage calendars, build automations, do research –
and create & manage **sub-agents** (e.g. customer service bots for your business).

**Primary:** Personal AI Assistant (your daily life + productivity)
**Secondary:** Sub-Agent Factory (spin up business chatbots on demand)
**Open Source:** Users self-host, own their data, extend with plugins

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  YOU (Telegram / Web / WhatsApp)                    │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  NEXUS CORE (Personal Agent)                        │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐  │
│  │ Router  │ │ Memory  │ │ Grounding│ │ Prompt  │  │
│  │ 3-Tier  │ │ 3-Layer │ │ flexible │ │ Builder │  │
│  └─────────┘ └─────────┘ └──────────┘ └─────────┘  │
│  ┌──────────────────────────────────────────────┐   │
│  │  MCP Plugin System                           │   │
│  │  📧 Gmail  📅 Calendar  🔧 n8n  📝 Notion   │   │
│  │  🔍 Web    📁 Files     🗄️ DB   🔌 Custom   │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Sub-Agent Manager                           │   │
│  │  🤖 Nailschool Bot  🤖 Pizzeria Bot  🤖 ... │   │
│  │  (each: own KB, own channel, strict ground.) │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Design Principles

1. **Personal-first** – Core use case is YOU talking to YOUR agent
1. **Action-oriented** – Not just answering questions, but doing things
1. **Plugin-based** – MCP servers as plugins; install only what you need
1. **Self-hosted** – Your data stays on your machine/server
1. **Sub-agents as feature** – Business chatbots are a capability, not the product
1. **Open Source** – Community can build plugins, share configs, contribute

## Tech Stack

|Component      |Choice                                       |Why                                      |
|---------------|---------------------------------------------|-----------------------------------------|
|Language       |Python 3.12+ (async)                         |Performance + ecosystem                  |
|Agent Loop     |Custom ReAct (NO LangGraph)                  |Simple, debuggable, fewer deps           |
|LLM Gateway    |LiteLLM Proxy                                |Unified API, any provider, budget control|
|Database       |Supabase (Postgres + pgvector)               |Free tier, managed, RLS                  |
|Cache          |Redis (Upstash free or local)                |Session state, response cache            |
|Embedding      |paraphrase-multilingual-MiniLM-L12-v2 (local)|Multilingual, 0 cost                     |
|Observability  |Langfuse Cloud (free tier)                   |50k obs/mo, optional                     |
|Plugins        |MCP Protocol                                 |Industry standard, huge ecosystem        |
|Primary Channel|Telegram (aiogram 3.x)                       |Best bot API, inline UI, free            |
|Alt Channels   |WhatsApp (Baileys), Web (FastAPI WS)         |Optional                                 |
|Hosting        |Hetzner CX11 or local Docker                 |3.29€/mo or free                         |

## Project Structure

```
project-nexus/
├── CLAUDE.md                    # THIS FILE
├── README.md                    # Setup guide for end users
├── pyproject.toml
├── docker-compose.yml           # Nexus + LiteLLM + Redis
├── .env.example
├── .github/workflows/
│   └── eval.yml
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py                # Pydantic Settings (.env)
│   │
│   ├── agent/                   # Core agent logic
│   │   ├── __init__.py
│   │   ├── loop.py              # ReAct loop (async, max 3 iterations)
│   │   ├── prompt.py            # Dynamic prompt builder
│   │   └── structured.py        # Output schemas (Pydantic)
│   │
│   ├── routing/                 # Intent classification + model selection
│   │   ├── __init__.py
│   │   ├── keyword.py           # Step 1: keyword pre-filter
│   │   ├── semantic.py          # Step 2: embedding similarity
│   │   ├── llm_classifier.py    # Step 3: LLM fallback
│   │   ├── confidence.py        # Heuristic confidence scoring
│   │   └── models.py            # RoutingDecision, Tier, RiskLevel
│   │
│   ├── memory/                  # Context management
│   │   ├── __init__.py
│   │   ├── working.py           # Last N turns (Redis)
│   │   ├── summary.py           # Running summary (compressed)
│   │   ├── semantic.py          # RAG from personal KB (pgvector)
│   │   ├── context.py           # Budget-enforced context assembly
│   │   └── personal.py          # Long-term personal facts store
│   │
│   ├── grounding/               # Fact validation (mode-dependent)
│   │   ├── __init__.py
│   │   ├── validator.py         # Deterministic grounding check
│   │   ├── citations.py         # Citation engine
│   │   ├── entity_registry.py   # Known facts registry
│   │   └── repair.py            # 1-step repair
│   │
│   ├── plugins/                 # MCP Plugin System
│   │   ├── __init__.py
│   │   ├── manager.py           # Plugin discovery, install, enable/disable
│   │   ├── registry.py          # Active plugins + dynamic tool loading
│   │   ├── trimming.py          # Result trimming (per-plugin + global cap)
│   │   ├── firewall.py          # Structured calls, injection protection
│   │   ├── permissions.py       # Scopes + confirmation gates
│   │   └── builtin/             # Built-in plugins (ship with Nexus)
│   │       ├── knowledge_base.py    # Personal KB search
│   │       ├── reminders.py         # Scheduled reminders
│   │       ├── web_search.py        # Web search
│   │       └── human_escalation.py  # Fallback
│   │
│   ├── integrations/            # First-party MCP server configs
│   │   ├── gmail/               # Gmail read/send/search
│   │   ├── gcalendar/           # Google Calendar CRUD
│   │   ├── n8n/                 # n8n workflow CRUD + trigger
│   │   ├── notion/              # Notion pages/databases
│   │   └── filesystem/          # Local file access
│   │
│   ├── channels/                # Communication interfaces
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract channel
│   │   ├── telegram.py          # Primary: aiogram 3.x
│   │   ├── web.py               # WebSocket chat
│   │   ├── whatsapp.py          # Baileys bridge (optional)
│   │   └── message.py           # UnifiedMessage model
│   │
│   ├── subagents/               # Sub-Agent Factory
│   │   ├── __init__.py
│   │   ├── manager.py           # Create, configure, deploy sub-agents
│   │   ├── runtime.py           # Sub-agent execution (isolated context)
│   │   ├── templates.py         # Pre-built templates (customer service, FAQ, ...)
│   │   └── models.py            # SubAgent, SubAgentConfig
│   │
│   ├── onboarding/              # First-run setup (Telegram-based)
│   │   ├── __init__.py
│   │   └── flow.py              # Interactive setup via chat
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── langfuse.py          # Tracing + decision logs
│   │   ├── pii.py               # PII redaction
│   │   └── alerts.py            # Telegram alerts
│   │
│   └── db/
│       ├── __init__.py
│       ├── supabase.py
│       ├── models.py
│       └── migrations/
│
├── tests/
│   ├── conftest.py
│   ├── golden_questions/
│   │   ├── questions.yaml
│   │   └── runner.py
│   ├── test_agent.py
│   ├── test_routing.py
│   ├── test_memory.py
│   ├── test_grounding.py
│   ├── test_plugins.py
│   ├── test_subagents.py
│   └── test_n8n.py
│
├── configs/
│   ├── litellm_config.yaml      # 3-tier model routing
│   ├── nexus.yaml               # Core Nexus settings
│   ├── intents/
│   │   ├── personal.yaml        # Personal assistant intents
│   │   └── subagent_base.yaml   # Base intents for sub-agents
│   ├── plugins/
│   │   ├── available.yaml       # All known plugins
│   │   └── enabled.yaml         # User's active plugins
│   └── subagents/               # Sub-agent configs (created at runtime)
│       └── example_bot/
│           ├── config.yaml
│           ├── intents.yaml
│           └── kb_seed.yaml
│
└── scripts/
    ├── setup.sh                 # One-command setup
    ├── run_evals.py
    └── calibrate.py
```

## Grounding Modes

The agent operates in different grounding modes depending on context:

```python
class GroundingMode(str, Enum):
    STRICT = "strict"    # Sub-agents: ONLY KB facts, citations mandatory
    HYBRID = "hybrid"    # Personal with KB: KB preferred, LLM knowledge allowed (marked)
    OPEN = "open"        # Personal general: Full LLM capabilities, KB optional
```

**How it works in practice:**

- You ask “What’s on my calendar tomorrow?” → OPEN mode (tool call, no KB needed)
- You ask “What’s the cancellation policy?” and you have a KB → HYBRID (checks KB first)
- Your Nailschool sub-agent gets asked “What’s the price?” → STRICT (only KB, with citation)
- You ask “Explain quantum physics” → OPEN mode (LLM knowledge, no grounding needed)

**Mode selection is automatic:**

- Core Nexus agent: HYBRID (default) or OPEN (if no KB loaded)
- Sub-agents: STRICT (always, that’s the point of business bots)
- Override per intent possible in config

## Plugin System (MCP-based)

Every integration is an MCP server. Users install what they need.

### Built-in Plugins (ship with Nexus)

|Plugin            |Capabilities                            |Always loaded?|
|------------------|----------------------------------------|--------------|
|`knowledge_base`  |Search personal KB, add/remove entries  |Yes           |
|`reminders`       |Set/list/cancel reminders (Redis-backed)|Yes           |
|`web_search`      |Search the web (via SearXNG or API)     |Yes           |
|`human_escalation`|“I don’t know” fallback                 |Yes           |

### First-Party Integrations (one-command install)

|Plugin      |Capabilities                                       |Auth   |
|------------|---------------------------------------------------|-------|
|`gmail`     |Read, search, send, label, summarize emails        |OAuth2 |
|`gcalendar` |Read, create, update, delete events; find free time|OAuth2 |
|`n8n`       |List, trigger, create, edit, delete workflows      |API Key|
|`notion`    |Read/write pages, query databases                  |OAuth2 |
|`filesystem`|Read/write local files (sandboxed directory)       |None   |

### n8n Integration (First-Class)

n8n is special because it’s a force multiplier – Nexus can use n8n to do things it can’t do natively.

**Three levels of n8n interaction:**

1. **Trigger**: “Run my weekly report workflow” → executes existing workflow
1. **Read**: “What workflows do I have?” → lists and describes workflows
1. **Create**: “Build a workflow that monitors my inbox for invoices and saves them to Google Drive” → generates n8n workflow JSON via API

**n8n workflow creation flow:**

```
User: Create a workflow that checks my Gmail every morning for
      newsletters and summarizes them in Notion

Nexus thinks:
  1. Trigger node: Cron, every day 08:00
  2. Gmail node: Search for label:newsletter, newer_than:1d
  3. AI node: Summarize each email (using Nexus's own LLM)
  4. Notion node: Create page in "Newsletter Summaries" database

Nexus: Here's the workflow I'll create:
  📋 "Daily Newsletter Digest"
  1. ⏰ Every day at 08:00
  2. 📧 Fetch newsletters from Gmail
  3. 🤖 Summarize with AI
  4. 📝 Save to Notion

  [✅ Create & Activate] [✏️ Modify] [❌ Cancel]

User: Create & Activate
Nexus: ✅ Workflow created and active in n8n.
       First run: Tomorrow 08:00
```

### Community Plugins (future)

Anyone can build an MCP server and share it. Nexus discovers and installs them.

## Sub-Agent System

Sub-agents are isolated chatbot instances that Nexus creates and manages for you.

```python
class SubAgent(BaseModel):
    id: str
    name: str                     # "Nailschool Bot"
    owner_id: str                 # Your Nexus user ID
    grounding_mode: Literal["strict"] = "strict"  # Always strict
    channel: str                  # "whatsapp", "telegram", "web"
    channel_config: dict          # Bot token, phone number, etc.
    kb_namespace: str             # Isolated KB partition
    system_prompt: str            # Business-specific prompt
    intents: dict                 # Business-specific intents
    tools_enabled: list[str]      # Subset of available tools
    active: bool
```

**Creating a sub-agent via Telegram:**

```
You: Create a customer service bot for my nail school

Nexus: I'll set up a business chatbot. Let me ask a few questions:

  1. What's the business name?
You: Beauty & Nailschool Bochum

  2. What channel should it run on?
  [Telegram] [WhatsApp] [Web Widget]
You: WhatsApp

  3. What should it handle?
  [FAQ / Pricing] [Appointments] [Complaints] [All of these]
You: All of these

  4. Can you share your price list and business info?
     (Send as text, file, or link – I'll build the KB)
You: [sends price list PDF]

Nexus: ✅ Sub-agent "Nailschool Bot" created!
  📋 KB: 24 entries from your price list
  💬 Channel: WhatsApp (needs phone number setup)
  🧠 Mode: Strict grounding (only answers from KB)

  Next steps:
  • /subagent nailschool connect – to link WhatsApp number
  • /subagent nailschool test – to test with sample questions
  • /subagent nailschool kb add – to add more knowledge
```

**Managing sub-agents:**

- `/subagents` – list all your bots
- `/subagent {name} status` – stats, costs, recent conversations
- `/subagent {name} kb add` – add knowledge
- `/subagent {name} pause/resume` – toggle active
- `/subagent {name} logs` – recent conversations + decision logs

## Architecture Rules

### 1. Three-Tier Model Routing

```
Tier 1 (70%): DeepSeek V3.2 / Gemini Flash  → cheapest
Tier 2 (25%): Claude Haiku / GPT-4.1 Mini   → balanced
Tier 3 (5%):  Claude Sonnet / GPT-5          → most capable
```

### 2. Routing Pipeline

1. Keyword Pre-Filter (free, <1ms)
1. Semantic Router (free, <10ms, embedding similarity)
1. LLM Classifier (only for ambiguous, ~$0.001)
1. Auto-Escalation (confidence <0.7 → next tier, max 1)

### 3. Three-Layer Memory

```
Layer 1: Last N Turns       → ~400 tokens (Redis)
Layer 2: Running Summary    → ~200 tokens (compressed every 3 msgs)
Layer 3: Semantic Recall    → ~300 tokens (pgvector – personal KB + conversation history)
Total budget: ~1,200 tokens HARD LIMIT
```

Plus: **Personal Facts Store** – long-term facts about the user:

- “User prefers German”, “User’s n8n instance is at http://localhost:5678”
- Extracted automatically from conversations, stored in Supabase
- Injected into system prompt when relevant

### 4. Heuristic Confidence

```python
confidence = 0.30*rag + 0.10*coverage + 0.20*tool_success + 0.25*validator + 0.15*citation
```

- In OPEN mode: validator weight set to 0, citation weight redistributed
- In STRICT mode (sub-agents): full formula, auto-low without citations

### 5. Plugin Security

- Tool Firewall: structured calls only, Pydantic validation, injection detection
- Permission Scopes: read/write per plugin
- Confirmation Gates: destructive actions require user confirmation
- Sandboxed: plugins can’t access each other’s data
- User text NEVER passed directly as tool argument

### 6. Dynamic Tool Loading

- Only load plugin schemas relevant to detected intent
- Core plugins always loaded (~400 tokens)
- Saves 60-80% tool tokens per request

### 7. Tool-Result Trimming

- Per-plugin limits (configurable)
- Global cap: 4,096 bytes across all tool results per loop

### 8. Sub-Agent Isolation

- Each sub-agent: own KB namespace, own system prompt, own intents
- Sub-agents run in STRICT grounding mode (always)
- Sub-agents share the LLM gateway but have separate cost tracking
- Sub-agent conversations are NOT visible to core Nexus (privacy)
- Sub-agents can’t call personal plugins (Gmail, Calendar, etc.)

### 9. PII Handling

- Personal data: encrypted at rest in Supabase
- Log redaction: synthetic replacement before Langfuse
- Sub-agent conversations: PII minimized (customer IDs, not names)

### 10. EU AI Act

- KI-Disclosure on all channels (configurable text)
- Sub-agents: mandatory disclosure in first message + channel bio

## Decision Logs (every request)

Fields: request_id, user_id, is_subagent, subagent_id, intent, router_confidence,
tier, risk_level, tools_called, tools_success, rag_top_score, cache_hit,
grounding_mode, validator_pass, citation_count, confidence_score,
agent_loops, total_tokens, cost_usd, latency_ms

## Onboarding Flow (Telegram-based, no config files)

First time `/start`:

```
Nexus: 👋 Hey! I'm Nexus, your personal AI agent.
       I can help you with emails, calendar, automations, and more.

       Let's set up in 2 minutes:

       1. Which LLM would you like to use?
       [OpenRouter Free] [Own OpenAI Key] [Own Anthropic Key] [Other]

User: OpenRouter Free

Nexus: 2. What should I call you?
User: Jerome

Nexus: 3. Which language do you prefer?
       [Deutsch] [English] [Both]
User: Both

Nexus: ✅ Setup complete, Jerome!

       I ship with these built-in capabilities:
       ✅ Reminders & To-Dos
       ✅ Web Search
       ✅ Personal Knowledge Base

       Want to connect more services?
       /connect gmail     – Read & send emails
       /connect calendar  – Manage your schedule
       /connect n8n       – Build automations
       /connect notion    – Notes & databases

       Or just start talking to me! Try:
       "Remind me to buy milk tomorrow at 9"
       "What's the latest news about AI?"
       "Create a sub-agent for my business"
```

## Cost Targets

- Self-hosted: only LLM API costs (OpenRouter free tier possible for light use)
- Normal personal use: ~5-15€/mo in API costs
- With sub-agents: +5-10€/mo per active sub-agent
- Daily LLM cap: configurable (default $2.00)

## Code Style

- Python 3.12+, async/await everywhere
- Type hints mandatory (Pydantic models)
- No hardcoded business logic – everything via config/plugins
- Tests: pytest + pytest-asyncio, mocks for external services
- Logging: structlog (JSON)

## Key Libraries

```
litellm, fastapi, uvicorn, aiogram>=3.0, sentence-transformers,
supabase-py, redis, langfuse, pydantic>=2.0, pydantic-settings,
apscheduler, semantic-router, faker, structlog, pyyaml, tiktoken,
httpx, pytest, pytest-asyncio
```

## Interfaces Between Modules

### UnifiedMessage (channels → agent)

```python
class UnifiedMessage(BaseModel):
    id: str
    channel: Literal["telegram", "whatsapp", "web"]
    sender_id: str
    text: str
    media: list[MediaAttachment] | None
    timestamp: datetime
    is_subagent_message: bool = False
    subagent_id: str | None = None
    metadata: dict = {}
```

### RoutingDecision (routing → agent)

```python
class RoutingDecision(BaseModel):
    intent: str
    tier: Literal[1, 2, 3]
    risk_level: Literal["low", "medium", "high", "critical"]
    confidence: float
    requires_confirmation: bool
    plugins_to_load: list[str]
    grounding_mode: GroundingMode
    source: Literal["keyword", "semantic_router", "llm_classifier"]
```

### AgentResponse (agent → channels)

```python
class AgentResponse(BaseModel):
    text: str
    citations: list[Citation] = []
    ui_component: UIComponent | None = None
    fallback_text: str
    confidence: float
    needs_confirmation: bool = False
    confirmation_payload: dict | None = None   # For inline keyboard actions
    decision_log: DecisionLog
```

### ContextBundle (memory → agent)

```python
class ContextBundle(BaseModel):
    last_turns: list[Turn]
    summary: str
    rag_snippets: list[Chunk]
    personal_facts: list[str]    # Long-term user facts
    total_tokens: int            # Must be ≤1,200
```