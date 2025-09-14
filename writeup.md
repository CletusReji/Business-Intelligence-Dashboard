# Project Write-up: Marketing Intelligence Dashboard

---

## 1. Project Objective

The goal of this project was to design, build, and host an interactive BI dashboard to help a business stakeholder understand the connection between marketing activities and business outcomes. The dashboard ingests daily marketing data from Facebook, Google, and TikTok, along with daily business performance data, to provide a comprehensive and actionable view of performance.

---

## 2. Technical Execution

My approach to the technical execution focused on creating a clean, reliable, and efficient data pipeline within the Python script.

* **Data Loading & Cleaning**: All four CSV files were loaded using Pandas. I implemented a robust data preparation function that standardizes all column names (e.g., converting to lowercase, replacing spaces with underscores) to prevent case-sensitivity and formatting errors.
* **Data Transformation & Merging**: The three individual marketing datasets were first combined into a single marketing DataFrame. This dataset was then aggregated to a daily level to match the granularity of the business data. Finally, the aggregated marketing data was joined with the business data using a left merge on the `date` column to create a unified, daily performance view.
* **Derived Metrics**: To move beyond surface-level reporting, I created several key metrics that are critical for business analysis but not present in the original data. These include:
    * **Return on Ad Spend (ROAS)**: `attributed_revenue / spend`
    * **Customer Acquisition Cost (CAC)**: `spend / new_customers`
    * **Cost Per Click (CPC)**: `spend / clicks`
    * **Click-Through Rate (CTR)**: `(clicks / impressions) * 100`

---

## 3. Visualization & Storytelling

The dashboard was designed as a multi-page Streamlit application to tell a coherent story, guiding the user from a high-level overview to granular details.

* **Homepage (Executive Overview)**: This page serves as a "30-second summary" for a busy executive. It immediately presents the most critical KPIs with comparison deltas to the previous period, providing instant context on performance trends. The use of donut charts for spend vs. revenue provides an intuitive visual for proportional analysis.
* **Channel Deep Dive**: This page allows for a more focused analysis of a specific marketing platform. The use of bar charts for tactic/state breakdowns, a geospatial map, and a marketing funnel visualization provides multiple lenses through which to analyze channel effectiveness.
* **Product Thinking**: I designed the dashboard with a "top-down" approach, anticipating the questions a decision-maker would ask.
    * **"How are we doing overall?"** is answered by the homepage KPIs.
    * **"Which channel is driving our performance?"** is answered by the Channel Deep Dive page.
    * **"Which specific campaigns should I invest more in?"** is answered by the Campaign Performance page.
    * **"If I have more budget, where should I put it?"** is answered by the interactive Budget Scenario Planner.

By creating features like the automated "Key Insights" summary and the "What-If" budget planner, the dashboard proactively guides users toward actionable conclusions, rather than simply presenting raw data.

---

## 4. Final Deliverable

The final project is a hosted, multi-page Streamlit application that is clean, interactive, and user-friendly.

This project successfully integrates data from disparate sources into a single, coherent narrative, providing a valuable tool for strategic business decision-making.