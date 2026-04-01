import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Escalation Simulator", page_icon="🚨", layout="wide")

BACKEND_URL = st.sidebar.text_input("Backend URL", value="http://localhost:8000")

st.title("🚨 Escalation Simulator")
st.markdown("""
Simulates the full escalation flow executed by `EscalationHandler.cls`.
This page calls the real FastAPI `POST /escalate` endpoint and shows what Salesforce would do —
creating a Case, setting priority, and logging the action.
""")
st.divider()

# ─── Business Logic Explainer ─────────────────────────────────────────────────────
with st.expander("ℹ️ Business Logic Rules (same as Apex)", expanded=True):
    c1, c2, c3 = st.columns(3)
    c1.error("🚨 **Critical**\nDelay > 7 days")
    c2.warning("⚠️ **High**\nDelay > 3 days")
    c3.info("🟡 **Medium**\nDelay ≤ 3 days")

st.divider()

# ─── Manual Escalation Form ───────────────────────────────────────────────────────
st.subheader("📤 Trigger Escalation")

form_col1, form_col2 = st.columns(2)

with form_col1:
    order_id = st.selectbox("Order ID", ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004"])
    delay_days = st.slider("Simulated Delay Days", min_value=0, max_value=14, value=5)
    reason = st.text_area(
        "Escalation Reason",
        value=f"Order delayed by {delay_days} days. Auto-escalated by Agentforce agent."
    )

with form_col2:
    # Live priority preview
    if delay_days > 7:
        priority = "Critical"
        st.error(f"🚨 Priority: **{priority}**\nDelay of {delay_days} days exceeds critical threshold (7 days)")
    elif delay_days > 3:
        priority = "High"
        st.warning(f"⚠️ Priority: **{priority}**\nDelay of {delay_days} days exceeds standard threshold (3 days)")
    else:
        priority = "Medium"
        st.info(f"🟡 Priority: **{priority}**\nDelay of {delay_days} days is within threshold. Escalation optional.")

    st.markdown("")
    raised_by = st.selectbox("Raised By", ["Agentforce (Demo)", "Manual Override", "Apex Trigger"])
    escalate_btn = st.button("🚨 Create Escalation", type="primary", use_container_width=True)

st.divider()

# ─── Escalation Result ───────────────────────────────────────────────────────────────
if escalate_btn:
    with st.spinner("Calling POST /escalate endpoint..."):
        try:
            payload = {
                "order_id": order_id,
                "reason": reason,
                "priority": priority,
                "raised_by": raised_by,
            }
            resp = requests.post(f"{BACKEND_URL}/escalate", json=payload, timeout=5)

            if resp.status_code == 200:
                result = resp.json()
                esc = result["escalation"]

                st.success(f"✅ Escalation Created Successfully!")

                # Escalation card
                st.subheader("🎫 Escalation Record")
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Escalation ID", esc["escalation_id"])
                r2.metric("Priority", esc["priority"])
                r3.metric("Status", esc["status"].title())
                r4.metric("SLA Deadline", esc["sla_deadline"][:16])

                st.divider()

                # Simulated Salesforce Case
                st.subheader("☁️ Simulated Salesforce Case (Service Cloud)")
                st.markdown("""
                > This is what `EscalationHandler.cls` would create in Salesforce Service Cloud.
                """)
                case_col1, case_col2 = st.columns(2)
                with case_col1:
                    st.markdown(f"**Subject:** `Order Delayed: {order_id} ({delay_days} days)`")
                    st.markdown(f"**Origin:** `Agentforce`")
                    st.markdown(f"**Status:** `New`")
                    st.markdown(f"**Priority:** `{priority}`")
                with case_col2:
                    st.markdown(f"**Customer:** {esc['customer_name']}")
                    st.markdown(f"**Email:** {esc['customer_email']}")
                    st.markdown(f"**External Escalation ID:** `{esc['escalation_id']}`")
                    st.markdown(f"**Created At:** {esc['created_at'][:19]}")

                # Agent action log entry
                st.divider()
                st.subheader("📝 Agent Action Log Entry")
                st.code(
                    f"[ESCALATION_CREATED] Order: {order_id} | "
                    f"EscalationId: {esc['escalation_id']} | "
                    f"Priority: {priority} | "
                    f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    language="text"
                )

                with st.expander("📄 Full API Response JSON"):
                    st.json(result)

                # Add to session log
                if "escalation_log" not in st.session_state:
                    st.session_state["escalation_log"] = []
                st.session_state["escalation_log"].append({
                    "Escalation ID": esc["escalation_id"],
                    "Order ID": order_id,
                    "Customer": esc["customer_name"],
                    "Priority": priority,
                    "Delay (days)": delay_days,
                    "Raised By": raised_by,
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "SLA": esc["sla_deadline"][:16],
                })

            else:
                st.error(f"API returned error: {resp.status_code} — {resp.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure FastAPI is running.")

# ─── Session Escalation Log ───────────────────────────────────────────────────────
if "escalation_log" in st.session_state and st.session_state["escalation_log"]:
    st.divider()
    st.subheader("📊 This Session's Escalation Log")
    df = pd.DataFrame(st.session_state["escalation_log"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("🗑️ Clear Log"):
        st.session_state["escalation_log"] = []
        st.rerun()
