import streamlit as st
import pandas as pd

from database import (
    load_data,
    insert_transaction,
    insert_transactions,
    load_recurring,
    supabase
)

from finance import (
    calculate_financials,
    detect_cashflow_risk
)

from charts import (
    balance_chart,
    monthly_cashflow
)

from recurring import generate_recurring


st.set_page_config(layout="wide")

st.title("💰 Personal Budget Planner")

# -----------------------------
# LOAD DATA
# -----------------------------

df = load_data()

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])


# -----------------------------
# GENERATE RECURRING
# -----------------------------

recurring_df = load_recurring()

if not recurring_df.empty:

    new_rows = generate_recurring(recurring_df, df)

    if len(new_rows) > 0:

        insert_transactions(new_rows)

        df = load_data()

        df["date"] = pd.to_datetime(df["date"])


# -----------------------------
# FINANCIAL CALCULATIONS
# -----------------------------

if not df.empty:

    df = calculate_financials(df)


# -----------------------------
# CASHFLOW RISK DETECTION
# -----------------------------

if not df.empty:

    risk = detect_cashflow_risk(df)

    if risk is not None:

        st.warning(
            f"⚠ Cashflow risk on {risk['date'].date()} "
            f"Balance: ${risk['running_balance']:,.0f}"
        )


# -----------------------------
# METRICS
# -----------------------------

if not df.empty:

    balance = df["running_balance"].iloc[-1]

    income = df[df["type"] == "Income"]["effective_amount"].sum()

    expenses = df[df["type"] == "Expense"]["effective_amount"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Balance Forecast", f"${balance:,.0f}")
    col2.metric("Income", f"${income:,.0f}")
    col3.metric("Expenses", f"${expenses:,.0f}")


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

        insert_transaction(row)

        st.success("Transaction added")

        st.rerun()


# -----------------------------
# ADD RECURRING
# -----------------------------

st.subheader("Add Recurring Transaction")

with st.form("recurring_transaction"):

    col1, col2 = st.columns(2)

    with col1:

        r_description = st.text_input("Description")

        r_type = st.selectbox(
            "Type",
            ["Income", "Expense"],
            key="rtype"
        )

        r_category = st.text_input("Category")

    with col2:

        r_subcategory = st.text_input("Subcategory")

        r_amount = st.number_input(
            "Amount",
            step=0.01
        )

        r_day = st.number_input(
            "Day of Month",
            min_value=1,
            max_value=28
        )

    r_submit = st.form_submit_button("Add Recurring")

    if r_submit:

        row = {

            "description": r_description,
            "type": r_type,
            "category": r_category,
            "subcategory": r_subcategory,
            "amount": r_amount,
            "frequency": "monthly",
            "day_of_month": int(r_day)

        }

        supabase.table(
            "recurring_transactions"
        ).insert(row).execute()

        st.success("Recurring transaction added")

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
# TABLE
# -----------------------------

st.subheader("Transactions")

st.dataframe(
    filtered.sort_values("date"),
    use_container_width=True
)


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
