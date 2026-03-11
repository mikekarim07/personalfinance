import streamlit as st
import pandas as pd

from database import load_data, supabase
from finance import calculate_financials, detect_cashflow_risk
from charts import balance_chart, monthly_cashflow


st.set_page_config(layout="wide")

st.title("💰 Personal Budget Planner")

# -----------------------------
# LOAD DATA
# -----------------------------

df = load_data()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])

# -----------------------------
# CALCULATE FINANCIALS
# -----------------------------

if not df.empty:
    df = calculate_financials(df)

# -----------------------------
# CASHFLOW RISK
# -----------------------------

if not df.empty:

    risk = detect_cashflow_risk(df)

    if risk is not None:

        st.warning(
            f"⚠ Cashflow risk on {risk['date'].date()} "
            f"Balance: ${risk['running_balance']:,.2f}"
        )

# -----------------------------
# METRICS
# -----------------------------

if not df.empty:

    balance = df["running_balance"].iloc[-1]

    income = df[df["type"] == "Income"]["effective_amount"].sum()

    expenses = df[df["type"] == "Expense"]["effective_amount"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Balance Forecast", f"${balance:,.2f}")
    col2.metric("Income", f"${income:,.2f}")
    col3.metric("Expenses", f"${expenses:,.2f}")

# -----------------------------
# ADD TRANSACTION
# -----------------------------

st.subheader("Add Transaction")

with st.form("add_transaction"):

    col1, col2 = st.columns(2)

    with col1:

        date = st.date_input("Date")

        description = st.text_input("Description")

        type_ = st.selectbox(
            "Type",
            ["Income", "Expense"]
        )

    with col2:

        category = st.text_input("Category")

        subcategory = st.text_input("Subcategory")

        budget = st.number_input(
            "Budget Amount",
            step=0.01
        )

        actual = st.number_input(
            "Actual Amount",
            step=0.01,
            value=0.0
        )

    submit = st.form_submit_button("Add Transaction")

    if submit:

        row = {

            "date": str(date),
            "description": description,
            "type": type_,
            "category": category,
            "subcategory": subcategory,
            "budget_amount": budget,
            "actual_amount": actual if actual != 0 else None

        }

        supabase.table("transactions").insert(row).execute()

        st.success("Transaction added")

        st.rerun()

# -----------------------------
# FILTERS
# -----------------------------

st.subheader("Filters")

if not df.empty:

    col1, col2, col3 = st.columns(3)

    with col1:

        year_filter = st.selectbox(
            "Year",
            sorted(df["date"].dt.year.unique())
        )

    with col2:

        month_filter = st.selectbox(
            "Month",
            ["All"] + list(range(1, 13))
        )

    with col3:

        type_filter = st.selectbox(
            "Type",
            ["All", "Income", "Expense"]
        )

    filtered = df.copy()

    filtered = filtered[
        filtered["date"].dt.year == year_filter
    ]

    if month_filter != "All":

        filtered = filtered[
            filtered["date"].dt.month == month_filter
        ]

    if type_filter != "All":

        filtered = filtered[
            filtered["type"] == type_filter
        ]

else:

    filtered = df

# -----------------------------
# EDITABLE TABLE
# -----------------------------

st.subheader("Transactions")

editable_df = filtered.sort_values("date").reset_index(drop=True)

display_df = editable_df.drop(columns=["id"])

edited_display_df = st.data_editor(

    display_df,

    use_container_width=True,

    column_config={

        "date": st.column_config.DateColumn("Date"),

        "budget_amount": st.column_config.NumberColumn(
            "Budget",
            format="$ %,.2f"
        ),

        "actual_amount": st.column_config.NumberColumn(
            "Actual",
            format="$ %,.2f"
        ),

        "effective_amount": st.column_config.NumberColumn(
            "Effective",
            format="$ %,.2f",
            disabled=True
        ),

        "running_balance": st.column_config.NumberColumn(
            "Balance",
            format="$ %,.2f",
            disabled=True
        ),

        "variance": st.column_config.NumberColumn(
            "Variance",
            format="$ %,.2f",
            disabled=True
        ),

    },

    disabled=[
        "effective_amount",
        "running_balance",
        "variance"
    ],

    key="transactions_editor"

)

# -----------------------------
# REBUILD DATAFRAME WITH ID
# -----------------------------

edited_df = edited_display_df.copy()

edited_df["id"] = editable_df["id"]

# -----------------------------
# SAVE CHANGES
# -----------------------------

if not edited_df.equals(editable_df):

    for i, row in edited_df.iterrows():

        original = editable_df.loc[i]

        if not row.equals(original):

            supabase.table("transactions").update({

                "date": str(row["date"]),
                "description": row["description"],
                "type": row["type"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "budget_amount": row["budget_amount"],
                "actual_amount": row["actual_amount"]

            }).eq("id", row["id"]).execute()

    st.success("Changes saved")

    st.rerun()

# -----------------------------
# CHARTS
# -----------------------------

if not df.empty:

    st.subheader("Balance Forecast")

    st.plotly_chart(
        balance_chart(df),
        use_container_width=True
    )

    st.subheader("Monthly Cashflow")

    st.plotly_chart(
        monthly_cashflow(df),
        use_container_width=True
    )
