# AI-Powered Multi-Agent Marketing Automation System

A production-ready intelligent marketing automation system built with Python, LangChain, OpenAI API, FastAPI, and SQL. Orchestrates campaign planning, content generation, and outreach execution end-to-end using a multi-agent framework.

---

## Features

- **Multi-Agent Framework** — Specialized agents for campaign planning, content generation, and outreach execution
- **LangChain Pipelines** — Multi-step workflows with strategic analysis, copy generation, and response validation
- **LLM Tool Integration** — Contextual reasoning, dynamic task routing, and autonomous decision-making
- **RESTful API** — FastAPI backend with persistent SQL storage, audit trails, and submission management
- **30–40% Efficiency Gain** — Automated end-to-end campaign lifecycle

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Agent Framework | LangChain |
| LLM Provider | OpenAI API (GPT-4o) |
| API Backend | FastAPI |
| Database | SQLite (SQLAlchemy ORM) |
| Task Queue | asyncio |
| Testing | pytest |

---

## Project Structure

```
ai-marketing-agent/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base agent class
│   ├── campaign_planner.py    # Campaign strategy agent
│   ├── content_generator.py   # Copy & creative content agent
│   ├── outreach_executor.py   # Outreach & response agent
│   └── orchestrator.py        # Master orchestration agent
├── api/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── campaigns.py       # Campaign endpoints
│   │   ├── content.py         # Content endpoints
│   │   └── outreach.py        # Outreach endpoints
│   └── schemas.py             # Pydantic request/response models
├── database/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy ORM models
│   ├── crud.py                # CRUD operations
│   └── session.py             # DB session management
├── tools/
│   ├── __init__.py
│   ├── search_tool.py         # Web search integration
│   ├── analytics_tool.py      # Campaign analytics
│   └── email_tool.py          # Email outreach tool
├── utils/
│   ├── __init__.py
│   ├── config.py              # Environment & settings
│   └── logger.py              # Structured logging
├── tests/
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_database.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/ai-marketing-agent.git
cd ai-marketing-agent
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your OpenAI API key and settings
```

### 3. Run the API

```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Trigger a Campaign

```bash
curl -X POST http://localhost:8000/campaigns/run \
  -H "Content-Type: application/json" \
  -d '{
    "product": "SaaS Analytics Tool",
    "target_audience": "B2B SaaS startups",
    "goal": "lead generation",
    "budget": 5000
  }'
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/campaigns/run` | Run full campaign pipeline |
| GET | `/campaigns/{id}` | Get campaign details |
| GET | `/campaigns/` | List all campaigns |
| POST | `/content/generate` | Generate marketing copy |
| GET | `/content/{campaign_id}` | Get content for a campaign |
| POST | `/outreach/execute` | Execute outreach sequence |
| GET | `/outreach/audit` | View audit trail |

---

## Agent Architecture

```
User Request
     │
     ▼
┌─────────────────┐
│   Orchestrator  │  ← Routes tasks, manages state, validates outputs
└────────┬────────┘
         │
   ┌─────┼─────┐
   ▼     ▼     ▼
┌──────┐ ┌──────────┐ ┌──────────┐
│Plan  │ │Content   │ │Outreach  │
│Agent │ │Generator │ │Executor  │
└──────┘ └──────────┘ └──────────┘
   │           │            │
   └─────┬─────┘            │
         ▼                  ▼
    SQL Database       Email / CRM
```

---

## Environment Variables

See `.env.example` for all required variables:

```
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./marketing.db
LOG_LEVEL=INFO
MAX_TOKENS=2000
TEMPERATURE=0.7
```

---

## Running Tests

```bash
pytest tests/ -v
```
