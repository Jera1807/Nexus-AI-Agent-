Project Nexus – CLAUDE.md
This file is the single source of truth for Claude Code sessions. Read this FIRST
before writing any code.
What is Nexus?
A universal, multi-tenant AI agent framework for deploying autonomous chatbots
across any business. Not a single-purpose bot – a platform that can be configured for
any client via tenant-specific configs (KB, prompts, tools, intents).
First deployment: Beauty & Nailschool Bochum (nail design school) Built by: AI &
Automation Ruhr (Jerome’s consulting business) Business model: Deploy Nexus
instances for SME clients as productized service
Design Principles
1. Tenant-agnostic core – All business logic is configurable, not hardcoded
2. Config-driven – New client = new tenant config, not new code
3. Cost-optimized – 3-tier model routing, caching, dynamic tool loading
4. Production-grade – Grounding validation, tool firewall, decision logs, CI/CD evals
5. Multi-channel – Same agent logic across WhatsApp, Telegram, Web, Email
Tech Stack
Component Choice Why
Language Python 3.12+ (async) Performance + ecosystem
Agent Loop Custom ReAct (NO LangGraph) Simpler debugging, fewer deps
LLM
Gateway LiteLLM Proxy Unified API for all providers
Database Supabase (Postgres + pgvector) Free tier, managed, RLS for
multi-tenant
Cache Upstash Redis (free tier) Session state, response cache
Embedding paraphrase-multilingual-MiniLM-
L12-v2 (local) Multilingual, 0 cost
Observability Langfuse Cloud (free tier) 50k observations/mo
Tools MCP Protocol Industry standard
WhatsApp Baileys (Node.js bridge) Free, no Meta Business API
needed
Telegram aiogram 3.x Async, inline keyboards
Hosting Hetzner CX11 (2 vCPU, 4GB RAM) 3.29€/mo, GDPR DE
Project Structure
project-nexus/
├── CLAUDE.md # THIS FILE
├── README.md
├── pyproject.toml ├── docker-compose.yml # uv/pip, Python 3.12+
# Agent + LiteLLM + Redis
├── .env.example
├── .github/
│ └── workflows/
│ └── eval.yml # Golden Questions CI
│
├── src/
│ ├── __init__.py
│ ├── main.py │ ├── config.py # Entrypoint: FastAPI app
# Pydantic Settings (.env)
│ │
│ ├── agent/
│ │ ├── __init__.py
│ │ ├── loop.py # ReAct agent loop (async)
│ │ ├── prompt.py # System prompt builder (dynamic, tenant-aware)
│ │ └── structured.py # Pydantic output schemas
│ │
│ ├── routing/
│ │ ├── __init__.py
│ │ ├── keyword.py # Step 1: Keyword pre-filter
│ │ ├── semantic.py # Step 2: Semantic Router (embedding)
│ │ ├── llm_classifier.py # Step 3: LLM fallback classifier
│ │ ├── confidence.py # Heuristic confidence calculation
│ │ └── models.py # RoutingDecision, Tier, RiskLevel
│ │
│ ├── memory/
│ │ ├── __init__.py
│ │ ├── working.py # Last N turns (Redis)
│ │ ├── summary.py # Running summary (compressed)
│ │ ├── semantic.py # RAG snippets (pgvector)
│ │ └── context.py # Context assembler (budget enforcement)
│ │
│ ├── grounding/
│ │ ├── __init__.py
│ │ ├── validator.py # Deterministic grounding validator
│ │ ├── citations.py # Machine-readable citation engine
│ │ ├── entity_registry.py # Auto-synced entity/policy lists (per tenant)
│ │ └── repair.py # 1-step repair logic
│ │
│ ├── tools/
│ │ ├── __init__.py
│ │ ├── registry.py # Tool registry + dynamic loading (per tenant)
│ │ ├── trimming.py # Result trimming (per-tool + global cap)
│ │ ├── firewall.py # Structured calls only, param validation
│ │ ├── permissions.py # Scopes, channel allowlists, confirmations
│ │ └── servers/ # MCP server implementations
│ │ ├── knowledge_base.py
│ │ ├── calendar.py
│ │ ├── customer.py
│ │ └──
...
│ │
│ ├── channels/
│ │ ├── web.py │ │
│ │ ├── pii.py │ │
│ ├── proactive/
│ │ ├── __init__.py
│ │ ├── base.py # Abstract channel interface
│ │ ├── telegram.py # aiogram 3.x bot
│ │ ├── whatsapp.py # Baileys bridge client
# FastAPI WebSocket
│ │ └── message.py # Unified message format
│ ├── observability/
│ │ ├── __init__.py
│ │ ├── langfuse.py # Langfuse client + decision logs
# PII redaction (synthetic replacement)
│ │ └── alerts.py # Telegram alert webhooks
│ │ ├── __init__.py
│ │ ├── scheduler.py # Cron job scheduler
│ │ ├── jobs.py # Configurable background jobs (per tenant)
│ │ └── consent.py # Opt-in/out, segmentation, frequency caps
│ │
│ ├── tenant/
│ │ ├── __init__.py
│ │ ├── manager.py # Tenant resolution + config loading
│ │ ├── models.py # Tenant, TenantMembership, TenantConfig
│ │ └── onboarding.py # Provision new tenant (DB, KB, intents, prompt)
│ │
│ └── db/
│ ├── __init__.py
│ ├── supabase.py # Supabase client
│ ├── models.py # SQLAlchemy/Pydantic DB models
│ └── migrations/ # SQL migration files
│
├── tests/
│ ├── conftest.py
│ ├── golden_questions/
│ │ ├── questions.yaml # Template test cases (tenant-agnostic)
│ │ └── runner.py # Eval runner
│ ├── test_routing.py
│ ├── test_memory.py
│ ├── test_grounding.py
│ ├── test_tools.py
│ └── test_agent.py
│
├── configs/
│ ├── litellm_config.yaml # 3-tier model config
│ ├── defaults/ # Default configs (overridable per tenant)
│ │ ├── intents.yaml # Base intent clusters (generic)
│ │ ├── tools.yaml # Tool permissions + trimming defaults
│ │ ├── channels.yaml # Channel config
│ │ └── prompt_template.yaml # Base system prompt template
│ └── tenants/ # Per-tenant overrides
│ └── example_tenant/
│ ├── tenant.yaml # Business name, language, tone, domain
│ ├── intents.yaml # Tenant-specific intents + example utterances
│ ├── tools.yaml # Which tools enabled, custom permissions
│ ├── risk_mapping.yaml # Which intents are high-risk for this business
│ └── kb_seed.yaml # Initial knowledge base content
│
└── scripts/
├── seed_kb.py ├── run_evals.py ├── calibrate.py └── onboard_tenant.py # Populate KB (from tenant config)
# Run golden questions
# Weekly confidence calibration
# CLI: create new tenant from template
Architecture Rules (NON-NEGOTIABLE)
1. Tenant Isolation
Every request carries a tenant_id
All DB queries scoped via RLS ( tenant_memberships table)
RLS Policy: EXISTS(SELECT 1 FROM tenant_memberships tm WHERE tm.user_id =
auth.uid() AND tm.tenant_id = table.tenant_id)
Cache keys prefixed: tenant:{id}:...
Separate Langfuse project per tenant (Phase 2+)
System prompt assembled from: base template + tenant-specific variables
Intent clusters loaded per tenant
Tool permissions configurable per tenant
2. Three-Tier Model Routing
Tier 1 (70%): DeepSeek V3.2 / Gemini Flash → $0.14-0.30/1M tokens
Tier 2 (25%): Claude Haiku / GPT-4.1 Mini → $0.80-2.00/1M tokens
Tier 3 (5%): Claude Sonnet / GPT-5 → $3-10/1M tokens
3. Routing Pipeline (4 Steps)
1. 2. 3. 4. Keyword Pre-Filter (free, <1ms): configurable keyword→tier mapping per tenant
Semantic Router (free, <10ms): Embedding similarity vs tenant-specific intent
clusters. Confidence ≥ threshold → direct route
LLM Classifier ($0.001, ~500ms): Only for ambiguous queries (15-25%)
Auto-Escalation: If confidence <0.7 after response → next tier. Max 1, then human.
4. Two-Dimensional Routing: Complexity × Risk
Risk mapping is configurable per tenant – which intents are “high risk” depends on
the business.
5. Heuristic Confidence Formula
confidence = (
0.30 * rag_similarity_score +
0.10 * rag_coverage +
0.20 * tool_success_rate +
0.25 * validator_pass + 0.15 * citation_coverage
# binary: 1.0 or 0.0
)
Weights calibratable per tenant (weekly calibration loop). AUTO-LOW: Hard-facts
without citations → confidence = 0.3
6. Three-Layer Memory (MANDATORY)
Layer 1: Last N Turns (raw) → ~400 tokens
Layer 2: Running Summary → ~200 tokens
Layer 3: RAG Snippets (relevant) → ~300 tokens (tenant-scoped)
Total budget: ~1,200 tokens HARD LIMIT
7. Grounding: Hard Facts vs Soft Content
Hard Facts: ONLY from KB/Tools. MUST have citation-ID.
Soft Content: LLM may formulate freely. No new facts.
Validator: deterministic (Regex + Entity-List → citation check → 1 repair → fail-fast)
Entity registry auto-synced from tenant’s KB
8. Machine-Readable Citations
{
"answer": "...",
"citations": [{"id": "KB-{CAT}-{NUM}", "fact": "...", "source": "..."}]
}
9. Dynamic Tool Loading
Only load tool schemas for detected intent (saves 60-80% tokens)
Intent-to-tool mapping configurable per tenant
Core tools always loaded: human_escalation, kb_search
10. Tool-Result Trimming
Per-tool limits configurable: max_bytes, top_n, field_
whitelist
Global cap: 4,096 bytes across ALL tool results per agent loop
11. Tool Firewall
User text NEVER as tool argument directly
Structured calls only (Pydantic validation)
No tool invention (whitelist only)
Injection pattern detection
12. Tool Permissions (3 Layers, per tenant)
Scopes (read/write), Channel Allowlists, Confirmation Gates
13. PII Handling
Minimize before LLM, secure store (Supabase RLS), synthetic log redaction (Faker)
14. EU AI Act: KI-Disclosure from Day 1 (configurable per
tenant/channel)
15. Proactive Jobs: per tenant, configurable, Auto-Send default OFF
16. Decision Logs: 18 fields per request (including tenant_id)
System Prompt Template
Assembled dynamically per request:
[BASE TEMPLATE] (role definition, grounding rules, citation format, escalation rules)
+
+
+
[TENANT VARIABLES] (business name, tone, language, domain instructions)
[LOADED TOOL SCHEMAS] (only relevant tools for this intent)
[CONTEXT] (memory: last turns + summary + RAG snippets)
Example tenant config ( configs/tenants/{id}/tenant.yaml ):
business_name: "Example Business"
business_type: "retail store"
language: "de"
tone: "friendly, professional"
domain_instructions: |
You are the AI assistant for this business.
Adapt this section for each client.
escalation_contact: "Owner via Telegram"
ki_disclosure: " Ich bin ein KI-Assistent von {business_name}."
Cost Targets (per tenant, configurable)
Monthly default: 13-23€ normal, max 35-45€ worst case
Daily LLM cap: configurable (default $2.00)
Per resolved conversation: <0.05€
Code Style
Python 3.12+, async/await everywhere
Type hints mandatory (Pydantic models for all data)
CRITICAL: No business-specific logic hardcoded. Everything via
config/tenant.
Tests: pytest + pytest-asyncio, mocks for external services
Logging: structlog (JSON)
Key Libraries
litellm, fastapi, uvicorn, aiogram>=3.0, sentence-transformers,
supabase-py, redis, langfuse, pydantic>=2.0, pydantic-settings,
apscheduler, semantic-router, faker, structlog, pyyaml, tiktoken,
pytest, pytest-asyncio
Interfaces Between Modules
TenantContext (tenant → everything)
class TenantContext(BaseModel):
tenant_id: str
config: TenantConfig # From configs/tenants/{id}/
prompt_variables: dict # Business name, tone, domain instructions
active_tools: list[str] # Which tools this tenant has enabled
intent_clusters: dict # Tenant-specific intents
risk_mapping: dict[str, str] # intent → risk level override
RoutingDecision (routing → agent)
class RoutingDecision(BaseModel):
intent: str
tier: Literal[1, 2, 3]
risk_level: Literal["low", "medium", "high", "critical"]
confidence: float
requires_confirmation: bool
tools_to_load: list[str]
source: Literal["keyword", "semantic_router", "llm_classifier"]
UnifiedMessage (channels → agent)
class UnifiedMessage(BaseModel):
id: str
channel: Literal["whatsapp", "telegram", "web", "email"]
sender_id: str
tenant_id: str
text: str
media: list[MediaAttachment] | None
timestamp: datetime
metadata: dict
AgentResponse (agent → channels)
class AgentResponse(BaseModel):
text: str
citations: list[Citation]
ui_component: UIComponent | None
fallback_text: str
confidence: float
decision_log: DecisionLog
ContextBundle (memory → agent)
class ContextBundle(BaseModel):
last_turns: list[Turn]
summary: str
rag_snippets: list[Chunk]
total_tokens: int # Must be ≤1,200
GroundingResult (grounding → agent)
class GroundingResult(BaseModel):
passed: bool
citations: list[Citation]
hard_facts_found: int
hard_facts_cited: int
needs_repair: bool
repaired_text: str | Non