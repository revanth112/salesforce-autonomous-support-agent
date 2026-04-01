from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Order Management API",
    description="Mock backend for Salesforce Autonomous Support Agent",
    version="1.0.0"
)

# Allow Salesforce Apex callouts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Mock Data ───────────────────────────────────────────────────────────────

ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "customer_name": "Rahul Sharma",
        "customer_email": "rahul.sharma@example.com",
        "product": "Salesforce Enterprise License",
        "status": "delayed",
        "expected_delivery": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "actual_delivery": None,
        "delay_days": 5,
        "shipping_partner": "BlueDart",
        "tracking_number": "BD9876543210"
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_id": "CUST-002",
        "customer_name": "Priya Nair",
        "customer_email": "priya.nair@example.com",
        "product": "Service Cloud Add-On",
        "status": "in_transit",
        "expected_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "actual_delivery": None,
        "delay_days": 0,
        "shipping_partner": "FedEx",
        "tracking_number": "FX1234567890"
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_id": "CUST-003",
        "customer_name": "Arjun Mehta",
        "customer_email": "arjun.mehta@example.com",
        "product": "Agentforce Starter Pack",
        "status": "delivered",
        "expected_delivery": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "actual_delivery": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "delay_days": 0,
        "shipping_partner": "Delhivery",
        "tracking_number": "DL0011223344"
    },
    "ORD-1004": {
        "order_id": "ORD-1004",
        "customer_id": "CUST-004",
        "customer_name": "Sneha Reddy",
        "customer_email": "sneha.reddy@example.com",
        "product": "Marketing Cloud Subscription",
        "status": "delayed",
        "expected_delivery": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "actual_delivery": None,
        "delay_days": 2,
        "shipping_partner": "DTDC",
        "tracking_number": "DTDC556677889"
    }
}

CUSTOMERS = {
    "CUST-001": {"name": "Rahul Sharma", "email": "rahul.sharma@example.com", "tier": "Enterprise", "phone": "+91-9876543210"},
    "CUST-002": {"name": "Priya Nair", "email": "priya.nair@example.com", "tier": "Professional", "phone": "+91-9123456789"},
    "CUST-003": {"name": "Arjun Mehta", "email": "arjun.mehta@example.com", "tier": "Starter", "phone": "+91-9988776655"},
    "CUST-004": {"name": "Sneha Reddy", "email": "sneha.reddy@example.com", "tier": "Professional", "phone": "+91-9001122334"}
}

# ─── Models ───────────────────────────────────────────────────────────────────

class EscalationRequest(BaseModel):
    order_id: str
    reason: str
    priority: str = "High"
    raised_by: Optional[str] = "Agentforce"

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Salesforce Autonomous Support Agent - Mock Backend", "status": "running"}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    """
    Fetch order details by Order ID.
    Called via Apex HTTP callout from Salesforce.
    """
    logger.info(f"[ORDER LOOKUP] Fetching order: {order_id}")
    order = ORDERS.get(order_id.upper())
    if not order:
        logger.warning(f"[ORDER LOOKUP] Order not found: {order_id}")
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    logger.info(f"[ORDER LOOKUP] Found order: {order['status']} | Delay: {order['delay_days']} days")
    return order


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    """
    Fetch customer details by Customer ID.
    Used for agent context enrichment.
    """
    logger.info(f"[CUSTOMER LOOKUP] Fetching customer: {customer_id}")
    customer = CUSTOMERS.get(customer_id.upper())
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


@app.post("/escalate")
def escalate_order(request: EscalationRequest):
    """
    Create an escalation ticket for a delayed order.
    Called by Apex when agent decides delay > threshold.
    Business Rule: delay > 3 days => escalate automatically.
    """
    logger.info(f"[ESCALATION] Creating escalation for order: {request.order_id}")
    order = ORDERS.get(request.order_id.upper())
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {request.order_id} not found")

    escalation_id = f"ESC-{random.randint(10000, 99999)}"
    escalation_record = {
        "escalation_id": escalation_id,
        "order_id": request.order_id,
        "customer_name": order["customer_name"],
        "customer_email": order["customer_email"],
        "delay_days": order["delay_days"],
        "reason": request.reason,
        "priority": request.priority,
        "raised_by": request.raised_by,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "sla_deadline": (datetime.now() + timedelta(hours=4)).isoformat()
    }

    logger.info(f"[ESCALATION] Escalation created: {escalation_id} | Priority: {request.priority}")
    return {
        "success": True,
        "escalation": escalation_record,
        "message": f"Escalation {escalation_id} created successfully. SLA: 4 hours."
    }


@app.get("/orders")
def list_orders():
    """List all mock orders — useful for testing."""
    return list(ORDERS.values())


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
