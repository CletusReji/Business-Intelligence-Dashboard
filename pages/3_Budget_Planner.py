# pages/3_Budget_Planner.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Budget Planner", layout="wide")

# (Copy the same load_and_prepare_data function from your other pages here)
@st.cache_data
def load_and_prepare_data():
    try:
        # Load and combine all marketing data
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

st.title("💰 Budget Scenario Planner")
st.markdown("Use historical performance to project outcomes with a hypothetical budget.")

if not df_marketing_details.empty:
    # --- CALCULATE HISTORICAL ROAS ---
    platform_avg_roas = df_marketing_details.groupby('platform').agg(
        total_spend=('spend', 'sum'),
        total_revenue=('attributed_revenue', 'sum')
    ).reset_index()
    platform_avg_roas['avg_roas'] = (platform_avg_roas['total_revenue'] / platform_avg_roas['total_spend']).fillna(0)

    st.sidebar.header("Budget Allocation")
    total_budget = st.sidebar.number_input("Enter Total Budget to Allocate", min_value=1000, value=50000, step=1000)

    platforms = platform_avg_roas['platform'].unique()
    budget_allocations = {}
    
    for platform in platforms:
        avg_roas = platform_avg_roas[platform_avg_roas['platform'] == platform]['avg_roas'].iloc[0]
        budget_allocations[platform] = st.sidebar.slider(
            f"Budget for {platform} (Avg. ROAS: {avg_roas:.2f}x)",
            min_value=0,
            max_value=total_budget,
            value=int(total_budget / len(platforms)), # Distribute evenly by default
            step=100
        )
    
    allocated_budget = sum(budget_allocations.values())
    
    if allocated_budget > total_budget:
        st.sidebar.error(f"Allocated budget (${allocated_budget:,.0f}) exceeds total budget (${total_budget:,.0f}).")
    else:
        st.sidebar.success(f"Remaining budget: ${total_budget - allocated_budget:,.0f}")

    # --- PROJECTED RESULTS ---
    st.header("Projected Performance")
    
    projection_data = []
    for platform, spend in budget_allocations.items():
        avg_roas = platform_avg_roas[platform_avg_roas['platform'] == platform]['avg_roas'].iloc[0]
        projected_revenue = spend * avg_roas
        projection_data.append({'Platform': platform, 'Projected Spend': spend, 'Projected Revenue': projected_revenue})
    
    df_projection = pd.DataFrame(projection_data)

    total_projected_revenue = df_projection['Projected Revenue'].sum()
    total_projected_roas = (total_projected_revenue / allocated_budget) if allocated_budget > 0 else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Total Projected Revenue", f"${total_projected_revenue:,.0f}")
    col2.metric("Projected ROAS", f"{total_projected_roas:.2f}x")

    fig = px.bar(
        df_projection,
        x='Platform',
        y='Projected Revenue',
        color='Platform',
        title="Projected Revenue by Platform"
    )
    st.plotly_chart(fig, use_container_width=True)