# Project Nexus

Multi-tenant AI-Agent Framework für den produktiven Einsatz bei KMU.

## Setup

1. Python 3.12+ installieren.
2. Environment anlegen:
   ```bash
   cp .env.example .env
   ```
3. Dependencies installieren:
   ```bash
   pip install -e .[dev]
   ```
4. Services starten:
   ```bash
   docker compose up
   ```

## Projektstruktur

- `src/`: Agent-Framework Module (Agent, Routing, Memory, Tools, Channels, Tenant, DB).
- `configs/defaults/`: Tenant-agnostische Defaults.
- `configs/tenants/example_tenant/`: Beispielkonfiguration für einen Mandanten.
- `tests/`: Unit- und Evaluations-Tests.

## Umsetzungsstand (grob)

- Session 0 (Scaffold): **100%**
- Session 1 (Tenant Foundation): **~55%** (Config-Loading + Vererbung + TenantContext umgesetzt)
- Session 2 (Routing Core: keyword + semantic + confidence + fallback): **~45%**
- Session 3 (Memory Core: working + summary + semantic + context budget): **~35%**
- Session 4 (Grounding Core: citations + validator + repair + entity registry): **~30%**
- Session 5 (Tools Core: registry + trimming + firewall + permissions): **~30%**
- Session 6+ (Channels, Observability, Evals): **~5%**

Gesamtfortschritt über Sessions 0–8: **ca. 52%**.

## Wie lege ich einen neuen Tenant an?

1. Verzeichnis `configs/tenants/<tenant_id>/` erstellen.
2. Dateien aus `configs/tenants/example_tenant/` als Vorlage kopieren:
   - `tenant.yaml`
   - `intents.yaml`
   - `tools.yaml`
   - `channels.yaml`
   - `prompt_template.yaml`
   - optional `kb_seed.yaml`
3. Werte anpassen (`business_name`, Sprache, erlaubte Channels, Tool-Policies).
4. Tenant über zukünftiges CLI `scripts/onboard_tenant.py` registrieren.
5. Tests ausführen:
   ```bash
   python -m pytest tests/test_tenant.py tests/test_routing.py tests/test_agent.py -v
   ```
