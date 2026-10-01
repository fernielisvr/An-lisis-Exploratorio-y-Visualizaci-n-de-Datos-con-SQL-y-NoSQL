import re
import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import run_query

st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")


# ---------------------------------------------------------------------------
# Normalización de nombres de columnas
# ---------------------------------------------------------------------------
def to_snake_upper(name: str) -> str:
    """Convierte CamelCase a SNAKE_CASE.
    Ej: 'EmployeeName' -> 'EMPLOYEE_NAME', 'AnnualComp' -> 'ANNUAL_COMP'
    """
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.upper()


# Mapa de rescate: por si Oracle devuelve los alias SIN comillas dobles
# (los pasa a MAYÚSCULAS juntas: HIREDATE, EMPLOYEENAME, etc.)
RENAME_MAP = {
    'EMPLOYEEID': 'EMPLOYEE_ID',
    'FIRSTNAME': 'FIRST_NAME',
    'LASTNAME': 'LAST_NAME',
    'EMPLOYEENAME': 'EMPLOYEE_NAME',
    'EMAIL': 'EMAIL',
    'PHONENUMBER': 'PHONE_NUMBER',
    'HIREDATE': 'HIRE_DATE',
    'JOBID': 'JOB_ID',
    'JOBTITLE': 'JOB_TITLE',
    'MINSALARY': 'MIN_SALARY',
    'MAXSALARY': 'MAX_SALARY',
    'SALARY': 'SALARY',
    'COMMISSIONPCT': 'COMMISSION_PCT',
    'ANNUALCOMP': 'ANNUAL_COMP',
    'MANAGERID': 'MANAGER_ID',
    'MANAGERNAME': 'MANAGER_NAME',
    'DEPARTMENTID': 'DEPARTMENT_ID',
    'DEPARTMENTNAME': 'DEPARTMENT_NAME',
    'LOCATIONID': 'LOCATION_ID',
    'CITY': 'CITY',
    'STATEPROVINCE': 'STATE_PROVINCE',
    'COUNTRYID': 'COUNTRY_ID',
    'COUNTRYNAME': 'COUNTRY_NAME',
    'REGIONID': 'REGION_ID',
    'REGIONNAME': 'REGION_NAME',
    'TENUREYEARS': 'TENURE_YEARS',
    'JOBSTARTDATE': 'JOB_START_DATE',
    'JOBENDDATE': 'JOB_END_DATE',
    'JOBHISTORYDEPTID': 'JOB_HISTORY_DEPT_ID',
    'JOBHISTORYJOBID': 'JOB_HISTORY_JOB_ID',
}


# ---------------------------------------------------------------------------
# Carga y preparación de datos
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    query = "SELECT * FROM HR.VW_STAGING_HR"
    df = run_query(query)

    # Asegurar que sea DataFrame
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    # 1) Normalizar nombres de columnas (CamelCase -> SNAKE_CASE)
    df.columns = [to_snake_upper(c) for c in df.columns]

    # 2) Rescate: por si Oracle devolvió alias en MAYÚSCULAS juntas
    df = df.rename(columns=RENAME_MAP)

    # 3) Validación temprana
    required = ['EMPLOYEE_ID', 'HIRE_DATE', 'SALARY', 'DEPARTMENT_NAME']
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(
            f"⚠️ Faltan columnas en la vista: {missing}. "
            f"Columnas recibidas: {list(df.columns)}"
        )
        st.stop()

    # 4) Fechas
    df['HIRE_DATE'] = pd.to_datetime(df['HIRE_DATE'], errors='coerce')
    df['HIRE_YEAR'] = df['HIRE_DATE'].dt.year
    df['YEAR_MONTH'] = df['HIRE_DATE'].dt.to_period('M').astype(str)

    # 5) Comisión anual (la vista no la trae, se calcula)
    df['ANNUAL_COMMISSION'] = (
        df['COMMISSION_PCT'].fillna(0) * df['SALARY'].fillna(0)
    )

    # 6) Rellenar nulos en dimensiones para evitar errores en gráficos
    for col in ['DEPARTMENT_NAME', 'REGION_NAME', 'COUNTRY_NAME',
                'CITY', 'JOB_TITLE', 'EMPLOYEE_NAME', 'MANAGER_NAME']:
        if col in df.columns:
            df[col] = df[col].fillna('(Sin dato)')

    return df


df = load_data()

# ---------------------------------------------------------------------------
# SIDEBAR: FILTROS
# ---------------------------------------------------------------------------
st.sidebar.header("Filtros del Dashboard")

departments = st.sidebar.multiselect(
    "Seleccionar Departamentos:",
    options=sorted(df["DEPARTMENT_NAME"].unique()),
    default=sorted(df["DEPARTMENT_NAME"].unique()),
)

years = st.sidebar.multiselect(
    "Seleccionar Año de Contratación:",
    options=sorted(df["HIRE_YEAR"].dropna().unique()),
    default=sorted(df["HIRE_YEAR"].dropna().unique()),
)

df_filtered = df[
    (df["DEPARTMENT_NAME"].isin(departments)) &
    (df["HIRE_YEAR"].isin(years))
].copy()

# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
st.title("HR Analytics Dashboard (Oracle HR)")
st.markdown("Visualización ejecutiva de nómina, plantilla y estructura organizacional.")

# KPIs
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("Nómina Anual Total",
                f"${df_filtered['ANNUAL_COMP'].sum():,.2f}")
col_kpi2.metric("Total Empleados",
                f"{df_filtered['EMPLOYEE_ID'].nunique():,}")
col_kpi3.metric("Salario Anual Promedio",
                f"${df_filtered['ANNUAL_COMP'].mean():,.2f}")

st.divider()

# Fila 1
c1, c2 = st.columns(2)

with c1:
    hires_monthly = (
        df_filtered.dropna(subset=['YEAR_MONTH'])
        .groupby('YEAR_MONTH')
        .size()
        .reset_index(name='HIRES')
        .sort_values('YEAR_MONTH')
    )
    if hires_monthly.empty:
        st.info("Sin datos de contrataciones para los filtros seleccionados.")
    else:
        fig1 = px.line(hires_monthly, x='YEAR_MONTH', y='HIRES',
                       title='Contrataciones por Mes')
        st.plotly_chart(fig1, use_container_width=True)

with c2:
    top_paid = (
        df_filtered.groupby('EMPLOYEE_NAME')['ANNUAL_COMP']
        .sum()
        .reset_index()
        .sort_values('ANNUAL_COMP', ascending=False)
        .head(10)
    )
    if top_paid.empty:
        st.info("Sin datos de salarios para los filtros seleccionados.")
    else:
        fig3 = px.bar(top_paid, x='ANNUAL_COMP', y='EMPLOYEE_NAME',
                      orientation='h', title='Top 10 Salarios Anuales')
        st.plotly_chart(fig3, use_container_width=True)

# Fila 2
c3, c4 = st.columns(2)

with c3:
    fig5 = px.treemap(
        df_filtered,
        path=['REGION_NAME', 'COUNTRY_NAME', 'DEPARTMENT_NAME'],
        values='ANNUAL_COMP',
        title='Nómina por Región / País / Departamento'
    )
    st.plotly_chart(fig5, use_container_width=True)

with c4:
    fig6 = px.scatter(
        df_filtered,
        x='SALARY',
        y='ANNUAL_COMMISSION',
        color='DEPARTMENT_NAME',
        hover_data=['EMPLOYEE_NAME', 'JOB_TITLE'],
        title='Salario vs Comisión Anual'
    )
    st.plotly_chart(fig6, use_container_width=True)

# ---------------------------------------------------------------------------
# Detalle
# ---------------------------------------------------------------------------
with st.expander("Ver detalle de empleados"):
    st.dataframe(
        df_filtered[[
            'EMPLOYEE_NAME', 'JOB_TITLE', 'DEPARTMENT_NAME',
            'CITY', 'COUNTRY_NAME', 'HIRE_DATE', 'SALARY'
        ]].sort_values('SALARY', ascending=False),
        use_container_width=True
    )
