import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Northwind Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/northwind_processed.csv')
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    return df

df = load_data()

# --- SIDEBAR: FILTROS INTERACTIVOS ---
st.sidebar.header("Filtros del Dashboard")
categories = st.sidebar.multiselect(
    "Seleccionar Categorías:",
    options=df["CategoryName"].unique(),
    default=df["CategoryName"].unique()
)

years = st.sidebar.multiselect(
    "Seleccionar Año:",
    options=df["OrderYear"].unique(),
    default=df["OrderYear"].unique()
)

# Filtrar DataFrame
df_filtered = df[(df["CategoryName"].isin(categories)) & (df["OrderYear"].isin(years))]

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Northwind Analytics Dashboard")
st.markdown("Visualización ejecutiva de desempeño comercial e indicadores clave.")

# KPIs
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("Ventas Totales", f"${df_filtered['TotalSales'].sum():,.2f}")
col_kpi2.metric("Total Ordenes", f"{df_filtered['OrderID'].nunique():,}")
col_kpi3.metric("Ticket Promedio", f"${df_filtered.groupby('OrderID')['TotalSales'].sum().mean():,.2f}")

st.divider()

# Fila 1
c1, c2 = st.columns(2)
with c1:
    sales_monthly = df_filtered.groupby('YearMonth')['TotalSales'].sum().reset_index()
    fig1 = px.line(sales_monthly, x='YearMonth', y='TotalSales', title='Ventas Mensuales')
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    top_cust = df_filtered.groupby('CustomerName')['TotalSales'].sum().reset_index().sort_values(by='TotalSales', ascending=False).head(10)
    fig3 = px.bar(top_cust, x='TotalSales', y='CustomerName', orientation='h', title='Top 10 Clientes')
    st.plotly_chart(fig3, use_container_width=True)

# Fila 2
c3, c4 = st.columns(2)
with c3:
    fig5 = px.treemap(df_filtered, path=['CategoryName', 'ProductName'], values='TotalSales', title='Ventas por Categoría y Producto')
    st.plotly_chart(fig5, use_container_width=True)

with c4:
    fig6 = px.scatter(df_filtered, x='Discount', y='Quantity', color='CategoryName', title='Relación Descuento vs Cantidades')
    st.plotly_chart(fig6, use_container_width=True)