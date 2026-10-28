import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="GrowthPilot | Marketing Analytics", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f7f9fc;}
    [data-testid="stMetric"] {background: white; padding: 16px 18px; border: 1px solid #e6eaf0; border-radius: 14px;}
    .hero {padding: 22px 26px; border-radius: 18px; background: linear-gradient(120deg,#111827,#243b63); color: white; margin-bottom: 18px;}
    .hero h1 {margin: 0; color: white; font-size: 2.1rem;}
    .hero p {margin: 8px 0 0 0; color: #d7e3f7;}
    .note {padding: 12px 14px; background: #fff8e7; border: 1px solid #f5d78e; border-radius: 10px; color: #604b16;}
    .insight {padding: 15px 17px; border: 1px solid #e6eaf0; background: white; border-radius: 13px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "growthpilot_synthetic_data.csv"

@st.cache_data
def load_data():
    # If the CSV is present, use it. Otherwise generate illustrative data so
    # the app can be deployed with app.py and requirements.txt alone.
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates=["date"])

    import numpy as np
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", periods=90, freq="D")
    channel_cfg = {
        "Instagram Ads": (150, 0.026, 42, 0.18),
        "Google Search": (105, 0.062, 58, 0.28),
        "Email": (55, 0.075, 49, 0.00),
        "Organic Search": (90, 0.048, 54, 0.00),
        "Referral": (30, 0.035, 46, 0.00),
    }
    device_names = ["mobile", "desktop", "tablet"]
    device_weights = [0.68, 0.27, 0.05]
    pages = ["/", "/collections/new", "/products/classic-tee", "/collections/bestsellers"]
    page_weights = [0.25, 0.24, 0.31, 0.20]
    output = []
    for date in dates:
        weekend_factor = 1.12 if date.dayofweek in [5, 6] else 1.0
        seasonal_factor = 1 + 0.10 * np.sin((date.dayofyear / 90) * 2 * np.pi)
        for channel, (base_sessions, base_cvr, aov, spend_rate) in channel_cfg.items():
            for di, device in enumerate(device_names):
                for pi, page in enumerate(pages):
                    sessions = max(1, int(rng.poisson(base_sessions * device_weights[di] * page_weights[pi] * weekend_factor * seasonal_factor)))
                    device_factor = {"mobile": 0.78, "desktop": 1.35, "tablet": 0.88}[device]
                    page_factor = {"/": 0.85, "/collections/new": 0.92, "/products/classic-tee": 1.18, "/collections/bestsellers": 1.10}[page]
                    cvr = min(base_cvr * device_factor * page_factor * rng.uniform(0.83, 1.17), 0.35)
                    purchases = min(sessions, int(rng.binomial(sessions, cvr)))
                    engaged = min(sessions, int(rng.binomial(sessions, {"mobile": 0.56, "desktop": 0.68, "tablet": 0.60}[device])))
                    product_views = int(sessions * rng.uniform(1.1, 1.8))
                    add_to_carts = min(product_views, int(rng.binomial(max(product_views, 1), 0.11 * page_factor)))
                    checkout_starts = min(add_to_carts, int(rng.binomial(max(add_to_carts, 1), 0.56)))
                    revenue = round(float(np.clip(rng.normal(aov, 8, size=purchases), 10, 150).sum()), 2) if purchases else 0.0
                    ad_spend = round(sessions * spend_rate * rng.uniform(0.88, 1.12), 2)
                    output.append({
                        "date": date, "channel": channel, "device": device, "landing_page": page,
                        "sessions": sessions, "engaged_sessions": engaged, "product_views": product_views,
                        "add_to_carts": add_to_carts, "checkout_starts": checkout_starts,
                        "purchases": purchases, "revenue": revenue, "ad_spend": ad_spend,
                    })
    return pd.DataFrame(output)

df = load_data()

st.markdown("""
<div class="hero">
  <h1>📈 GrowthPilot</h1>
  <p>Marketing performance, conversion insights, and prioritized growth experiments.</p>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="note"><b>Portfolio demo:</b> This dashboard uses entirely synthetic, illustrative ecommerce data. It is not real company or Google Analytics data. Do not present its example findings as real-world results.</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("Explore the data")
st.sidebar.caption("Adjust filters to update the dashboard.")
min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date = end_date = pd.to_datetime(date_range)
channels = sorted(df["channel"].unique())
selected_channels = st.sidebar.multiselect("Marketing channels", channels, default=channels)
devices = sorted(df["device"].unique())
selected_devices = st.sidebar.multiselect("Devices", devices, default=devices)
pages = sorted(df["landing_page"].unique())
selected_pages = st.sidebar.multiselect("Landing pages", pages, default=pages)

filtered = df[
    df["date"].between(start_date, end_date)
    & df["channel"].isin(selected_channels)
    & df["device"].isin(selected_devices)
    & df["landing_page"].isin(selected_pages)
].copy()

if filtered.empty:
    st.warning("No rows match those filters. Choose at least one channel, device, and landing page.")
    st.stop()

sessions = int(filtered["sessions"].sum())
engaged = int(filtered["engaged_sessions"].sum())
purchases = int(filtered["purchases"].sum())
revenue = float(filtered["revenue"].sum())
spend = float(filtered["ad_spend"].sum())
conversion = purchases / sessions * 100 if sessions else 0
engagement = engaged / sessions * 100 if sessions else 0
roas = revenue / spend if spend > 0 else None
aov = revenue / purchases if purchases else 0

st.subheader("Performance overview")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Sessions", f"{sessions:,}")
m2.metric("Purchases", f"{purchases:,}")
m3.metric("Revenue", f"${revenue:,.0f}")
m4.metric("Purchase conversion", f"{conversion:.2f}%")
m5.metric("Ad spend", f"${spend:,.0f}")
st.caption(f"Engagement rate: {engagement:.1f}%  •  Average order value: ${aov:.2f}  •  Blended revenue / tracked ad spend: {f'{roas:.2f}x' if roas is not None else 'N/A'}")
st.caption("ROAS-like ratio is only an illustrative blended ratio: the dataset uses synthetic ad spend and includes revenue from organic channels, so it should not be treated as channel-attributed ROAS.")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Acquisition", "Conversion funnel", "Growth actions"])

with tab1:
    left, right = st.columns([1.45, 1])
    with left:
        daily = filtered.groupby("date", as_index=False).agg(revenue=("revenue","sum"), sessions=("sessions","sum"))
        fig = px.line(daily, x="date", y="revenue", markers=False, title="Revenue trend", labels={"date":"Date","revenue":"Revenue ($)"})
        fig.update_layout(margin=dict(l=10,r=10,t=55,b=10), plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        channel_summary = filtered.groupby("channel", as_index=False).agg(revenue=("revenue","sum"), purchases=("purchases","sum"))
        fig = px.bar(channel_summary.sort_values("revenue"), x="revenue", y="channel", orientation="h", title="Revenue by channel", labels={"revenue":"Revenue ($)","channel":"Channel"})
        fig.update_layout(margin=dict(l=10,r=10,t=55,b=10), plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Data preview")
    st.dataframe(filtered.head(20), use_container_width=True, hide_index=True)

with tab2:
    by_channel = filtered.groupby("channel", as_index=False).agg(
        sessions=("sessions","sum"), engaged_sessions=("engaged_sessions","sum"),
        purchases=("purchases","sum"), revenue=("revenue","sum"), ad_spend=("ad_spend","sum")
    )
    by_channel["conversion_rate_pct"] = (by_channel["purchases"] / by_channel["sessions"].replace(0, pd.NA) * 100).fillna(0)
    by_channel["revenue_per_session"] = (by_channel["revenue"] / by_channel["sessions"].replace(0, pd.NA)).fillna(0)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(by_channel.sort_values("sessions"), x="sessions", y="channel", orientation="h", title="Sessions by channel", labels={"sessions":"Sessions","channel":"Channel"})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(by_channel.sort_values("conversion_rate_pct"), x="conversion_rate_pct", y="channel", orientation="h", title="Purchase conversion by channel", labels={"conversion_rate_pct":"Conversion rate (%)","channel":"Channel"})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Channel scorecard")
    st.dataframe(by_channel.style.format({"revenue":"${:,.2f}","ad_spend":"${:,.2f}","conversion_rate_pct":"{:.2f}%","revenue_per_session":"${:.2f}"}), use_container_width=True, hide_index=True)
    st.info("Interpretation tip: volume is not the same as quality. Compare conversion and revenue per session alongside sessions.")

with tab3:
    funnel = filtered[["product_views","add_to_carts","checkout_starts","purchases"]].sum().reset_index()
    funnel.columns = ["stage_key","events"]
    label_map = {"product_views":"Product views","add_to_carts":"Add to cart","checkout_starts":"Checkout started","purchases":"Purchases"}
    funnel["stage"] = funnel["stage_key"].map(label_map)
    funnel = funnel[["stage","events"]]
    fig = px.funnel(funnel, x="events", y="stage", title="Event-stage volume (not a user-level cohort funnel)", labels={"events":"Recorded events","stage":"Stage"})
    fig.update_layout(margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This chart compares event counts aggregated across rows. It is not a strict funnel of the same users, and event counts can exceed sessions.")
    device_summary = filtered.groupby("device", as_index=False).agg(sessions=("sessions","sum"), purchases=("purchases","sum"))
    device_summary["conversion_rate_pct"] = (device_summary["purchases"] / device_summary["sessions"].replace(0, pd.NA) * 100).fillna(0)
    fig = px.bar(device_summary, x="device", y="conversion_rate_pct", title="Purchase conversion by device", labels={"device":"Device","conversion_rate_pct":"Conversion rate (%)"})
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    by_channel = filtered.groupby("channel", as_index=False).agg(sessions=("sessions","sum"), purchases=("purchases","sum"), revenue=("revenue","sum"))
    by_channel["conversion_rate_pct"] = (by_channel["purchases"] / by_channel["sessions"].replace(0, pd.NA) * 100).fillna(0)
    top_volume = by_channel.sort_values("sessions", ascending=False).iloc[0]
    top_cvr = by_channel.sort_values("conversion_rate_pct", ascending=False).iloc[0]
    low_cvr = by_channel.sort_values("conversion_rate_pct", ascending=True).iloc[0]
    st.markdown("### What the current filters suggest")
    st.markdown(f'<div class="insight"><b>1. Highest traffic volume:</b> {top_volume["channel"]} has {int(top_volume["sessions"]):,} sessions. Check whether that traffic is translating into purchases.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight"><b>2. Highest observed conversion:</b> {top_cvr["channel"]} converts at {top_cvr["conversion_rate_pct"]:.2f}% in this filtered sample. Investigate what differs about its audience and journey before reallocating budget.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight"><b>3. Conversion investigation candidate:</b> {low_cvr["channel"]} has the lowest observed conversion ({low_cvr["conversion_rate_pct"]:.2f}%). Review landing page relevance, device mix and traffic intent.</div>', unsafe_allow_html=True)
    st.markdown("### Experiment backlog")
    experiments = pd.DataFrame([
        {"Experiment":"Improve mobile product-page clarity","Hypothesis":"Clearer product details and stronger calls to action may reduce friction.","Primary metric":"Mobile purchase conversion rate","Effort":"Medium","Priority":"High"},
        {"Experiment":"Match ad creative to landing page","Hypothesis":"Closer message match may improve visitor intent and conversion.","Primary metric":"Landing-page purchase conversion rate","Effort":"Medium","Priority":"High"},
        {"Experiment":"Test an email reactivation segment","Hypothesis":"A relevant offer to inactive customers may increase returning purchases.","Primary metric":"Incremental purchases vs. control","Effort":"Low","Priority":"Medium"},
    ])
    st.dataframe(experiments, use_container_width=True, hide_index=True)
    st.caption("Recommendations are hypotheses to validate, not proven causes or guaranteed results.")

st.sidebar.divider()
st.sidebar.download_button(
    "Download filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="growthpilot_filtered_data.csv",
    mime="text/csv",
    use_container_width=True
)
st.sidebar.caption("GrowthPilot portfolio demo • Synthetic data • Not for business decisions")
