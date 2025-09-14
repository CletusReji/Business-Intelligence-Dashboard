# pages/2_Campaign_Performance.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Campaign Performance", layout="wide")

# (Copy the same load_and_prepare_data function from your other pages here)
@st.cache_data
def load_and_prepare_data():
    try:
        df_facebook = pd.read_csv('Facebook.csv').rename(columns={'impression': 'impressions', 'attributed revenue': 'attributed_revenue'})
        df_google = pd.read_csv('Google.csv').rename(columns={'impression': 'impressions', 'attributed revenue': 'attributed_revenue'})
        df_tiktok = pd.read_csv('TikTok.csv').rename(columns={'impression': 'impressions', 'attributed revenue': 'attributed_revenue'})
        for df in [df_facebook, df_google, df_tiktok]:
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df_facebook['platform'] = 'Facebook'; df_google['platform'] = 'Google'; df_tiktok['platform'] = 'TikTok'
        df_marketing = pd.concat([df_facebook, df_google, df_tiktok], ignore_index=True)
        return df_marketing
    except Exception:
        return pd.DataFrame()

df_marketing_details = load_and_prepare_data()

st.title("🎯 Campaign Performance")
st.markdown("Drill down into the performance of individual marketing campaigns.")

if not df_marketing_details.empty:
    df_marketing_details['date'] = pd.to_datetime(df_marketing_details['date'])

    # --- FILTERS ---
    st.sidebar.header("Filters")
    min_date = df_marketing_details['date'].min().date()
    max_date = df_marketing_details['date'].max().date()
    date_range = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))

    # Platform selector to narrow down campaigns
    platform_list = ["All"] + df_marketing_details['platform'].unique().tolist()
    selected_platform = st.sidebar.selectbox("Select a Platform", platform_list)

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

        # Filter by date first
        mask = (df_marketing_details['date'] >= start_date) & (df_marketing_details['date'] <= end_date)
        df_filtered = df_marketing_details[mask]

        # Optional filter by platform
        if selected_platform != "All":
            df_filtered = df_filtered[df_filtered['platform'] == selected_platform]

        st.header(f"Campaign Breakdown for {selected_platform} Platform(s)")

        # --- Campaign Performance Table ---
        campaign_performance = df_filtered.groupby(['platform', 'campaign']).agg(
            spend=('spend', 'sum'),
            attributed_revenue=('attributed_revenue', 'sum'),
            clicks=('clicks', 'sum'),
            impressions=('impressions', 'sum')
        ).reset_index()

        campaign_performance['roas'] = (campaign_performance['attributed_revenue'] / campaign_performance['spend']).fillna(0)
        campaign_performance['cpc'] = (campaign_performance['spend'] / campaign_performance['clicks']).fillna(0)
        campaign_performance['ctr'] = (campaign_performance['clicks'] / campaign_performance['impressions'] * 100).fillna(0)

        st.dataframe(
            campaign_performance.sort_values('roas', ascending=False).style.format({
                'spend': '${:,.2f}',
                'attributed_revenue': '${:,.2f}',
                'roas': '{:.2f}x',
                'cpc': '${:,.2f}',
                'ctr': '{:.2f}%'
            })
        )

        st.download_button(
            label="📥 Download Campaign Data as CSV",
            data=campaign_performance.to_csv(index=False).encode('utf-8'),
            file_name='campaign_data.csv',
            mime='text/csv',
        )