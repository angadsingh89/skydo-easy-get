from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Smart Cashflow MVP", page_icon=":moneybag:", layout="wide")


def theme_css() -> str:
    return """
    <style>
    :root{
      --bg:#f8fafc;
      --text:#0f172a;
      --muted:#64748b;
      --line:rgba(148,163,184,.28);
      --glass:rgba(255,255,255,.55);
      --glass-soft:rgba(255,255,255,.38);
      --primary-start:#4f46e5;
      --primary-end:#06b6d4;
    }
    .stApp{
      color:var(--text);
      background:
        radial-gradient(900px 300px at -5% -10%, rgba(79,70,229,.20), transparent 50%),
        radial-gradient(700px 260px at 105% 0%, rgba(6,182,212,.16), transparent 45%),
        linear-gradient(180deg,#f8fbff 0%, #f7faff 35%, #f8fafc 100%);
    }
    [data-testid="stHeader"]{background:transparent;}
    [data-testid="stSidebar"]{
      background:rgba(255,255,255,.62);
      border-right:1px solid rgba(255,255,255,.65);
      backdrop-filter: blur(12px);
    }
    .brand{
      font:600 1.15rem/1.2 Inter,system-ui,sans-serif;
      letter-spacing:.01em;color:var(--text);margin:.1rem 0 .8rem 0;
    }
    .nav-pill{
      border:1px solid var(--line);
      border-radius:12px;
      padding:.45rem .65rem;
      margin:.3rem 0;
      font-size:.82rem;
      color:#334155;
      background:rgba(255,255,255,.54);
    }
    .nav-pill.active{
      color:white;
      border-color:transparent;
      background:linear-gradient(90deg,var(--primary-start),var(--primary-end));
      box-shadow:0 8px 24px rgba(79,70,229,.24);
    }
    .topbar{
      display:flex;justify-content:space-between;align-items:center;
      border:1px solid rgba(255,255,255,.7);
      background:var(--glass);
      backdrop-filter:blur(12px);
      border-radius:16px;padding:.65rem .9rem;margin-bottom:1rem;
    }
    .badge{
      padding:.24rem .6rem;border-radius:999px;
      font-size:.74rem;color:#334155;
      background:rgba(255,255,255,.8);border:1px solid var(--line);
    }
    .btn-primary{
      border:none;border-radius:12px;padding:.52rem .82rem;
      color:white;font-weight:600;font-size:.82rem;
      background:linear-gradient(90deg,var(--primary-start),var(--primary-end));
      box-shadow:0 10px 28px rgba(79,70,229,.27);
      transition:all .25s ease;
    }
    .hero{
      border:1px solid rgba(255,255,255,.75);
      background:var(--glass);
      backdrop-filter: blur(14px);
      border-radius:20px;padding:1.1rem 1.2rem;margin-bottom:1rem;
      box-shadow:0 18px 50px rgba(15,23,42,.08);
    }
    .hero-kicker{
      display:inline-block;border-radius:999px;padding:.22rem .6rem;
      font-size:.72rem;color:#312e81;
      border:1px solid rgba(79,70,229,.22);background:rgba(99,102,241,.11);
      margin-bottom:.6rem;
    }
    .hero-title{
      margin:.1rem 0 .4rem 0;
      font-size:2.1rem;line-height:1.08;font-weight:700;letter-spacing:-.02em;color:#0f172a;
    }
    .hero-sub{margin:0;color:#475569;font-size:.98rem;}
    .card{
      border:1px solid rgba(255,255,255,.75);
      background:var(--glass-soft);
      backdrop-filter: blur(12px);
      border-radius:16px;padding:.9rem 1rem;
      box-shadow:0 12px 30px rgba(15,23,42,.07);
      transition:all .24s ease;
    }
    .card:hover{transform:translateY(-2px);}
    .label{
      color:var(--muted);font-size:.72rem;letter-spacing:.06em;
      text-transform:uppercase;font-weight:600;
    }
    .value{
      margin:.25rem 0 0 0;color:var(--text);font-size:1.65rem;font-weight:700;
    }
    .section{
      border:1px solid rgba(255,255,255,.75);
      background:var(--glass-soft);
      backdrop-filter: blur(12px);
      border-radius:16px;padding:.82rem .95rem;
      box-shadow:0 12px 30px rgba(15,23,42,.07);
    }
    .section-title{font-size:1.02rem;font-weight:650;color:#0f172a;margin:.1rem 0 .55rem 0;}
    .muted{color:var(--muted);font-size:.84rem;margin-top:.3rem;}
    .risk-chip{
      display:inline-block;padding:.25rem .62rem;border-radius:999px;
      font-size:.75rem;margin:.2rem .3rem .2rem 0;
      background:rgba(244,63,94,.12);color:#be123c;border:1px solid rgba(244,63,94,.20);
    }
    .table-wrap{
      border:1px solid rgba(255,255,255,.75);
      border-radius:16px;background:var(--glass-soft);backdrop-filter:blur(12px);
      padding:.45rem .55rem .55rem .55rem;overflow:auto;box-shadow:0 12px 30px rgba(15,23,42,.07);
    }
    .table-wrap table{width:100%;border-collapse:separate;border-spacing:0;font-size:.84rem;color:#0f172a;}
    .table-wrap thead th{
      text-align:left;padding:.55rem .5rem;font-size:.70rem;text-transform:uppercase;letter-spacing:.04em;
      color:#334155;background:rgba(255,255,255,.7);border-bottom:1px solid var(--line);
      position:sticky;top:0;
    }
    .table-wrap tbody td{
      padding:.52rem .5rem;border-bottom:1px solid rgba(148,163,184,.17);white-space:nowrap;font-weight:500;
    }
    .table-wrap tbody tr:hover{background:rgba(255,255,255,.55);}
    .status{
      display:inline-block;padding:.18rem .45rem;border-radius:999px;font-size:.72rem;font-weight:600;
      border:1px solid transparent;
    }
    .status-paid{color:#166534;background:rgba(34,197,94,.12);border-color:rgba(34,197,94,.22);}
    .status-overdue{color:#b91c1c;background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.22);}
    .status-partial{color:#92400e;background:rgba(245,158,11,.14);border-color:rgba(245,158,11,.26);}
    .status-pending{color:#1d4ed8;background:rgba(59,130,246,.12);border-color:rgba(59,130,246,.22);}
    @media (max-width: 900px){
      .hero-title{font-size:1.7rem;}
    }
    </style>
    """


def inr(value: float) -> str:
    return f"Rs {value:,.0f}"


def build_demo_data():
    today = date.today()
    invoices = pd.DataFrame(
        [
            {"invoice_number": "INV-1001", "client_name": "Northwind Retail", "due_date": today - timedelta(days=10), "amount": 250000.0, "amount_paid_base": 250000.0, "status": "paid", "last_payment_date": today - timedelta(days=8)},
            {"invoice_number": "INV-1002", "client_name": "Northwind Retail", "due_date": today + timedelta(days=3), "amount": 180000.0, "amount_paid_base": 99000.0, "status": "partially_paid", "last_payment_date": today - timedelta(days=1)},
            {"invoice_number": "INV-2001", "client_name": "LatePay GmbH", "due_date": today - timedelta(days=15), "amount": 325000.0, "amount_paid_base": 0.0, "status": "pending", "last_payment_date": None},
            {"invoice_number": "INV-1999", "client_name": "LatePay GmbH", "due_date": today - timedelta(days=60), "amount": 210000.0, "amount_paid_base": 210000.0, "status": "paid", "last_payment_date": today - timedelta(days=40)},
        ]
    )
    payments = pd.DataFrame(
        [
            {"payment_reference": "PAY-EXACT-001", "client_name": "Northwind Retail", "payment_date": today - timedelta(days=8), "amount_received": 3000.0, "source_currency": "USD", "net_amount_base": 250000.0},
            {"payment_reference": "PAY-PARTIAL-001", "client_name": "Northwind Retail", "payment_date": today - timedelta(days=1), "amount_received": 1200.0, "source_currency": "USD", "net_amount_base": 99000.0},
        ]
    )
    reconciliation = pd.DataFrame(
        [
            {"payment_id": 1, "invoice_id": 1, "status": "matched", "matched_amount_base": 250000.0, "delta_amount_base": 0.0},
            {"payment_id": 2, "invoice_id": 2, "status": "partially_matched", "matched_amount_base": 99000.0, "delta_amount_base": 81000.0},
        ]
    )
    return invoices, payments, reconciliation


def compute_summary(invoices: pd.DataFrame, payments: pd.DataFrame):
    today = date.today()
    total_received = float(payments["net_amount_base"].sum())
    invoices = invoices.copy()
    invoices["due_date"] = pd.to_datetime(invoices["due_date"])
    invoices["last_payment_date"] = pd.to_datetime(invoices["last_payment_date"], errors="coerce")
    paid = invoices[invoices["status"] == "paid"].dropna(subset=["last_payment_date"]).copy()
    paid["delay"] = (paid["last_payment_date"] - paid["due_date"]).dt.days
    delay_by_client = paid.groupby("client_name")["delay"].mean().to_dict()
    invoices["pending_amount"] = invoices["amount"] - invoices["amount_paid_base"]
    invoices["avg_delay"] = invoices["client_name"].map(delay_by_client).fillna(0).clip(lower=0)
    invoices["predicted_payment_date"] = invoices["due_date"] + pd.to_timedelta(invoices["avg_delay"].astype(int), unit="D")
    expected_7d = float(
        invoices[
            (invoices["pending_amount"] > 0)
            & (invoices["predicted_payment_date"] >= pd.Timestamp(today))
            & (invoices["predicted_payment_date"] <= pd.Timestamp(today + timedelta(days=7)))
        ]["pending_amount"].sum()
    )
    overdue_amount = float(invoices[(invoices["pending_amount"] > 0) & (invoices["due_date"] < pd.Timestamp(today))]["pending_amount"].sum())
    risky_clients = sorted(invoices.loc[invoices["avg_delay"] >= 10, "client_name"].dropna().unique().tolist())
    invoices["status"] = invoices.apply(
        lambda row: "overdue" if row["pending_amount"] > 0 and row["due_date"] < pd.Timestamp(today) else row["status"],
        axis=1,
    )
    return total_received, expected_7d, overdue_amount, risky_clients, invoices


def forex_chart():
    rates = [88.9, 89.4, 89.1, 90.2, 90.8, 91.7, 91.3, 92.1, 92.53]
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"]
    fig = go.Figure()
    for i in range(len(rates) - 1):
        color = "#16a34a" if rates[i + 1] >= rates[i] else "#ef4444"
        fig.add_trace(
            go.Scatter(
                x=[labels[i], labels[i + 1]],
                y=[rates[i], rates[i + 1]],
                mode="lines",
                line=dict(color=color, width=3),
                hovertemplate="USD/INR: %{y}<extra></extra>",
                showlegend=False,
            )
        )
    markers = ["#16a34a"] + ["#16a34a" if rates[i] >= rates[i - 1] else "#ef4444" for i in range(1, len(rates))]
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=rates,
            mode="markers",
            marker=dict(size=7, color=markers, line=dict(color="white", width=1.4)),
            showlegend=False,
            hovertemplate="USD/INR: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=rates,
            mode="lines",
            line=dict(color="rgba(15,23,42,.35)", width=1.8),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,.08)",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    y_min = min(rates) - 0.7
    y_max = max(rates) + 0.7
    fig.update_layout(
        margin=dict(l=10, r=10, t=8, b=8),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,.42)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,.24)", range=[y_min, y_max], tickformat=".2f"),
        hovermode="x unified",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


def status_badge(status: str) -> str:
    cls = {
        "paid": "status-paid",
        "overdue": "status-overdue",
        "partially_paid": "status-partial",
        "partially_matched": "status-partial",
        "pending": "status-pending",
        "matched": "status-paid",
    }.get(status, "status-pending")
    label = status.replace("_", " ")
    return f'<span class="status {cls}">{label}</span>'


def render_table(df: pd.DataFrame):
    formatted = df.copy()
    if "status" in formatted.columns:
        formatted["status"] = formatted["status"].astype(str).map(status_badge)
    st.markdown(f'<div class="table-wrap">{formatted.to_html(index=False, escape=False)}</div>', unsafe_allow_html=True)


def main():
    st.markdown(theme_css(), unsafe_allow_html=True)
    invoices, payments, reconciliation = build_demo_data()
    total_received, expected_7d, overdue_amount, risky_clients, invoices = compute_summary(invoices, payments)

    with st.sidebar:
        st.markdown('<div class="brand">Smart Cashflow MVP</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-pill active">Overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-pill">Reconciliation</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-pill">Forecasting</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-pill">Clients</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-pill">Settings</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="topbar"><span class="badge">Live • Export Intelligence</span><button class="btn-primary">New Invoice</button></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero">
          <span class="hero-kicker">Cash Flow Command Center</span>
          <h1 class="hero-title">Know exactly when your export cash lands.</h1>
          <p class="hero-sub">AI-SaaS style finance cockpit for payment matching, delay monitoring, and short-term inflow visibility.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3, gap="small")
    m1.markdown(f'<div class="card"><div class="label">Total Received</div><p class="value">{inr(total_received)}</p></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="card"><div class="label">Expected Inflow (Next 7d)</div><p class="value">{inr(expected_7d)}</p></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="card"><div class="label">Overdue Amount</div><p class="value">{inr(overdue_amount)}</p></div>', unsafe_allow_html=True)

    st.write("")
    c_left, c_right = st.columns([1.0, 2.1], gap="large")
    with c_left:
        st.markdown(
            """
            <div class="section">
              <div class="label">USD / INR</div>
              <p class="value" style="font-size:2rem;margin-top:.2rem;">92.53</p>
              <p class="muted">+0.84% this week</p>
              <p class="muted">Indicative live trend for settlement planning.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section" style="margin-top:.8rem;"><div class="section-title">Risk Watchlist</div>', unsafe_allow_html=True)
        if risky_clients:
            st.markdown("".join([f'<span class="risk-chip">{name}</span>' for name in risky_clients]), unsafe_allow_html=True)
        else:
            st.markdown('<p class="muted">No risky clients flagged.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c_right:
        st.markdown('<div class="section"><div class="section-title">Forex Rate Trend</div>', unsafe_allow_html=True)
        forex_chart()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    t1, t2 = st.columns(2, gap="large")
    with t1:
        st.markdown('<div class="section-title">Invoices</div>', unsafe_allow_html=True)
        iv = invoices[["invoice_number", "client_name", "due_date", "status", "amount_paid_base", "amount"]].copy()
        iv["due_date"] = pd.to_datetime(iv["due_date"]).dt.strftime("%Y-%m-%d")
        iv["amount_paid_base"] = iv["amount_paid_base"].map(inr)
        iv["amount"] = iv["amount"].map(inr)
        render_table(iv)
    with t2:
        st.markdown('<div class="section-title">Payments</div>', unsafe_allow_html=True)
        pv = payments[["payment_reference", "client_name", "payment_date", "source_currency", "net_amount_base"]].copy()
        pv["payment_date"] = pd.to_datetime(pv["payment_date"]).dt.strftime("%Y-%m-%d")
        pv["net_amount_base"] = pv["net_amount_base"].map(inr)
        render_table(pv)

    st.write("")
    st.markdown('<div class="section-title">Reconciliation Status</div>', unsafe_allow_html=True)
    rv = reconciliation.copy()
    rv["matched_amount_base"] = rv["matched_amount_base"].map(inr)
    rv["delta_amount_base"] = rv["delta_amount_base"].map(inr)
    render_table(rv)


if __name__ == "__main__":
    main()
