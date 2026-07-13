# Ceres — Autonomous Harvest Rescue & Micro-Logistics Agent

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![Package Manager](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Framework](https://img.shields.io/badge/framework-Google%20ADK-green.svg)](https://github.com/google/generative-ai-docs)
[![Protocol](https://img.shields.io/badge/protocol-MCP-orange.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)

**Track:** Agents for Good — Kaggle AI Agents Intensive Capstone

Ceres is an autonomous, three-agent pipeline designed to rescue smallholder farmers' harvests during climate emergencies. By sending a single SMS or WhatsApp message (e.g., *"flood coming, I need to sell my 500kg of tomatoes now"*), a farmer triggers an automated workflow that negotiates pricing, secures logistics, insures against transport failure, and sets up an escrow contract—requiring only a final "YES" from the farmer to execute.

---

## The Problem

Smallholder farmers routinely lose a massive share of their harvest when climate shocks (flash floods, sudden storms) hit before they can find a buyer, negotiate a fair price, and secure transport. Existing applications only provide warnings; they do not act. Furthermore, they assume a level of digital literacy and time that a farmer in the middle of a crisis simply does not have.

## The Solution

Ceres runs as a linear agent graph—`Liaison -> Logistics -> Security`—orchestrated with Google's **Agent Development Kit (ADK)** and powered by Gemini.

```
                  [ Farmer SMS / WhatsApp ]
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                      Liaison Agent                       │
│  - Parses free text into structured JSON data            │
│  - Redacts PII (phone numbers, exact addresses)          │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                     Logistics Agent                      │
│  - Calls MCP tools for weather, market price, & buyers   │
│  - Enforces floor price: floor_price = market_price * 0.85│
│  - Books freight; fails over to warehouse if unavailable │
│  - Generates the escrow contract draft                  │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                      Security Agent                      │
│  - Re-checks for PII leaks & validates price > 0         │
│  - Formulates a plain-language SMS summary               │
│  - Awaits human-in-the-loop "YES" approval to finalize   │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
                 [ Escrow & Freight Settled ]
```

Every critical transaction metric (price, floor, bid, freight status) is derived from deterministic **Model Context Protocol (MCP)** tool calls with structured JSON returns—not from LLM hallucinations.

---

## Tech Stack

| Category | Technology | Description |
|---|---|---|
| **Agent Orchestration** | [Google ADK](https://github.com/google/generative-ai-docs) | Multi-agent workflow graph execution and management |
| **LLM Engine** | Google Gemini | Advanced reasoning, parsing, and decision-making |
| **Tooling Protocol** | [Model Context Protocol (MCP)](https://modelcontextprotocol.io) | FastMCP server hosting deterministic tools over stdio |
| **Deployment Layer** | FastAPI & A2A SDK | High-performance web framework with Agent-to-Agent protocol support |
| **Package Management** | [uv](https://github.com/astral-sh/uv) | Ultra-fast Python package installer and resolver |
| **Type Checking & Linting** | Ty & Ruff | Modern Rust-based static analysis and formatting |
| **Telemetry** | OpenTelemetry | Instrumentation for Google GenAI and logging |

---

## Repository Structure

```
📁 app/
  📁 app_utils/
    📄 a2a.py                  # Agent-to-Agent protocol utilities
    📄 services.py             # External service integrations
    📄 telemetry.py            # OpenTelemetry & Cloud Logging setup
    📄 typing.py               # Shared Type definitions
  📄 __init__.py               # Exports ADK app instance
  📄 agent.py                  # Liaison, Logistics, and Security agents + Workflow
  📄 fast_api_app.py           # FastAPI wrapper & A2A endpoints
  📄 mcp_server.py             # FastMCP tool server (weather, pricing, buyers, freight, etc.)
📁 tests/
  📁 eval/                     # Evaluation datasets and configurations
    📁 datasets/
    📄 eval_config.yaml
  📁 integration/              # End-to-end and agent integration tests
    📄 test_agent.py
    📄 test_server_e2e.py
  📁 unit/                     # Unit tests
    📄 test_dummy.py
📄 agents-cli-manifest.yaml    # ADK CLI configuration
📄 ceres_demo.html             # Standalone interactive frontend demo
📄 Dockerfile                  # Containerization configuration
📄 GEMINI.md                   # Gemini-specific configuration notes
📄 pyproject.toml              # Project dependencies and tool configurations
📄 uv.lock                     # Locked dependency tree
```

---

## Getting Started & Installation

### Prerequisites

- **Python**: `3.11` up to `3.13`
- **uv** (Recommended): Install via `curl -LsSf https://astral.sh/uv/install.sh` or `brew install uv`
- **Google Gemini API Key**: Required for agent execution

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fawaztanigbola/Ceres-Project.git
   cd Ceres-Project
   ```

2. **Create a virtual environment and install dependencies:**
   Using `uv` (highly recommended for speed and reliability):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync --all-extras
   ```

   *Alternatively, using standard pip:*
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install .[eval,lint]
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env  # If .env.example exists, otherwise create a new one
   ```
   Add your API keys:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

---

## Usage & Quick Start

### 1. Run the Agent Graph in ADK's Dev Console
The fastest way to inspect the reasoning, tool calls, and transitions of the three agents:
```bash
adk web app
```

### 2. Run the Production FastAPI + A2A Service
To launch the production-ready FastAPI server with Agent-to-Agent (A2A) protocol routes and telemetry:
```bash
uvicorn app.fast_api_app:app --reload --port 8000
```

> **Note on MCP Server Execution:** You do not need to start the MCP server separately. The `Logistics_Agent` automatically spawns `app/mcp_server.py` as a subprocess using the active Python interpreter (`sys.executable`), preventing version mismatches.

### 3. Running Tests & Evaluations

- **Run Unit & Integration Tests:**
  ```bash
  pytest tests/unit tests/integration
  ```

- **Run Evaluation Pipeline:**
  ```bash
  pytest tests/eval
  ```

---

## Key Course Concepts Demonstrated

*   **Multi-Agent System (ADK):** Three distinct agents, each with a narrow, specialized responsibility, connected via an explicit `Workflow` graph (`app/agent.py`).
*   **Model Context Protocol (MCP):** A custom `FastMCP` server exposing six deterministic tools over stdio, spawned dynamically as a subprocess by the Logistics Agent (`app/mcp_server.py`).
*   **Security & Guardrails:**
    *   **PII Redaction:** Enforced twice (at intake by Liaison and pre-payment by Security).
    *   **Floor-Price Rule:** Automatically blocks lowball trades if buyer bids fall below `market_price * 0.85`.
    *   **Human-in-the-Loop:** A human-approval gate via `LongRunningFunctionTool` blocks final escrow settlement until a plain-language "YES" is received.

---

## Standalone Interactive Demo

The repository includes `ceres_demo.html`, a standalone, dependency-free interactive page that traces the full pipeline against three distinct scenarios:

1.  **Small Harvest (Clears Fully):** A normal trade executed end-to-end.
2.  **Oversized Load (Freight Fails over):** Triggers the `book_freight` error path and automatically reroutes to `find_warehouse_storage`.
3.  **Lowball Bids (Trade Blocked):** Every buyer bid falls below the floor price, causing Ceres to halt the trade instead of accepting a bad deal.

To view the demo, open `ceres_demo.html` directly in any modern web browser, or deploy it directly to Vercel, Netlify, or GitHub Pages.

---

## Roadmap

*   **Real-world Integrations:** Replace mocked data sources in `mcp_server.py` with real satellite weather APIs and live commodity-exchange feeds.
*   **Persistent Session Storage:** Implement historical session tracking so a farmer's negotiation history can inform future floor-price decisions.
*   **Cooperative Dashboards:** Extend the A2A interface to allow agricultural cooperative dashboards to query Ceres for fleet-wide harvest-risk visibility.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (or is available as open-source software under standard terms).