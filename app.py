import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from pathlib import Path

st.set_page_config(page_title="GrowthPilot | Marketing Analytics", page_icon="📈", layout="wide")

st.markdown("""
<style>
.main {background:#f7f9fc}
[data-testid="stMetric"] {background:white;padding:14px;border:1px solid #e6eaf0;border-radius:13px}
.hero {padding:22px 25px;border-radius:17px;background:linear-gradient(120deg,#111827,#243b63);color:white;margin-bottom:16px}
.hero h1 {color:white;margin:0}.hero p {color:#d7e3f7;margin:7px 0 0}
.notice {padding:12px 14px;background:#fff8e7;border:1px solid #f5d78e;border-radius:10px;color:#604b16}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📈 GrowthPilot</h1>
<p>Your marketing data, turned into decisions.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="notice"><b>Demo data notice:</b> If you have not uploaded your own CSV, the app uses clearly labelled synthetic example data. '
    'Upload your own marketing CSV or enter records manually to analyze your own data.</div>',
    unsafe_allow_html=True
)

REQUIRED = ["date", "channel", "sessions", "purchases", "revenue"]
OPTIONAL_DEFAULTS = {
    "device": "unknown",
    "landing_page": "(not provided)",
    "engaged_sessions": 0,
    "product_views": 0,
    "add_to_carts": 0,
    "checkout_starts": 0,
    "ad_spend": 0.0,
}

def sample_data():
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", periods=45, freq="D")
    channels = [
        ("Instagram Ads", 120, 0.028, 38, 0.18),
        ("Google Search", 85, 0.061, 55, 0.26),
        ("Email", 45, 0.075, 48, 0.00),
        ("Organic Search", 75, 0.047, 51, 0.00),
        ("Referral", 25, 0.036, 43, 0.00),
    ]
    rows = []
    for day in dates:
        for channel, avg_sessions, cvr, aov, spend_rate in channels:
            sessions = max(1, int(rng.poisson(avg_sessions * (1.12 if day.dayofweek >= 5 else 1))))
            purchases = int(rng.binomial(sessions, cvr * rng.uniform(.8, 1.2)))
            product_views = int(sessions * rng.uniform(1.2, 1.7))
            carts = int(product_views * rng.uniform(.07, .14))
            checkout = int(carts * rng.uniform(.45, .7))
            revenue = round(sum(rng.normal(aov, 7, purchases).clip(10, 150)), 2) if purchases else 0.0
            rows.append({
                "date": day, "channel": channel, "device": "all devices",
                "landing_page": "all landing pages", "sessions": sessions,
                "engaged_sessions": int(sessions * rng.uniform(.5, .72)),
                "product_views": product_views, "add_to_carts": carts,
                "checkout_starts": checkout, "purchases": purchases,
                "revenue": revenue, "ad_spend": round(sessions * spend_rate * rng.uniform(.9, 1.1), 2)
            })
    return pd.DataFrame(rows)

def normalize_data(raw):
    df = raw.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    aliases = {
        "date": ["day", "order_date", "report_date"],
        "channel": ["source", "marketing_channel", "source_medium", "campaign_source"],
        "sessions": ["visits", "website_visits", "traffic"],
        "purchases": ["orders", "conversions", "transactions"],
        "revenue": ["sales", "total_revenue", "purchase_revenue"],
        "ad_spend": ["spend", "marketing_spend", "cost"],
        "device": ["device_category", "platform"],
        "landing_page": ["page", "landingpage"],
    }
    for target, options in aliases.items():
        if target not in df.columns:
            for opt in options:
                if opt in df.columns:
                    df = df.rename(columns={opt: target})
                    break
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    for col, default in OPTIONAL_DEFAULTS.items():
        if col not in df.columns:
            df[col] = default
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["sessions", "purchases", "revenue", "ad_spend", "engaged_sessions", "product_views", "add_to_carts", "checkout_starts"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["channel", "device", "landing_page"]:
        df[col] = df[col].fillna("(not provided)").astype(str)
    df = df.dropna(subset=["date"])
    if df.empty:
        raise ValueError("No valid dates were found. Use dates like 2026-01-31.")
    if (df[["sessions", "purchases", "revenue", "ad_spend"]] < 0).any().any():
        raise ValueError("Sessions, purchases, revenue, and ad spend cannot be negative.")
    return df

if "user_records" not in st.session_state:
    st.session_state.user_records = pd.DataFrame(columns=[
        "date","channel","device","landing_page","sessions","engaged_sessions",
        "product_views","add_to_carts","checkout_starts","purchases","revenue","ad_spend"
    ])

with st.sidebar:
    st.header("Data source")
    source_mode = st.radio("Choose data", ["Try sample data", "Upload my CSV", "Enter data manually"])
    st.caption("Your uploaded file is processed by this app session. Don't upload confidential customer-level data.")

data = None
if source_mode == "Try sample data":
    data = sample_data()
    st.caption("Currently showing synthetic sample data.")
elif source_mode == "Upload my CSV":
    st.markdown("### Upload your marketing data")
    st.write("Upload a CSV file. Required columns: `date`, `channel`, `sessions`, `purchases`, `revenue`.")
    st.write("Optional: `device`, `landing_page`, `ad_spend`, `engaged_sessions`, `product_views`, `add_to_carts`, `checkout_starts`.")
    template = pd.DataFrame([{
        "date":"2026-01-01","channel":"Instagram Ads","sessions":100,"purchases":5,
        "revenue":250,"ad_spend":40,"device":"mobile","landing_page":"/products/example",
        "engaged_sessions":60,"product_views":120,"add_to_carts":15,"checkout_starts":8
    }])
    st.download_button("Download CSV template", template.to_csv(index=False).encode("utf-8"), "growthpilot_csv_template.csv", "text/csv")
    uploaded = st.file_uploader("Choose CSV file", type=["csv"])
    if uploaded is not None:
        try:
            data = normalize_data(pd.read_csv(uploaded))
            st.success(f"Loaded {len(data):,} rows from your CSV.")
        except Exception as e:
            st.error(f"Could not read this CSV: {e}")
            st.info("Download the template above, replace the example row with your own data, and upload it again.")
elif source_mode == "Enter data manually":
    st.markdown("### Add a marketing data record")
    st.write("Enter one row for a date and channel. You can add multiple records.")
    with st.form("add_record", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            record_date = st.date_input("Date")
            channel = st.selectbox("Marketing channel", ["Instagram Ads","Google Search","Organic Search","Email","Referral","Influencer","Other"])
            device = st.selectbox("Device", ["all devices","mobile","desktop","tablet"])
            sessions = st.number_input("Sessions / visits", min_value=0, value=100, step=1)
            purchases = st.number_input("Purchases / orders", min_value=0, value=5, step=1)
        with c2:
            revenue = st.number_input("Revenue (₹ or your chosen currency)", min_value=0.0, value=250.0, step=10.0)
            ad_spend = st.number_input("Ad spend (same currency; optional)", min_value=0.0, value=40.0, step=10.0)
            landing_page = st.text_input("Landing page (optional)", value="(not provided)")
            engaged_sessions = st.number_input("Engaged sessions (optional)", min_value=0, value=60, step=1)
        submitted = st.form_submit_button("Add record")
    if submitted:
        if purchases > sessions:
            st.error("Purchases cannot be greater than sessions for this simple record. Please check the values.")
        else:
            new_row = pd.DataFrame([{
                "date":pd.to_datetime(record_date), "channel":channel, "device":device,
                "landing_page":landing_page or "(not provided)", "sessions":sessions,
                "engaged_sessions":engaged_sessions, "product_views":0, "add_to_carts":0,
                "checkout_starts":0, "purchases":purchases, "revenue":revenue, "ad_spend":ad_spend
            }])
            st.session_state.user_records = pd.concat([st.session_state.user_records, new_row], ignore_index=True)
            st.success("Record added.")
    if not st.session_state.user_records.empty:
        st.markdown("#### Your manually entered records")
        st.dataframe(st.session_state.user_records, use_container_width=True, hide_index=True)
        data = st.session_state.user_records.copy()
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download my records as CSV", data.to_csv(index=False).encode("utf-8"), "my_growthpilot_data.csv", "text/csv")
        with col2:
            if st.button("Clear manually entered records"):
                st.session_state.user_records = st.session_state.user_records.iloc[0:0].copy()
                st.rerun()
    else:
        st.info("Add at least one record above to see your dashboard.")

if data is None or data.empty:
    st.stop()

# Standardize and calculate metrics for all modes
data = normalize_data(data)
sessions_total = int(data["sessions"].sum())
purchases_total = int(data["purchases"].sum())
revenue_total = float(data["revenue"].sum())
spend_total = float(data["ad_spend"].sum())
cvr_total = purchases_total / sessions_total * 100 if sessions_total else 0
aov = revenue_total / purchases_total if purchases_total else 0

st.divider()
st.subheader("Dashboard")
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Sessions", f"{sessions_total:,}")
k2.metric("Purchases", f"{purchases_total:,}")
k3.metric("Revenue", f"{revenue_total:,.2f}")
k4.metric("Conversion rate", f"{cvr_total:.2f}%")
k5.metric("Ad spend", f"{spend_total:,.2f}")
st.caption(f"Average order value: {aov:,.2f}. Revenue and spend use the currency and definitions in your input data; the app does not convert currencies.")

left, right = st.columns(2)
with left:
    daily = data.groupby("date", as_index=False).agg(revenue=("revenue","sum"))
    fig = px.line(daily, x="date", y="revenue", markers=True, title="Revenue over time")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
with right:
    by_channel = data.groupby("channel", as_index=False).agg(
        sessions=("sessions","sum"), purchases=("purchases","sum"), revenue=("revenue","sum"), ad_spend=("ad_spend","sum")
    )
    by_channel["conversion_rate"] = np.where(by_channel["sessions"] > 0, by_channel["purchases"]/by_channel["sessions"]*100, 0)
    fig = px.bar(by_channel.sort_values("revenue"), x="revenue", y="channel", orientation="h", title="Revenue by marketing channel")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Channel performance")
st.dataframe(by_channel.style.format({
    "revenue":"{:,.2f}", "ad_spend":"{:,.2f}", "conversion_rate":"{:.2f}%"
}), use_container_width=True, hide_index=True)

st.subheader("Growth insights")
if len(by_channel):
    high_volume = by_channel.sort_values("sessions", ascending=False).iloc[0]
    high_cvr = by_channel.sort_values("conversion_rate", ascending=False).iloc[0]
    low_cvr = by_channel.sort_values("conversion_rate", ascending=True).iloc[0]
    st.write(f"**Most traffic:** {high_volume['channel']} brings {int(high_volume['sessions']):,} sessions. Check whether that volume is producing enough purchases.")
    st.write(f"**Highest observed conversion:** {high_cvr['channel']} converts at {high_cvr['conversion_rate']:.2f}% in the data provided.")
    st.write(f"**Potential investigation:** {low_cvr['channel']} has the lowest observed conversion ({low_cvr['conversion_rate']:.2f}%). Review audience intent, landing page relevance, and device mix before making budget decisions.")
    st.caption("These are descriptive observations, not proof of cause. Validate tracking and compare like-for-like periods before changing budgets.")

st.subheader("Raw data")
st.dataframe(data, use_container_width=True, hide_index=True)
st.download_button("Download current data as CSV", data.to_csv(index=False).encode("utf-8"), "growthpilot_current_data.csv", "text/csv")
