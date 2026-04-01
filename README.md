# Autonomous Customer Support Agent

> **Salesforce Agentforce + Apex + Python FastAPI**
> Portfolio project built to demonstrate Forward Deployed Engineer (FDE) capabilities.

---

## What This Project Does

This project implements a fully autonomous customer support agent that **understands intent, makes decisions, executes multi-step actions, updates systems, and responds** — all without human intervention.

### Example Flow

**User asks:** _"Where is my order and can you escalate if delayed?"_

| Step | What Happens | Technology |
|------|-------------|------------|
| 1 | Understand intent | Agentforce AI |
| 2 | Call external API to fetch order | Apex HTTP Callout |
| 3 | Fetch order status + delay info | Python FastAPI |
| 4 | Evaluate business rule: delay > 3 days? | Apex Business Logic |
| 5 | Create escalation ticket externally | Apex → FastAPI POST |
| 6 | Create Salesforce Case with priority | Apex → Service Cloud |
| 7 | Log the agent's decision trace | AgentActionLogger |
| 8 | Respond with full action summary | Agentforce Response |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SALESFORCE ORG                       │
│                                                         │
│  ┌─────────────┐    ┌──────────────────────────────┐   │
│  │  Agentforce │───>│   OrderServiceCallout.cls    │   │
│  │  AI Agent   │    │   (Invocable Method)          │   │
│  └─────────────┘    └──────────────┬───────────────┘   │
│                                    │ HTTP Callout        │
│  ┌─────────────┐    ┌──────────────▼───────────────┐   │
│  │ Service     │<───│   EscalationHandler.cls      │   │
│  │ Cloud Cases │    │   (Case Creation + Priority)  │   │
│  └─────────────┘    └──────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │            AgentActionLogger.cls                 │  │
│  │         (Full decision trace log)                │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │ REST API (Apex Callout)
                            │
┌───────────────────────────▼─────────────────────────────┐
│               PYTHON FASTAPI BACKEND                     │
│                                                          │
│  GET  /orders/{order_id}   → Fetch order + delay info    │
│  POST /escalate            → Register escalation ticket  │
│  GET  /customers/{id}      → Fetch customer context      │
│  GET  /health              → Health check                │
└──────────────────────────────────────────────────────────┘
```

---

## Key Features

### Multi-Step Decision Making
Not just one response — the agent runs a full pipeline of actions:
1. Fetch order data
2. Evaluate delay threshold
3. Conditionally escalate
4. Create Salesforce Case
5. Respond with context

### External System Integration (Apex Callouts)
Apex classes make real HTTP REST API calls to the Python FastAPI backend. This mirrors real-world enterprise integrations that FDE engineers build.

### Business Logic Engine
```
delay > 7 days  → Priority: Critical
delay > 3 days  → Priority: High (auto-escalate)
delay <= 3 days → No escalation, inform customer
```

### System Updates
- Creates Salesforce **Cases** in Service Cloud
- Sets **Priority** dynamically based on delay severity
- Registers escalation in external system
- Logs full **agent decision trace** per action

### Agent Observability (Logging)
Every decision the agent makes is logged to `Agent_Log__c` custom object with:
- Action type (ORDER_FETCH, ESCALATION_CREATED, ERROR)
- Timestamp
- Full decision details

---

## Project Structure

```
salesforce-autonomous-support-agent/
│
├── apex/
│   ├── OrderServiceCallout.cls      # Main invocable — Agentforce entry point
│   ├── EscalationHandler.cls        # Creates Cases + calls escalation API
│   ├── AgentResponseBuilder.cls     # Builds natural language responses
│   └── AgentActionLogger.cls        # Logs agent decisions for observability
│
├── backend/
│   ├── main.py                      # FastAPI app with all endpoints
│   └── requirements.txt             # Python dependencies
│
└── README.md
```

---

## Setup Guide

### 1. Run the Python Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Expose it publicly using ngrok:
```bash
ngrok http 8000
# Copy the https:// URL
```

### 2. Configure Salesforce

1. Sign up for a free [Salesforce Developer Org](https://developer.salesforce.com/signup)
2. In **Setup > Remote Site Settings**, add your ngrok URL
3. Deploy all Apex classes in the `/apex` folder via Developer Console or VS Code SFDX
4. Create the `Agent_Log__c` custom object with fields:
   - `Order_Id__c` (Text 50)
   - `Action_Type__c` (Text 50)
   - `Details__c` (Long Text Area)
   - `Timestamp__c` (DateTime)
5. Update `BASE_URL` in `OrderServiceCallout.cls` and `EscalationHandler.cls` with your ngrok URL

### 3. Configure Agentforce

1. Go to **Setup > Agentforce Agents** → Create New Agent
2. Set **Agent Type**: Service Agent
3. Add **Topics**: Order Management, Escalation Handling
4. Add **Actions** (Invocable Methods):
   - `Get Order Status and Decide Action` (from `OrderServiceCallout`)
   - `Create Escalation and Case` (from `EscalationHandler`)
5. Write **Agent Instructions**:
   ```
   When a customer asks about an order, call GetOrderStatus action first.
   If the order is delayed and requiresEscalation is true, 
   automatically call CreateEscalationAndCase action.
   Always respond with the agentResponse field from the action output.
   ```

---

## API Reference

### GET /orders/{order_id}
Fetch order details.

**Sample Response:**
```json
{
  "order_id": "ORD-1001",
  "status": "delayed",
  "delay_days": 5,
  "customer_name": "Rahul Sharma",
  "expected_delivery": "2026-03-28"
}
```

### POST /escalate
Create an escalation ticket.

**Request:**
```json
{
  "order_id": "ORD-1001",
  "reason": "Order delayed by 5 days. Auto-escalated by Agentforce agent.",
  "priority": "High",
  "raised_by": "Agentforce"
}
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| AI Agent | Salesforce Agentforce |
| Backend Logic | Apex (Salesforce) |
| CRM / Cases | Service Cloud |
| External API | Python FastAPI |
| Integration | Apex HTTP Callouts (REST) |
| Logging | Custom Salesforce Object |

---

## Built For

This project was built as a portfolio piece targeting the **Salesforce Forward Deployed Engineer (FDE) Associate** role, demonstrating:

- Real Agentforce implementation with invocable methods
- Apex callout patterns for enterprise integrations  
- Service Cloud automation (Case creation, priority logic)
- Python/FastAPI backend integration
- Agentic observability and decision logging
- Multi-step autonomous action execution

---

## Streamlit Frontend (Live Demo)

A Python Streamlit app that visually demonstrates the full autonomous agent flow — connecting directly to the FastAPI backend.

### Pages

| Page | Description |
|------|-------------|
| 🤖 Agent Simulator | Main page — type a query, watch the agent execute step-by-step |
| 📦 Order Lookup | View all orders in a dashboard, inspect individual order details |
| 🚨 Escalation Simulator | Manually trigger escalations, see simulated Salesforce Case creation |
| 🔍 Agent Trace Log | Decision audit log with timeline view — mirrors `AgentActionLogger.cls` |

### Run Locally

```bash
# Step 1: Start the FastAPI backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Step 2: In a new terminal, run Streamlit
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

### Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub (already done)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New App**
4. Set:
   - **Repository:** `revanth112/salesforce-autonomous-support-agent`
   - **Branch:** `main`
   - **Main file path:** `streamlit/app.py`
5. Click **Deploy**

> Note: For the Streamlit Cloud deployment, update the Backend URL in the sidebar to point to your deployed FastAPI URL (e.g., Railway, Render, or ngrok).

---

*Built by Sunku Venkata Revanth Kumar*


*Built by Sunku Venkata Revanth Kumar*
