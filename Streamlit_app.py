import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# ----------------------------------------------------------
# Page Config
# ----------------------------------------------------------
st.set_page_config(page_title="AI Salary Dashboard", layout="wide")

st.title("AI/ML Salary Insights Dashboard")

# ----------------------------------------------------------
# Load Data
# ----------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("salaries.csv")

df = load_data()

# ----------------------------------------------------------
# Convert Country Code → Full Country Name
# ----------------------------------------------------------
def code_to_country(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code   # fallback if a code is unknown

df["country_name"] = df["employee_residence"].apply(code_to_country)

# ----------------------------------------------------------
# Legend mapping (ONLY for charts)
# ----------------------------------------------------------
exp_map = {
    "EN": "Entry-level",
    "MI": "Mid-level",
    "SE": "Senior-level",
    "EX": "Executive-level"
}

# ----------------------------------------------------------
# Sidebar Filters
# ----------------------------------------------------------
st.sidebar.header("Filters")

years = sorted(df["work_year"].unique())
selected_year = st.sidebar.selectbox("Select Year", years)

countries = sorted(df["country_name"].unique())
selected_country = st.sidebar.multiselect(
    "Employee Country",
    countries,
    default=countries
)

experience_levels = sorted(df["experience_level"].unique())
selected_exp = st.sidebar.multiselect(
    "Experience Level",
    experience_levels,
    default=experience_levels
)

# ----------------------------------------------------------
# Filtered Data
# ----------------------------------------------------------
df_f = df[
    (df["work_year"] == selected_year) &
    (df["country_name"].isin(selected_country)) &
    (df["experience_level"].isin(selected_exp))
]

# =====================================================================
# 1️⃣ Salary Trend by Experience Level (Line Chart)
# =====================================================================
st.subheader("📈 Salary Trend by Experience Level")

trend = (
    df[df["experience_level"].isin(selected_exp)]
    .groupby(["work_year", "experience_level"])["salary_in_usd"]
    .median()
    .reset_index()
)

# Custom colors for lines
color_map = {
    "Entry-level": "#FF5733",      # orange-red
    "Mid-level": "#2E86C1",  # strong blue
    "Senior-level": "#28B463",     # green
    "Executive-level": "#AF7AC5" # purple
}

fig1 = px.line(
    trend,
    x="work_year",
    y="salary_in_usd",
    color=trend["experience_level"].map(exp_map),
    markers=True,
    color_discrete_map=color_map  # <-- apply new colors
)

# Make lines thicker
fig1.update_traces(line=dict(width=3))
fig1.update_layout(legend_title_text="Experience")

st.plotly_chart(fig1, use_container_width=True)

# =====================================================================
# 2️⃣ Top 10 Highest Paying Job Titles (Bar Chart + Card)
# =====================================================================
st.subheader("💰 Top 10 Highest Paying Job Titles")

job_salary = (
    df_f.groupby("job_title")["salary_in_usd"]
    .median()
    .sort_values(ascending=False)
    .reset_index()
    .head(10)
)

# Identify highest paid job
top_job = job_salary.iloc[0]["job_title"]
top_salary = job_salary.iloc[0]["salary_in_usd"]

# Assign colors: blue for top job, light gray for others
job_salary["color"] = job_salary["job_title"].apply(
    lambda x: "#2E86C1" if x == top_job else "#AED6F1"
)

col1, col2 = st.columns([3, 1])

with col1:
    fig2 = px.bar(
        job_salary,
        x="salary_in_usd",
        y="job_title",
        orientation="h",
        color="color",  # use our custom color column
        color_discrete_map="identity"  # use exact colors
    )

    fig2.update_layout(
        showlegend=False,
        yaxis=dict(categoryorder="total ascending")
    )

    st.plotly_chart(fig2, use_container_width=True)

# Salary Card
with col2:
    st.markdown("### 🏆 Highest Paid Job")
    st.markdown(
        f"""
        <div style='padding:20px; background:#f8f8f8; border-radius:12px; text-align:center;'>
            <h4>{top_job}</h4>
            <h2 style='color:#006400;'>${int(top_salary):,}</h2>
            <p>Median Salary (USD)</p>
        </div>
        """,
        unsafe_allow_html=True
    )
# =====================================================================
# 3️⃣ Salary by Country (NOW USING FULL COUNTRY NAME)
# =====================================================================
st.subheader("🌍 Country-wise Median Salary")

country_salary = (
    df_f.groupby("country_name")["salary_in_usd"]
    .median()
    .sort_values(ascending=False)
    .reset_index()
    .head(20)
)

fig3 = px.bar(
    country_salary,
    x="country_name",
    y="salary_in_usd",

)
st.plotly_chart(fig3, use_container_width=True)
