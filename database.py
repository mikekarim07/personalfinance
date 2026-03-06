import streamlit as st
import pandas as pd
from supabase import create_client

# -------------------------
# CONNECTION
# -------------------------

url = st.secrets["url"]
key = st.secrets["key"]

supabase = create_client(url, key)

# -------------------------
# TABLES
# -------------------------

TRANSACTIONS = "transactions"
RECURRING = "recurring_transactions"


# -------------------------
# LOAD TRANSACTIONS
# -------------------------

def load_data():

    response = supabase.table(TRANSACTIONS).select("*").execute()

    df = pd.DataFrame(response.data)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


# -------------------------
# INSERT SINGLE TRANSACTION
# -------------------------

def insert_transaction(row):

    supabase.table(TRANSACTIONS).insert(row).execute()


# -------------------------
# INSERT MULTIPLE TRANSACTIONS
# -------------------------

def insert_transactions(rows):

    supabase.table(TRANSACTIONS).insert(rows).execute()


# -------------------------
# LOAD RECURRING
# -------------------------

def load_recurring():

    response = supabase.table(RECURRING).select("*").execute()

    df = pd.DataFrame(response.data)

    return df
