import streamlit as st

from database import load_data, insert_transaction
from finance import calculate_financials, detect_cashflow_risk
from charts import balance_chart, monthly_cashflow


st.set_page_config(layout="wide")

st.title("💰 Personal Budget Planner")


df = load_data()


if not df.empty:

    df = calculate_financials(df)


# -------------------------
# CASHFLOW RISK
# -------------------------

risk = detect_cashflow_risk(df)

if risk is not None:

    st.warning(
        f"⚠ Cashflow risk on {risk['date'].date()} "
        f"Balance: ${risk['running_balance']:,.0f}"
    )


# -------------------------
# METRICS
# -------------------------

if not df.empty:

    balance = df["running_balance"].iloc[-1]

    income = df[df["type"]=="Income"]["effective_amount"].sum()

    expenses = df[df["type"]=="Expense"]["effective_amount"].sum()

    col1,col2,col3 = st.columns(3)

    col1.metric("Balance Forecast",f"${balance:,.0f}")

    col2.metric("Income",f"${income:,.0f}")

    col3.metric("Expenses",f"${expenses:,.0f}")


# -------------------------
# ADD TRANSACTION
# -------------------------

st.subheader("Add Transaction")

with st.form("add_tx"):

    col1,col2 = st.columns(2)

    with col1:

        date = st.date_input("Date")
        description = st.text_input("Description")
        type_ = st.selectbox("Type",["Income","Expense"])

    with col2:

        category = st.text_input("Category")
        subcategory = st.text_input("Subcategory")

        budget = st.number_input("Budget Amount")

        actual = st.number_input(
            "Actual Amount",
            value=0.0
        )

    submit = st.form_submit_button("Add")

    if submit:

        row = {

        "date":str(date),
        "description":description,
        "type":type_,
        "category":category,
        "subcategory":subcategory,
        "budget_amount":budget,
        "actual_amount":actual if actual!=0 else None

        }

        insert_transaction(row)

        st.success("Transaction added")

        st.rerun()


# -------------------------
# TABLE
# -------------------------

st.subheader("Transactions")

st.dataframe(df,use_container_width=True)


# -------------------------
# CHARTS
# -------------------------

if not df.empty:

    st.plotly_chart(
        balance_chart(df),
        use_container_width=True
    )

    st.plotly_chart(
        monthly_cashflow(df),
        use_container_width=True
    )
