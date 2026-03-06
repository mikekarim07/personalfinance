import streamlit as st
import pandas as pd
from supabase import create_client

url = st.secrets["url"]
key = st.secrets["key"]

supabase = create_client(url, key)

TABLE = "transactions"


def load_data():

    response = supabase.table(TABLE).select("*").execute()

    df = pd.DataFrame(response.data)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


def insert_transaction(row):

    supabase.table(TABLE).insert(row).execute()


def update_transaction(id,row):

    supabase.table(TABLE).update(row).eq("id",id).execute()
