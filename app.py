from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Smart Cashflow MVP", page_icon=":moneybag:", layout="wide")


def inr(value: float) -> str:
    return f"Rs {value:,.0f}"


def build_demo_data():
    today = date.today()

    invoices = pd.DataFrame(
        [
            {
                "invoice_number": "INV-1001",
                "client_name": "Northwind Retail",
                "due_date": today - timedelta(days=10),
                "amount": 250000.0,
                "amount_paid_base": 250000.0,
                "status": "paid",
                "last_payment_date": today - timedelta(days=8),
            },
            {
                "invoice_number": "INV-1002",
                "client_name": "Northwind Retail",
                "due_date": today + timedelta(days=3),
                "amount": 180000.0,
                "amount_paid_base": 99000.0,
                "status": "partially_paid",
                "last_payment_date": today - timedelta(days=1),
            },
            {
                "invoice_number": "INV-2001",
                "client_name": "LatePay GmbH",
                "due_date": today - timedelta(days=15),
                "amount": 325000.0,
                "amount_paid_base": 0.0,
                "status": "pending",
                "last_payment_date": None,
            },
            {
                "invoice_number": "INV-1999",
                "client_name": "LatePay GmbH",
                "due_date": today - timedelta(days=60),
                "amount": 210000.0,
                "amount_paid_base": 210000.0,
                "status": "paid",
                "last_payment_date": today - timedelta(days=40),
            },
        ]
    )

    payments = pd.DataFrame(
        [
            {
                "payment_reference": "PAY-EXACT-001",
                "client_name": "Northwind Retail",
                "payment_date": today - timedelta(days=8),
                "amount_received": 3000.0,
                "source_currency": "USD",
                "net_amount_base": 250000.0,
            },
            {
                "payment_reference": "PAY-PARTIAL-001",
                "client_name": "Northwind Retail",
                "payment_date": today - timedelta(days=1),
                "amount_received": 1200.0,
                "source_currency": "USD",
                "net_amount_base": 99000.0,
            },
        ]
    )

    reconciliation = pd.DataFrame(
        [
            {
                "payment_id": 1,
                "invoice_id": 1,
                "status": "matched",
                "matched_amount_base": 250000.0,
                "delta_amount_base": 0.0,
            },
            {
                "payment_id": 2,
                "invoice_id": 2,
                "status": "partially_matched",
                "matched_amount_base": 99000.0,
                "delta_amount_base": 81000.0,
            },
        ]
    )

    return invoices, payments, reconciliation


def compute_summary(invoices: pd.DataFrame, payments: pd.DataFrame):
    today = date.today()
    total_received = float(payments["net_amount_base"].sum())

    invoices = invoices.copy()
    invoices["due_date"] = pd.to_datetime(invoices["due_date"])
    invoices["last_payment_date"] = pd.to_datetime(invoices["last_payment_date"], errors="coerce")

    paid = invoices[invoices["status"] == "paid"].copy()
    paid = paid.dropna(subset=["last_payment_date"])
    paid["delay"] = (paid["last_payment_date"] - paid["due_date"]).dt.days
    delay_by_client = paid.groupby("client_name")["delay"].mean().to_dict()

    invoices["pending_amount"] = invoices["amount"] - invoices["amount_paid_base"]
    invoices["avg_delay"] = invoices["client_name"].map(delay_by_client).fillna(0).clip(lower=0)
    invoices["predicted_payment_date"] = invoices["due_date"] + pd.to_timedelta(
        invoices["avg_delay"].astype(int), unit="D"
    )

    expected_7d = float(
        invoices[
            (invoices["pending_amount"] > 0)
            & (invoices["predicted_payment_date"] >= pd.Timestamp(today))
            & (invoices["predicted_payment_date"] <= pd.Timestamp(today + timedelta(days=7)))
        ]["pending_amount"].sum()
    )

    overdue_amount = float(
        invoices[
            (invoices["pending_amount"] > 0)
            & (invoices["due_date"] < pd.Timestamp(today))
        ]["pending_amount"].sum()
    )

    risky_clients = sorted(
        invoices.loc[invoices["avg_delay"] >= 10, "client_name"].dropna().unique().tolist()
    )

    invoices["status"] = invoices.apply(
        lambda row: "overdue"
        if row["pending_amount"] > 0 and row["due_date"] < pd.Timestamp(today)
        else row["status"],
        axis=1,
    )

    return total_received, expected_7d, overdue_amount, risky_clients, invoices


def forex_chart():
    rates = [88.9, 89.4, 89.1, 90.2, 90.8, 91.7, 91.3, 92.1, 92.53]
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=rates,
            mode="lines+markers",
            line=dict(color="#111827", width=3),
            marker=dict(size=6, color="#111827"),
            fill="tozeroy",
            fillcolor="rgba(17,24,39,0.08)",
            name="USD/INR",
        )
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eef2ff"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def main():
    invoices, payments, reconciliation = build_demo_data()
    total_received, expected_7d, overdue_amount, risky_clients, invoices = compute_summary(
        invoices, payments
    )

    st.markdown("## Smart Cashflow MVP")
    st.caption("Cash Flow Intelligence for Exporters")

    left, right = st.columns([2, 1])
    with left:
        st.markdown("### Know exactly when your export cash lands")
        st.write(
            "A clean operations cockpit for invoices, payment matching, delayed clients, and expected inflows."
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Received", inr(total_received))
        c2.metric("Expected Inflow (Next 7d)", inr(expected_7d))
        c3.metric("Overdue Amount", inr(overdue_amount))

    with right:
        st.markdown("#### USD/INR Trend")
        st.metric("Current Rate", "92.53", "+0.84%")
        forex_chart()

    st.markdown("---")
    st.subheader("Delayed / Risky Clients")
    if risky_clients:
        st.write(", ".join(risky_clients))
    else:
        st.write("No risky clients flagged in current window.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Invoices")
        invoice_view = invoices[
            ["invoice_number", "client_name", "due_date", "status", "amount_paid_base", "amount"]
        ].copy()
        invoice_view["amount_paid_base"] = invoice_view["amount_paid_base"].map(inr)
        invoice_view["amount"] = invoice_view["amount"].map(inr)
        st.dataframe(invoice_view, use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("Payments")
        payment_view = payments[
            ["payment_reference", "client_name", "payment_date", "source_currency", "net_amount_base"]
        ].copy()
        payment_view["net_amount_base"] = payment_view["net_amount_base"].map(inr)
        st.dataframe(payment_view, use_container_width=True, hide_index=True)

    st.subheader("Reconciliation Status")
    rec_view = reconciliation.copy()
    rec_view["matched_amount_base"] = rec_view["matched_amount_base"].map(inr)
    rec_view["delta_amount_base"] = rec_view["delta_amount_base"].map(inr)
    st.dataframe(rec_view, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
