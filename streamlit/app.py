import streamlit as st
import requests
import time

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Autonomous Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Config ───────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"  # Change to deployed URL when live

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg", width=160)
    st.markdown("## Autonomous Support Agent")
    st.markdown("**Salesforce Agentforce + Apex + FastAPI**")
    st.divider()
    backend_url = st.text_input("Backend URL", value=BACKEND_URL)
    st.caption("Run `uvicorn main:app --reload` in /backend first.")
    st.divider()
    st.markdown("### Navigation")
    st.page_link("app.py", label="🤖 Agent Simulator", icon="🏠")
    st.page_link("pages/1_Order_Lookup.py", label="📦 Order Lookup")
    st.page_link("pages/2_Escalation_Simulator.py", label="🚨 Escalation Simulator")
    st.page_link("pages/3_Agent_Trace_Log.py", label="🔍 Agent Trace Log")
    st.divider()
    st.markdown("**Mock Orders Available:**")
    st.code("ORD-1001 → Delayed 5 days\nORD-1002 → In Transit\nORD-1003 → Delivered\nORD-1004 → Delayed 2 days")

# ─── Hero ────────────────────────────────────────────────────────────────────
st.title("🤖 Autonomous Customer Support Agent")
st.markdown("""
> **Understand → Decide → Act → Update Systems → Respond**

This demo simulates a Salesforce Agentforce agent that autonomously handles customer order queries.
It calls a real Python FastAPI backend, applies business logic, and takes multi-step actions.
""")
st.divider()

# ─── Agent Chat Simulator ─────────────────────────────────────────────────────
st.subheader("💬 Ask the Agent")

col1, col2 = st.columns([3, 1])
with col1:
    user_query = st.text_input(
        "Customer message:",
        value="Where is my order ORD-1001 and can you escalate if delayed?",
        label_visibility="collapsed",
    )
with col2:
    run_btn = st.button("▶ Run Agent", type="primary", use_container_width=True)

# ─── Sample Queries ───────────────────────────────────────────────────────────
st.markdown("**Quick examples:**")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)
with q_col1:
    if st.button("ORD-1001 (Delayed 5d)", use_container_width=True):
        st.session_state["selected_order"] = "ORD-1001"
with q_col2:
    if st.button("ORD-1002 (In Transit)", use_container_width=True):
        st.session_state["selected_order"] = "ORD-1002"
with q_col3:
    if st.button("ORD-1003 (Delivered)", use_container_width=True):
        st.session_state["selected_order"] = "ORD-1003"
with q_col4:
    if st.button("ORD-1004 (Delayed 2d)", use_container_width=True):
        st.session_state["selected_order"] = "ORD-1004"

# Get order ID from query or session
order_id = "ORD-1001"
if "selected_order" in st.session_state:
    order_id = st.session_state["selected_order"]
for word in user_query.upper().split():
    if word.startswith("ORD-"):
        order_id = word
        break

st.divider()

# ─── Agent Execution ──────────────────────────────────────────────────────────
if run_btn or "selected_order" in st.session_state:
    if "selected_order" in st.session_state:
        del st.session_state["selected_order"]

    st.subheader("⚙️ Agent Execution Trace")

    trace_container = st.container()
    result_container = st.container()

    with trace_container:
        # Step 1
        with st.status("🧠 Step 1: Understanding customer intent...", expanded=True) as s1:
            time.sleep(0.6)
            st.write(f"Detected order ID: `{order_id}`")
            st.write("Intent: **Order Status Inquiry + Conditional Escalation**")
            s1.update(label="✅ Step 1: Intent understood", state="complete")

        # Step 2
        with st.status(f"🔍 Step 2: Calling Order API → GET /orders/{order_id}...", expanded=True) as s2:
            time.sleep(0.5)
            try:
                resp = requests.get(f"{backend_url}/orders/{order_id}", timeout=5)
                if resp.status_code == 200:
                    order = resp.json()
                    st.json(order)
                    s2.update(label=f"✅ Step 2: Order fetched — Status: {order['status'].upper()}", state="complete")
                elif resp.status_code == 404:
                    st.error(f"Order `{order_id}` not found in system.")
                    s2.update(label="❌ Step 2: Order not found", state="error")
                    st.stop()
                else:
                    st.error(f"Backend returned error: {resp.status_code}")
                    s2.update(label="❌ Step 2: API error", state="error")
                    st.stop()
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is the FastAPI server running?")
                s2.update(label="❌ Step 2: Backend unreachable", state="error")
                st.stop()

        # Step 3: Business Logic
        delay_days = order.get("delay_days", 0)
        status = order.get("status", "unknown")
        requires_escalation = status == "delayed" and delay_days > 3

        with st.status("📊 Step 3: Applying business logic...", expanded=True) as s3:
            time.sleep(0.5)
            st.write(f"- Order Status: `{status}`")
            st.write(f"- Delay Days: `{delay_days}`")
            st.write(f"- Threshold: `3 days`")
            st.write(f"- Requires Escalation: `{requires_escalation}`")
            if requires_escalation:
                priority = "Critical" if delay_days > 7 else "High"
                st.warning(f"⚠️ Delay exceeds threshold → **Escalating with priority: {priority}**")
            else:
                st.success("✅ Delay within acceptable range → No escalation needed")
            s3.update(label="✅ Step 3: Business logic evaluated", state="complete")

        # Step 4: Escalation (conditional)
        escalation_result = None
        if requires_escalation:
            with st.status("🚨 Step 4: Creating escalation ticket → POST /escalate...", expanded=True) as s4:
                time.sleep(0.6)
                try:
                    esc_payload = {
                        "order_id": order_id,
                        "reason": f"Order delayed by {delay_days} days. Auto-escalated by Agentforce agent.",
                        "priority": "Critical" if delay_days > 7 else "High",
                        "raised_by": "Agentforce (Demo)"
                    }
                    esc_resp = requests.post(f"{backend_url}/escalate", json=esc_payload, timeout=5)
                    if esc_resp.status_code == 200:
                        escalation_result = esc_resp.json()
                        st.json(escalation_result)
                        s4.update(label=f"✅ Step 4: Escalation created — {escalation_result['escalation']['escalation_id']}", state="complete")
                    else:
                        s4.update(label="❌ Step 4: Escalation API error", state="error")
                except Exception as e:
                    s4.update(label=f"❌ Step 4: Error — {str(e)}", state="error")
        else:
            with st.status("⏭️ Step 4: Escalation skipped (delay within threshold)") as s4:
                time.sleep(0.3)
                s4.update(label="⏭️ Step 4: No escalation required", state="complete")

        # Step 5: Build Response
        with st.status("💬 Step 5: Building agent response...", expanded=True) as s5:
            time.sleep(0.4)
            customer_name = order.get("customer_name", "Customer")
            if status == "delivered":
                agent_msg = f"Hi {customer_name}, your order has been successfully delivered. Is there anything else I can help you with?"
            elif status == "in_transit":
                agent_msg = f"Hi {customer_name}, your order is currently in transit and on schedule. You should receive it within the expected delivery window."
            elif status == "delayed" and requires_escalation:
                esc_id = escalation_result["escalation"]["escalation_id"] if escalation_result else "N/A"
                agent_msg = (
                    f"Hi {customer_name}, your order `{order_id}` is delayed by {delay_days} days.\n\n"
                    f"Because this exceeds our 3-day threshold, I have automatically escalated your case.\n"
                    f"**Escalation ID:** `{esc_id}`\n"
                    f"Our team will contact you at `{order.get('customer_email', 'your email')}` within 4 hours."
                )
            else:
                agent_msg = f"Hi {customer_name}, your order `{order_id}` is currently delayed by {delay_days} days. Our team is actively working to resolve this."
            s5.update(label="✅ Step 5: Response ready", state="complete")

    # ─── Final Output ─────────────────────────────────────────────────────────
    with result_container:
        st.divider()
        st.subheader("🤖 Agent Response")
        st.success(agent_msg)

        # Metrics
        st.divider()
        st.subheader("📊 Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Order ID", order_id)
        m2.metric("Status", status.replace("_", " ").title())
        m3.metric("Delay Days", delay_days)
        m4.metric("Escalated", "Yes" if requires_escalation else "No")

        if escalation_result:
            st.info(f"🎫 **Salesforce Case** would be created with priority: **{esc_payload['priority']}** | SLA: 4 hours")
