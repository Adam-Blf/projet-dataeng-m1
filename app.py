import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Configuration de la page Streamlit
st.set_page_config("Olist Analytics Dashboard", layout="wide")
st.title("📊 Dashboard E-Commerce (Olist)")

# Extraction des données via SQLite (Simulation API Datamart)
def fetch_gold_data(q):
    conn = sqlite3.connect("datamart.db")
    df = pd.read_sql(q, conn)
    conn.close()
    return df

try:
    kpis = fetch_gold_data("SELECT * FROM kpi_state")
    
    # Indicateurs Métriques
    col1, col2 = st.columns(2)
    col1.metric("Revenue Global Olist", f"${kpis['total_sales'].sum():,.2f}")
    col2.metric("Etats Couverts", len(kpis))
    
    # Graphe 1 : Top Revenus par État
    top_states = kpis.sort_values('total_sales', ascending=False).head(10)
    st.plotly_chart(px.bar(top_states, x='customer_state', y='total_sales', title="KPI Chiffre d'affaires par État"))
    
    col3, col4 = st.columns(2)
    
    # Graphe 2 : Meilleurs clients d'un état spécifique
    with col3:
        state_filter = st.selectbox("Sélectionnez l'État", kpis['customer_state'].unique())
        rankings = fetch_gold_data(f"SELECT * FROM dim_rankings WHERE customer_state = '{state_filter}'")
        st.plotly_chart(px.bar(rankings.sort_values("state_rank").head(10), 
                               x='customer_unique_id', y='lifetime_revenue', title=f"Top 10 Acheteurs ({state_filter})", color='state_rank'))
        
    # Graphe 3 : Chronologie des revenus
    with col4:
        sales_timeline = fetch_gold_data("SELECT order_purchase_timestamp, revenue FROM fact_sales")
        sales_timeline['date'] = pd.to_datetime(sales_timeline['order_purchase_timestamp']).dt.date
        st.plotly_chart(px.line(sales_timeline.groupby('date').sum(), title="Evolution des Revenus Temporels", y='revenue'))

except Exception as e:
    st.error("Données Gold non trouvées. Exécutez d'abord la pipeline Spark pour générer 'datamart.db'.")

st.sidebar.info("Projet Data Engineering M1 - Adam & Emilien")
