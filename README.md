# Marketing Intelligence Dashboard

This project is an interactive Business Intelligence (BI) dashboard built with Python and Streamlit. It analyzes marketing campaign data from multiple platforms (Facebook, Google, TikTok) and connects it to core business performance metrics to provide actionable insights for decision-makers.

The live dashboard can be accessed here: `https://cletus-business-intelligence-dashboard.streamlit.app/`

---

## 📊 Features

This dashboard is structured as a multi-page Streamlit application to cater to different levels of analysis:

* **🏠 Executive Overview**: A high-level summary of overall business health, featuring key performance indicators (KPIs) like Total Revenue, Gross Profit, Customer Acquisition Cost (CAC), and overall Return on Ad Spend (ROAS). It includes trend charts and automated insights.
* **📊 Channel Deep Dive**: A detailed analysis of individual marketing platforms. Users can filter by platform and date to view performance breakdowns by marketing tactic and state, visualize data on a US map, and track performance against a set target.
* **🎯 Campaign Performance**: A granular view of all individual marketing campaigns, allowing managers to identify top and bottom-performing campaigns based on metrics like ROAS, CPC, and CTR.
* **💰 Budget Scenario Planner**: An interactive tool that allows users to allocate a hypothetical budget across platforms to see a projection of potential revenue based on historical performance.

---

## 🚀 How to Run Locally

### Prerequisites
* Python 3.8+
* `pip` package manager

### Setup Instructions
1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPOSITORY_URL]
    cd business-intelligence-dashboard
    ```

2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run Homepage.py
    ```
The application will open in your default web browser.

---

## 🛠️ Tech Stack

* **Language**: Python
* **Libraries**:
    * **Streamlit**: For the web application framework.
    * **Pandas**: For data manipulation and analysis.
    * **Plotly Express**: For creating interactive visualizations.

## 📁 Data Sources

* `Facebook.csv`, `Google.csv`, `TikTok.csv`: Campaign-level marketing data.
* `business.csv`: Daily business performance data.