# pages/1_Channel_Deep_Dive.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Channel Deep Dive",
    layout="wide"
)

# --- DATA LOADING (Same function as app.py) ---
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

# --- HELPER FUNCTIONS ---
def get_channel_insights(df, platform):
    """Generates insights for a specific channel."""
    if df.empty: return "No data for insights."
    tactic_perf = df.groupby('tactic').agg({'spend': 'sum', 'attributed_revenue': 'sum'}).reset_index()
    tactic_perf['roas'] = (tactic_perf['attributed_revenue'] / tactic_perf['spend']).fillna(0)
    if tactic_perf.empty or tactic_perf['roas'].max() == 0: return "Not enough data for tactic comparison."
    best_tactic = tactic_perf.loc[tactic_perf['roas'].idxmax()]
    return f"On **{platform}**, the **'{best_tactic['tactic']}'** tactic is the most efficient, with a **{best_tactic['roas']:.2f}x ROAS**."

# --- MAIN APP ---
df_marketing_details = load_and_prepare_data()

st.title("📊 Channel Deep Dive")
st.markdown("Analyze the performance of individual marketing channels, tactics, and states.")

if not df_marketing_details.empty:
    df_marketing_details['date'] = pd.to_datetime(df_marketing_details['date'])

    # --- Calculate ROAS for the DataFrame ---
    df_marketing_details['roas'] = (df_marketing_details['attributed_revenue'] / df_marketing_details['spend']).fillna(0)
    
    # --- FILTERS ---
    st.sidebar.header("Filters")
    min_date = df_marketing_details['date'].min().date()
    max_date = df_marketing_details['date'].max().date()
    date_range = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))
    
    all_platforms = df_marketing_details['platform'].unique()
    selected_platform = st.sidebar.selectbox("Select a Platform", all_platforms)
    
    target_roas = st.sidebar.number_input("Set Target ROAS", value=3.0, step=0.1)

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask = ((df_marketing_details['date'] >= start_date) & (df_marketing_details['date'] <= end_date) & (df_marketing_details['platform'] == selected_platform))
        df_filtered = df_marketing_details[mask]

        st.header(f"Performance for {selected_platform}")

        with st.expander("See automated summary", expanded=True):
            st.markdown(get_channel_insights(df_filtered, selected_platform))
        
        # --- KPIs ---
        col1, col2, col3, col4 = st.columns(4)
        spend = df_filtered['spend'].sum()
        revenue = df_filtered['attributed_revenue'].sum()
        roas_kpi = (revenue / spend) if spend > 0 else 0
        clicks = df_filtered['clicks'].sum()
        col1.metric("Total Spend", f"${spend:,.0f}")
        col2.metric("Attributed Revenue", f"${revenue:,.0f}")
        col3.metric("Channel ROAS", f"{roas_kpi:.2f}x")
        col4.metric("Total Clicks", f"{clicks:,}")

        # --- DAILY TRENDS FOR SELECTED CHANNEL ---
        st.header(f"Daily Trends for {selected_platform}")
        daily_perf = df_filtered.groupby('date').agg({
            'spend': 'sum',
            'attributed_revenue': 'sum'
        }).reset_index()

        fig_daily_trend = px.line(
            daily_perf,
            x='date',
            y=['spend', 'attributed_revenue'],
            title=f'Daily Spend and Revenue for {selected_platform}',
            labels={'value': 'Amount (USD)', 'date': 'Date'}
        )
        st.plotly_chart(fig_daily_trend, use_container_width=True)
        
        # --- BREAKDOWNS WITH TARGET LINE ---
        st.header("Performance Breakdowns")
        c1, c2 = st.columns(2)
        
        tactic_performance = df_filtered.groupby('tactic').agg({'spend': 'sum', 'attributed_revenue': 'sum'}).reset_index()
        tactic_performance['roas'] = (tactic_performance['attributed_revenue'] / tactic_performance['spend']).fillna(0)
        fig_tactic = px.bar(tactic_performance, x='tactic', y='roas', color='spend', title=f"ROAS by Tactic", labels={'roas': 'ROAS', 'spend': 'Spend'})
        fig_tactic.add_hline(y=target_roas, line_dash="dot", annotation_text="Target ROAS", annotation_position="bottom right")
        c1.plotly_chart(fig_tactic, use_container_width=True)

        state_performance = df_filtered.groupby('state').agg({'spend': 'sum', 'attributed_revenue': 'sum'}).reset_index()
        state_performance['roas'] = (state_performance['attributed_revenue'] / state_performance['spend']).fillna(0)
        fig_state = px.bar(state_performance, x='state', y='roas', color='spend', title=f"ROAS by State", labels={'roas': 'ROAS', 'spend': 'Spend'})
        fig_state.add_hline(y=target_roas, line_dash="dot", annotation_text="Target ROAS", annotation_position="bottom right")
        c2.plotly_chart(fig_state, use_container_width=True)

        # --- GEOSPATIAL ANALYSIS ---
        st.header(f"Geospatial Performance for {selected_platform}")
        state_performance_map = df_filtered.groupby('state').agg(
            spend=('spend', 'sum'),
            roas=('roas', 'mean')
        ).reset_index()
        fig_map = px.choropleth(
            state_performance_map,
            locations='state',
            locationmode="USA-states",
            color='roas',
            hover_name='state',
            hover_data=['spend'],
            color_continuous_scale="Viridis",
            scope="usa",
            title="Average ROAS by State"
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # --- FUNNEL ANALYSIS ---
        st.header(f"Marketing Funnel for {selected_platform}")
        total_impressions = df_filtered['impressions'].sum()
        total_clicks = df_filtered['clicks'].sum()

        if total_impressions > 0 and total_clicks > 0:
            funnel_data = dict(
                number=[total_impressions, total_clicks],
                stage=["Impressions", "Clicks"]
            )
            fig_funnel = px.funnel(funnel_data, x='number', y='stage', title=f"Impression-to-Click Funnel on {selected_platform}")
            st.plotly_chart(fig_funnel, use_container_width=True)
        else:
            st.warning("Not enough data to build a funnel chart for the selected period.")

        # --- DATA EXPORT ---
        st.header("Filtered Channel Data")
        st.dataframe(df_filtered)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=df_filtered.to_csv(index=False).encode('utf-8'),
            file_name=f'{selected_platform}_data.csv',
            mime='text/csv',
        )