# GrowthPilot — Marketing Analytics Portfolio Project

GrowthPilot is a beginner-friendly marketing analytics dashboard for exploring ecommerce acquisition, conversion, revenue, device performance, and potential growth experiments.

## Important data notice

**All data included in this repository is synthetic and illustrative.** It is generated for demonstration and learning only. It is not Google Analytics data, real business performance, or evidence that any channel or experiment actually performs as shown. Do not present the sample findings as real-world results.

## Features

- KPI overview: sessions, purchases, revenue, conversion, ad spend
- Date, channel, device, and landing-page filters
- Revenue trend and channel comparison
- Acquisition scorecard including conversion rate and revenue per session
- Event-stage volume chart and device conversion comparison
- Automatically generated observations based on the current filters
- Experiment backlog with hypotheses, metrics, effort, and priority
- CSV download of the filtered dataset

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (optional but recommended).

   Windows:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Launch the app:
   ```bash
   streamlit run app.py
   ```

Streamlit will show a local address to open in your browser.

## Project structure

```text
GrowthPilot/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── growthpilot_synthetic_data.csv
```

## Metrics and caveats

- Purchase conversion rate = purchases / sessions. The data is synthetic and aggregated.
- Revenue per session = revenue / sessions.
- The displayed blended revenue / tracked ad spend ratio is **not channel-attributed ROAS**. Revenue includes organic sources and the ad-spend field is synthetic.
- The funnel chart shows aggregated event-stage counts, not a user-level cohort funnel.
- Session counts are generated at an aggregate grain. They should not be treated as production analytics.
- Recommendations are hypotheses to test, not causal conclusions.

## Suggested portfolio case-study outline

1. Business question: how can an ecommerce team compare marketing channel volume and conversion?
2. Dataset: synthetic, 90 days, channel/device/landing-page aggregates.
3. Method: clean data, calculate KPIs, compare segments, inspect funnel event counts.
4. Findings: insert only findings you verify by interacting with the dashboard; clearly label them as synthetic-data observations.
5. Recommendations: describe hypotheses, test design, primary metric, guardrail metric, and limitations.
6. Next steps: replace synthetic data with a properly permissioned real dataset, add channel-level cost and attribution, and evaluate experiments with controls.

## Recruiter demo (2 minutes)

- 0:00–0:20 — State the marketing problem and disclose the synthetic dataset.
- 0:20–0:50 — Show the KPI overview and filter controls.
- 0:50–1:20 — Compare channels and devices; explain conversion rate.
- 1:20–1:45 — Show the experiment backlog and explain how you would test a hypothesis.
- 1:45–2:00 — Discuss limitations and what data you would add next.

## Resume bullet template

**GrowthPilot — Ecommerce Marketing Analytics Dashboard**
- Built an interactive dashboard with Streamlit and Plotly to explore acquisition, conversion, revenue, device performance, and growth experiment ideas.
- Created segment-level KPIs and filterable charts, documented metric definitions, and surfaced hypotheses for marketing experiments.
- Used synthetic demonstration data; documented limitations and the additional real-world data required for valid budget and attribution decisions.

Only list skills and outcomes you can explain and reproduce yourself.
