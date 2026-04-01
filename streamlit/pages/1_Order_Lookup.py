import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Order Lookup", page_icon="📦", layout="wide")

BACKEND_URL = st.sidebar.text_input("Backend URL", value="http://localhost:8000")

st.title("📦 Order Lookup")
st.markdown("Fetch and inspect real-time order data from the external FastAPI system — exactly what the Apex callout does inside Salesforce.")
st.divider()

# ─── All Orders Table ───────────────────────────────────────────────────────────
st.subheader("📊 All Orders Dashboard")

col_refresh, _ = st.columns([1, 5])
with col_refresh:
    load_all = st.button("🔄 Load All Orders", type="primary", use_container_width=True)

if load_all:
    try:
        resp = requests.get(f"{BACKEND_URL}/orders", timeout=5)
        if resp.status_code == 200:
            orders = resp.json()
            df = pd.DataFrame(orders)

            # Color-coded status
            def status_badge(s):
                badges = {
                    "delayed": "🔴 Delayed",
                    "in_transit": "🟡 In Transit",
                    "delivered": "🟢 Delivered",
                }
                return badges.get(s, s)

            df["status_display"] = df["status"].apply(status_badge)
            df["escalation_risk"] = df.apply(
                lambda r: "🚨 HIGH" if r["status"] == "delayed" and r["delay_days"] > 3 else ("⚠️ Medium" if r["delay_days"] > 0 else "✅ None"),
                axis=1
            )

            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📦 Total Orders", len(df))
            m2.metric("🔴 Delayed", len(df[df["status"] == "delayed"]))
            m3.metric("🟡 In Transit", len(df[df["status"] == "in_transit"]))
            m4.metric("🟢 Delivered", len(df[df["status"] == "delivered"]))

            st.divider()

            # Table
            st.dataframe(
                df[["order_id", "customer_name", "product", "status_display", "delay_days", "expected_delivery", "escalation_risk", "tracking_number"]].rename(columns={
                    "order_id": "Order ID",
                    "customer_name": "Customer",
                    "product": "Product",
                    "status_display": "Status",
                    "delay_days": "Delay (days)",
                    "expected_delivery": "Expected Delivery",
                    "escalation_risk": "Escalation Risk",
                    "tracking_number": "Tracking #",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.error(f"API returned {resp.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure FastAPI is running on the URL above.")

st.divider()

# ─── Individual Order Lookup ────────────────────────────────────────────────────
st.subheader("🔎 Single Order Lookup")
st.caption("Simulates the Apex HTTP callout: GET /orders/{order_id}")

lookup_col1, lookup_col2 = st.columns([3, 1])
with lookup_col1:
    order_id = st.selectbox(
        "Select Order ID:",
        ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004"],
        label_visibility="collapsed"
    )
with lookup_col2:
    fetch_btn = st.button("🔍 Fetch Order", type="primary", use_container_width=True)

if fetch_btn:
    try:
        resp = requests.get(f"{BACKEND_URL}/orders/{order_id}", timeout=5)
        if resp.status_code == 200:
            order = resp.json()

            # Details panel
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Order Details")
                st.markdown(f"**Order ID:** `{order['order_id']}`")
                st.markdown(f"**Product:** {order['product']}")
                st.markdown(f"**Status:** `{order['status'].upper()}`")
                st.markdown(f"**Expected Delivery:** {order['expected_delivery']}")
                st.markdown(f"**Actual Delivery:** {order.get('actual_delivery') or 'Not yet delivered'}")
                st.markdown(f"**Delay Days:** `{order['delay_days']}`")
                st.markdown(f"**Shipping Partner:** {order['shipping_partner']}")
                st.markdown(f"**Tracking #:** `{order['tracking_number']}`")

            with c2:
                st.markdown("#### Customer Info")
                st.markdown(f"**Name:** {order['customer_name']}")
                st.markdown(f"**Email:** {order['customer_email']}")
                st.markdown(f"**Customer ID:** `{order['customer_id']}`")

                st.divider()
                st.markdown("#### Agent Decision")
                requires_esc = order["status"] == "delayed" and order["delay_days"] > 3
                if requires_esc:
                    priority = "Critical" if order["delay_days"] > 7 else "High"
                    st.error(f"🚨 **ESCALATE** — Delay exceeds 3-day threshold\nPriority: **{priority}**")
                elif order["status"] == "delayed":
                    st.warning("⚠️ Delayed but within threshold. Monitor.")
                elif order["status"] == "delivered":
                    st.success("✅ Delivered. No action needed.")
                else:
                    st.info("🟡 In Transit. On schedule.")

            st.divider()
            with st.expander("📄 Raw JSON Response (as Apex would receive)"):
                st.json(order)
        elif resp.status_code == 404:
            st.error(f"Order `{order_id}` not found.")
        else:
            st.error(f"Error: {resp.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
