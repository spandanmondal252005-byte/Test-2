# GrowthPilot — Interactive Marketing Analytics

GrowthPilot lets a user explore synthetic demo data, upload a CSV, or enter marketing data manually.

## Input options
- **Try sample data:** clearly labelled synthetic data for demonstrations.
- **Upload my CSV:** required columns are `date`, `channel`, `sessions`, `purchases`, `revenue`. Optional columns include `ad_spend`, `device`, `landing_page`, `engaged_sessions`, `product_views`, `add_to_carts`, and `checkout_starts`. Use the in-app CSV template.
- **Enter data manually:** add daily/channel records in the form. Records remain in the current browser app session; download them as CSV to keep a copy.

## Run
`pip install -r requirements.txt`
`streamlit run app.py`

## Data and metric notes
All built-in sample data is synthetic. Revenue/spend use the currency provided by the user and are not converted. Conversion rate is purchases / sessions. Recommendations are descriptive prompts, not causal claims. Avoid uploading sensitive customer-level data.
