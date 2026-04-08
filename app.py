from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Smart Cashflow MVP", page_icon=":moneybag:", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(56,189,248,0.25) 0%, rgba(56,189,248,0) 35%),
            radial-gradient(circle at 85% 15%, rgba(34,197,94,0.20) 0%, rgba(34,197,94,0) 30%),
            radial-gradient(circle at 55% 80%, rgba(99,102,241,0.20) 0%, rgba(99,102,241,0) 28%),
            linear-gradient(145deg, #eef2ff 0%, #f8fafc 50%, #eff6ff 100%);
    }
    .hero-wrap {
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.45);
        backdrop-filter: blur(14px);
        padding: 1.1rem 1.2rem 1.3rem 1.2rem;
        box-shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
    }
    .hero-top {
        background: rgba(15, 23, 42, 0.9);
        color: #f8fafc;
        border-radius: 12px;
        padding: 0.45rem 0.7rem;
        font-size: 0.78rem;
        letter-spacing: 0.03em;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.2rem;
        line-height: 1.1;
        font-weight: 650;
        color: #0f172a;
        margin: 0.2rem 0 0.5rem 0;
    }
    .hero-sub {
        color: #475569;
        font-size: 1rem;
        margin-bottom: 0;
    }
    .metric-card {
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.38);
        backdrop-filter: blur(10px);
        padding: 0.9rem 1rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    .metric-label {
        color: #64748b;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 650;
        margin: 0;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0f172a;
        margin: 0.4rem 0 0.6rem 0;
    }
    .panel {
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(12px);
        padding: 0.9rem 1rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    .small-muted {
        color: #64748b;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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

    for i in range(len(rates) - 1):
        up = rates[i + 1] >= rates[i]
        color = "#16a34a" if up else "#dc2626"
        fig.add_trace(
            go.Scatter(
                x=[labels[i], labels[i + 1]],
                y=[rates[i], rates[i + 1]],
                mode="lines",
                line=dict(color=color, width=3),
                showlegend=False,
                hovertemplate="USD/INR: %{y}<extra></extra>",
            )
        )

    marker_colors = ["#16a34a"]
    for i in range(1, len(rates)):
        marker_colors.append("#16a34a" if rates[i] >= rates[i - 1] else "#dc2626")

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=rates,
            mode="markers",
            marker=dict(size=7, color=marker_colors, line=dict(color="white", width=1)),
            showlegend=False,
            hovertemplate="USD/INR: %{y}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=rates,
            mode="lines",
            line=dict(color="rgba(30,41,59,0.15)", width=1),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.08)",
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=190,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.35)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.25)"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def main():
    invoices, payments, reconciliation = build_demo_data()
    total_received, expected_7d, overdue_amount, risky_clients, invoices = compute_summary(
        invoices, payments
    )

    st.markdown(
        """
        <div class="hero-wrap">
          <div class="hero-top">Smart Cashflow MVP</div>
          <div class="hero-title">Know exactly when your export cash lands.</div>
          <p class="hero-sub">A clean operations cockpit for invoices, payment matching, delayed clients, and expected inflows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3 = st.columns(3, gap="small")
    c1.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">Total Received</div>
          <p class="metric-value">{inr(total_received)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">Expected Inflow (Next 7d)</div>
          <p class="metric-value">{inr(expected_7d)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">Overdue Amount</div>
          <p class="metric-value">{inr(overdue_amount)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    fx_left, fx_right = st.columns([1.1, 2.3], gap="large")
    with fx_left:
        st.markdown(
            """
            <div class="panel">
              <div class="metric-label">USD / INR</div>
              <div style="font-size:2rem;font-weight:650;color:#0f172a;line-height:1;">92.53</div>
              <div class="small-muted" style="margin-top:0.4rem;">+0.84% this week</div>
              <div class="small-muted" style="margin-top:0.6rem;">Indicative live trend for settlement planning.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with fx_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Forex Rate Trend</div>', unsafe_allow_html=True)
        forex_chart()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.subheader("Delayed / Risky Clients")
    if risky_clients:
        st.write(", ".join(risky_clients))
    else:
        st.write("No risky clients flagged in current window.")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.subheader("Invoices")
        invoice_view = invoices[
            ["invoice_number", "client_name", "due_date", "status", "amount_paid_base", "amount"]
        ].copy()
        invoice_view["amount_paid_base"] = invoice_view["amount_paid_base"].map(inr)
        invoice_view["amount"] = invoice_view["amount"].map(inr)
        st.dataframe(
            invoice_view,
            use_container_width=True,
            hide_index=True,
            height=230,
            column_config={
                "status": st.column_config.TextColumn("status"),
            },
        )

    with col_b:
        st.subheader("Payments")
        payment_view = payments[
            ["payment_reference", "client_name", "payment_date", "source_currency", "net_amount_base"]
        ].copy()
        payment_view["net_amount_base"] = payment_view["net_amount_base"].map(inr)
        st.dataframe(payment_view, use_container_width=True, hide_index=True, height=230)

    st.subheader("Reconciliation Status")
    rec_view = reconciliation.copy()
    rec_view["matched_amount_base"] = rec_view["matched_amount_base"].map(inr)
    rec_view["delta_amount_base"] = rec_view["delta_amount_base"].map(inr)
    st.dataframe(rec_view, use_container_width=True, hide_index=True, height=170)


if __name__ == "__main__":
    main()
