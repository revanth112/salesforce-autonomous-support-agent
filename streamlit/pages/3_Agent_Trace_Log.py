import streamlit as st
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="Agent Trace Log", page_icon="🔍", layout="wide")

st.title("🔍 Agent Trace Log")
st.markdown("""
Visualizes what `AgentActionLogger.cls` records inside Salesforce.
Every decision the autonomous agent makes is logged with:
- **Action Type** — What the agent did
- **Details** — What data it processed and what decision it made
- **Timestamp** — When it happened

This provides full **observability** of agent behavior — critical for enterprise deployments.
""")
st.divider()

# ─── Simulate Trace Entries ────────────────────────────────────────────────────────────
if "trace_log" not in st.session_state:
    # Pre-populate with a realistic demo trace
    st.session_state["trace_log"] = [
        {
            "Timestamp": "2026-04-02 00:45:01",
            "Order ID": "ORD-1001",
            "Action Type": "ORDER_FETCH",
            "Details": "Status: delayed | Delay: 5 days | Escalate: True",
            "Agent": "Agentforce",
            "Result": "✅ Success",
        },
        {
            "Timestamp": "2026-04-02 00:45:02",
            "Order ID": "ORD-1001",
            "Action Type": "ESCALATION_CREATED",
            "Details": "CaseId: 5001A000001XyZQ | EscalationId: ESC-42891 | Priority: High",
            "Agent": "Agentforce",
            "Result": "✅ Success",
        },
        {
            "Timestamp": "2026-04-02 00:46:15",
            "Order ID": "ORD-1002",
            "Action Type": "ORDER_FETCH",
            "Details": "Status: in_transit | Delay: 0 days | Escalate: False",
            "Agent": "Agentforce",
            "Result": "✅ Success",
        },
        {
            "Timestamp": "2026-04-02 00:47:33",
            "Order ID": "ORD-1003",
            "Action Type": "ORDER_FETCH",
            "Details": "Status: delivered | Delay: 0 days | Escalate: False",
            "Agent": "Agentforce",
            "Result": "✅ Success",
        },
        {
            "Timestamp": "2026-04-02 00:48:10",
            "Order ID": "ORD-9999",
            "Action Type": "ERROR",
            "Details": "Callout failed: Order ORD-9999 not found (404)",
            "Agent": "Agentforce",
            "Result": "❌ Failed",
        },
    ]

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("➕ Simulate New Entry", use_container_width=True):
        orders = ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004"]
        actions = [
            ("ORDER_FETCH", "Status: delayed | Delay: 4 days | Escalate: True", "✅ Success"),
            ("ESCALATION_CREATED", f"CaseId: 5001XYZ | EscalationId: ESC-{random.randint(10000,99999)} | Priority: High", "✅ Success"),
            ("ORDER_FETCH", "Status: in_transit | Delay: 0 days | Escalate: False", "✅ Success"),
            ("ERROR", "Callout timeout: External API did not respond in 10s", "❌ Failed"),
        ]
        order = random.choice(orders)
        action, details, result = random.choice(actions)
        st.session_state["trace_log"].append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Order ID": order,
            "Action Type": action,
            "Details": details,
            "Agent": "Agentforce",
            "Result": result,
        })
        st.rerun()

    if st.button("🗑️ Clear Log", use_container_width=True):
        st.session_state["trace_log"] = []
        st.rerun()

# ─── Metrics ───────────────────────────────────────────────────────────────────────
if st.session_state["trace_log"]:
    df = pd.DataFrame(st.session_state["trace_log"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📝 Total Actions", len(df))
    m2.metric("✅ Successful", len(df[df["Result"].str.startswith("✅")]))
    m3.metric("❌ Errors", len(df[df["Result"].str.startswith("❌")]))
    m4.metric("🚨 Escalations", len(df[df["Action Type"] == "ESCALATION_CREATED"]))

    st.divider()

    # Filter
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        action_filter = st.multiselect(
            "Filter by Action Type:",
            options=df["Action Type"].unique().tolist(),
            default=df["Action Type"].unique().tolist()
        )
    with filter_col2:
        result_filter = st.multiselect(
            "Filter by Result:",
            options=df["Result"].unique().tolist(),
            default=df["Result"].unique().tolist()
        )

    filtered_df = df[
        df["Action Type"].isin(action_filter) &
        df["Result"].isin(result_filter)
    ]

    st.dataframe(
        filtered_df[["Timestamp", "Order ID", "Action Type", "Details", "Agent", "Result"]],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Timeline view
    st.subheader("⏱️ Agent Action Timeline")
    for i, row in filtered_df.iterrows():
        icon = "✅" if row["Result"].startswith("✅") else "❌"
        action_color = {
            "ORDER_FETCH": "🔍",
            "ESCALATION_CREATED": "🚨",
            "ERROR": "❌",
        }.get(row["Action Type"], "⚙️")

        st.markdown(
            f"`{row['Timestamp']}` {action_color} **{row['Action Type']}** — "
            f"`{row['Order ID']}` — {row['Details']} {icon}"
        )
else:
    st.info("No trace entries yet. Run the Agent Simulator or trigger an escalation to generate logs.")

st.divider()

# ─── About section ──────────────────────────────────────────────────────────────────
with st.expander("📚 How this maps to Salesforce (AgentActionLogger.cls)"):
    st.code("""
// In Salesforce, AgentActionLogger.cls writes to Agent_Log__c:
SObject logRecord = (SObject) Type.forName('Agent_Log__c').newInstance();
logRecord.put('Order_Id__c', orderId);
logRecord.put('Action_Type__c', actionType);
logRecord.put('Details__c', details);
logRecord.put('Timestamp__c', Datetime.now());
insert logRecord;
    """, language="java")
    st.markdown("This Streamlit page renders the same data that would appear in Salesforce's `Agent_Log__c` custom object.")
