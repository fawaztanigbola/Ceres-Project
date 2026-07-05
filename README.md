# Ceres — Autonomous Harvest Rescue & Micro-Logistics Agent

**Track:** Agents for Good — Kaggle AI Agents Intensive Capstone

Ceres is a three-agent pipeline that lets a smallholder farmer text a single emergency SMS/WhatsApp message ("flood coming, I need to sell my 500kg of tomatoes now") and have it autonomously negotiated, priced, insured against logistics failure, and settled into escrow — with the farmer's final "YES" as the only required human action.

## The problem

Smallholder farmers routinely lose a large share of their harvest when a climate shock (flash flood, storm) hits before they can find a buyer, a fair price, and transport. Existing apps only warn about the danger; they don't act on it, and they assume a level of digital literacy and time that a farmer mid-crisis doesn't have.

## The solution

Ceres runs as a linear agent graph — `Liaison -> Logistics -> Security` — orchestrated with Google's Agent Development Kit (ADK):

```
Farmer SMS
    |
    v
Liaison Agent      parses free text into {crop, weight, region}; strips phone
                    numbers / addresses before anything moves downstream
    |
    v
Logistics Agent     calls MCP tools for weather, market price, and vetted
                     buyers; enforces floor_price = market_price * 0.85;
                     books freight, or fails over to warehouse storage if
                     no trucks are available; creates the escrow contract
    |
    v
Security Agent      re-checks for PII and validates price > 0; sends the
                     farmer a plain-language SMS and waits for a "YES"
                     before the transaction is considered final
```

## Architecture

| Component | File | Role |
|---|---|---|
| Agent graph | `app/agent.py` | Defines `Liaison_Agent`, `Logistics_Agent`, `Security_Agent` and wires them into a `Workflow` |
| MCP tool server | `app/mcp_server.py` | `FastMCP` server exposing 6 deterministic tools (weather, pricing, buyers, freight, warehouse, escrow) over stdio |
| App entrypoint | `app/__init__.py` | Re-exports the ADK `app` object |
| Deployment layer | `app/fast_api_app.py` | Wraps the agent graph in a FastAPI service with A2A protocol routes, telemetry, and a `/feedback` endpoint |

Every number in a transaction (price, floor, bid, freight status) comes from a real MCP tool call with a structured JSON return — not from the model guessing — which removes an entire class of hallucinated-price failure modes.

### Key course concepts demonstrated
- **Multi-agent system (ADK):** three distinct agents, each with a narrow responsibility, connected via an explicit `Workflow` graph (code: `app/agent.py`).
- **MCP server:** a custom `FastMCP` server exposing six tools over stdio, spawned as a subprocess by the Logistics Agent (code: `app/mcp_server.py`).
- **Security features:** a PII guardrail enforced twice (intake and pre-payment), a floor-price rule that blocks lowball trades, and a human-approval gate via `LongRunningFunctionTool` before any escrow is finalized (code: `app/agent.py`).

## Live demo

`ceres_demo.html` is a standalone, dependency-free interactive page that traces the full pipeline against three scenarios:

1. **Small harvest — clears fully:** a normal trade end to end.
2. **Oversized load — freight fails over:** triggers the `book_freight` error path and the automatic reroute to `find_warehouse_storage`.
3. **Lowball bids — trade blocked:** every buyer bid falls below the floor price, and Ceres halts the trade instead of accepting a bad deal.

Open it directly in a browser, or deploy it as-is (no build step) to Vercel, Netlify, or GitHub Pages.

## Setup

```bash
git clone <this_repo_url>
cd ceres-project

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # google-adk, mcp, fastapi, google-cloud-logging, etc.

cp .env.example .env                   # add GOOGLE_API_KEY=your_key_here
```

**Run the agent graph in ADK's dev console (fastest way to inspect reasoning):**
```bash
adk web app
```

**Or run the production FastAPI + Agent-to-Agent (A2A) service:**
```bash
uvicorn app.fast_api_app:app --reload --port 8000
```

The MCP server does not need a separate start step — `Logistics_Agent` spawns `mcp_server.py` automatically as a subprocess using the same Python interpreter (`sys.executable`) running the agent, so there is no version mismatch between caller and tool server.

**No API keys or secrets are committed to this repository.** Set `GOOGLE_API_KEY` locally via `.env` (excluded via `.gitignore`) or your deployment platform's secret manager.

## Repository structure

```
ceres-project/
├── .agents/skills
    ├── SKILL.md
├── app/
    ├── app_utils/
│   ├── __init__.py        # exports `app` for ADK
│   ├── agent.py           # Liaison / Logistics / Security agents + Workflow
│   ├── mcp_server.py       # FastMCP tool server (weather, price, buyers, freight, warehouse, escrow)
│   └── fast_api_app.py     # FastAPI + A2A deployment wrapper
├── ceres_demo.html         # standalone interactive live demo
├── GEMINI.md
├── agents-cli-manifest.yaml
├── pyproject.toml
└── README.md
```

## Roadmap

Replace the mocked data sources in `mcp_server.py` with real satellite weather and commodity-exchange APIs, add persistent session storage so a farmer's negotiation history informs future floor-price decisions, and extend the A2A interface so cooperative-level dashboards can query Ceres for fleet-wide harvest-risk visibility.
