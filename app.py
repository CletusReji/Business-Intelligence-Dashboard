# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Executive Overview",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA LOADING AND PREPARATION ---
@st.cache_data
def load_and_prepare_data():
    # (The data loading function is the same as our last version.
    #  For brevity, I am omitting the full code, but you should use the
    #  complete, working function that correctly renames all columns.)
    try:
        df_facebook = pd.read_csv('Facebook.csv').rename(columns={'impression': 'impressions', 'attributed revenue': 'attributed_revenue'})
        df_google = pd.read_csv('Google.csv').rename(columns={'impression': 'impressions', 'attributed revenue': 'attributed_revenue'})
        df_tiktok = pd.read_csv('TikTok.csv').rename(columns={'impression': 'impressions', 'attributed revenue': 'attributed_revenue'})
        df_business = pd.read_csv('Business.csv').rename(columns={'# of orders': 'orders', '# of new orders': 'new_orders', 'new customers': 'new_customers', 'total revenue': 'total_revenue', 'gross profit': 'gross_profit'})
        for df in [df_facebook, df_google, df_tiktok, df_business]:
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df_facebook['platform'] = 'Facebook'; df_google['platform'] = 'Google'; df_tiktok['platform'] = 'TikTok'
        df_marketing = pd.concat([df_facebook, df_google, df_tiktok], ignore_index=True)
        df_marketing['date'] = pd.to_datetime(df_marketing['date']); df_business['date'] = pd.to_datetime(df_business['date'])
        df_marketing_daily = df_marketing.groupby('date').agg({'spend': 'sum', 'impressions': 'sum', 'clicks': 'sum', 'attributed_revenue': 'sum'}).reset_index()
        df_merged = pd.merge(df_business, df_marketing_daily, on='date', how='left')
        for col in ['spend', 'impressions', 'clicks', 'attributed_revenue']: df_merged[col] = df_merged[col].fillna(0)
        df_merged['roas'] = (df_merged['attributed_revenue'] / df_merged['spend']).fillna(0)
        df_merged['cpc'] = (df_merged['spend'] / df_merged['clicks']).fillna(0)
        df_merged['ctr'] = (df_merged['clicks'] / df_merged['impressions'] * 100).fillna(0)
        df_merged['cpo'] = (df_merged['spend'] / df_merged['orders']).fillna(0)
        return df_merged, df_marketing
    except Exception:
        st.error("Error loading data. Please ensure all CSV files are present and correctly formatted.")
        return pd.DataFrame(), pd.DataFrame()


# --- HELPER FUNCTIONS ---
def get_key_insights(marketing_data):
    """Generates a text summary of key marketing insights."""
    if marketing_data.empty:
        return "No data available for insights."
    
    platform_perf = marketing_data.groupby('platform').agg({'spend': 'sum', 'attributed_revenue': 'sum'}).reset_index()
    platform_perf['roas'] = (platform_perf['attributed_revenue'] / platform_perf['spend']).fillna(0)
    
    if platform_perf.empty:
        return "Not enough data for platform comparison."

    best_platform = platform_perf.loc[platform_perf['roas'].idxmax()]
    worst_platform = platform_perf.loc[platform_perf['roas'].idxmin()]

    insight1 = f"🚀 **Top Performer**: **{best_platform['platform']}** is driving the highest return with a **{best_platform['roas']:.2f}x ROAS**."
    insight2 = f"📉 **Area for Review**: **{worst_platform['platform']}** shows the lowest efficiency with a **{worst_platform['roas']:.2f}x ROAS**."
    
    return f"{insight1}\n{insight2}"

# --- MAIN APP ---
df_daily_performance, df_marketing_details = load_and_prepare_data()

st.title("🏠 Executive Overview")
st.markdown("High-level metrics for overall business and marketing performance.")

if not df_daily_performance.empty:
    # --- FILTERS ---
    st.sidebar.header("Filters")
    min_date = df_daily_performance['date'].min().date()
    max_date = df_daily_performance['date'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        
        # --- DATA FILTERING ---
        df_filtered = df_daily_performance[(df_daily_performance['date'] >= start_date) & (df_daily_performance['date'] <= end_date)]
        df_marketing_filtered = df_marketing_details[(df_marketing_details['date'] >= start_date) & (df_marketing_details['date'] <= end_date)]

        # --- KEY INSIGHTS SECTION ---
        st.header("💡 Key Insights")
        with st.expander("See automated summary", expanded=True):
            st.markdown(get_key_insights(df_marketing_filtered))

        # --- KPI SECTION WITH CONDITIONAL FORMATTING ---
        st.header("Overall Performance Snapshot")
        
        # Calculate previous period for comparison
        period_duration = end_date - start_date
        prev_start_date = start_date - period_duration - timedelta(days=1)
        prev_end_date = end_date - period_duration - timedelta(days=1)
        df_previous = df_daily_performance[(df_daily_performance['date'] >= prev_start_date) & (df_daily_performance['date'] <= prev_end_date)]

        # Current period metrics
        total_revenue = df_filtered['total_revenue'].sum()
        total_spend = df_filtered['spend'].sum()
        total_profit = df_filtered['gross_profit'].sum()
        overall_roas = (df_filtered['attributed_revenue'].sum() / total_spend) if total_spend > 0 else 0
        
        # Previous period metrics
        prev_revenue = df_previous['total_revenue'].sum()
        prev_spend = df_previous['spend'].sum()
        prev_profit = df_previous['gross_profit'].sum()
        prev_roas = (df_previous['attributed_revenue'].sum() / prev_spend) if prev_spend > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Revenue", f"${total_revenue:,.0f}", f"{total_revenue - prev_revenue:,.0f}", help="Total revenue from all orders.")
        col2.metric("Gross Profit", f"${total_profit:,.0f}", f"{total_profit - prev_profit:,.0f}", help="Total Revenue minus Cost of Goods Sold.")
        col3.metric("Total Ad Spend", f"${total_spend:,.0f}", f"{total_spend - prev_spend:,.0f}", delta_color="inverse")
        col4.metric("Overall ROAS", f"{overall_roas:.2f}x", f"{overall_roas - prev_roas:.2f}x", help="Return on Ad Spend = (Attributed Revenue / Ad Spend)")

        # --- CHARTS ---
        st.header("Performance Over Time")
        fig_revenue_spend = px.line(
            df_filtered, x='date', y=['total_revenue', 'spend', 'gross_profit'],
            title='Daily Revenue, Spend, and Profit', labels={'value': 'Amount (USD)', 'date': 'Date'}
        )
        st.plotly_chart(fig_revenue_spend, use_container_width=True)

        # --- DATA EXPORT ---
        st.header("Raw Data")
        st.dataframe(df_filtered)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=df_filtered.to_csv(index=False).encode('utf-8'),
            file_name='overview_data.csv',
            mime='text/csv',
        )