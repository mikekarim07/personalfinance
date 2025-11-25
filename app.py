import streamlit as st
from supabase import create_client, Client
import pandas as pd

st.set_page_config(page_title="Personal Budget", page_icon="💰", layout="wide")

# --- CONNECT TO SUPABASE ---
@st.cache_resource
def get_client() -> Client:
    url = st.secrets["url"]
    key = st.secrets["key"]
    return create_client(url, key)

supabase = get_client()

# --- LOAD DATA ---
@st.cache_data(ttl=30)
def load_movs():
    data = supabase.table("data_movs").select("*").execute()
    return pd.DataFrame(data.data)

st.title("💰 Personal Budget Control")

df = load_movs()
st.subheader("Current Movements")
st.dataframe(df, use_container_width=True)

# --- ADD NEW ROW ---
st.subheader("➕ Add New Movement")

with st.form("add_form"):
    new_date = st.date_input("Date")
    new_type = st.selectbox("Type", ["Income", "Expense"])
    new_category = st.text_input("Category")
    new_subcategory = st.text_input("Subcategory")
    new_description = st.text_input("Description")
    new_forecast = st.number_input("Forecast Amount", min_value=0.0, step=0.01)
    new_actual = st.number_input("Actual Amount", min_value=0.0, step=0.01)

    submitted = st.form_submit_button("Add Movement")

if submitted:
    supabase.table("data_movs").insert({
        "Date": str(new_date),
        "Type": new_type,
        "Category": new_category,
        "Subcategory": new_subcategory,
        "Description": new_description,
        "Forecast_amount": new_forecast,
        "Actual_amount": new_actual
    }).execute()

    st.success("Movement added!")
    st.cache_data.clear()
    st.experimental_rerun()

# --- EDIT EXISTING ROW ---
st.subheader("✏️ Edit Movement")

# Select row to edit
row_id = st.selectbox("Select Movement ID", df["movs_id"])

row = df[df["movs_id"] == row_id].iloc[0]

with st.form("edit_form"):
    e_date = st.date_input("Date", pd.to_datetime(row["Date"]))
    e_type = st.selectbox("Type", ["Income", "Expense"], index=0 if row["Type"] == "Income" else 1)
    e_category = st.text_input("Category", row["Category"])
    e_subcategory = st.text_input("Subcategory", row["Subcategory"])
    e_description = st.text_input("Description", row["Description"])
    e_forecast = st.number_input("Forecast Amount", min_value=0.0, value=float(row["Forecast_amount"]))
    e_actual = st.number_input("Actual Amount", min_value=0.0, value=float(row["Actual_amount"]))

    edit_submit = st.form_submit_button("Save Changes")

if edit_submit:
    supabase.table("data_movs").update({
        "Date": str(e_date),
        "Type": e_type,
        "Category": e_category,
        "Subcategory": e_subcategory,
        "Description": e_description,
        "Forecast_amount": e_forecast,
        "Actual_amount": e_actual
    }).eq("movs_id", row_id).execute()

    st.success("Movement updated!")
    st.cache_data.clear()
    st.experimental_rerun()
