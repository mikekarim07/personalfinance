import streamlit as st
import pandas as pd

from database import load_data, supabase
from finance import calculate_financials, detect_cashflow_risk
from charts import balance_chart, monthly_cashflow


st.set_page_config(layout="wide")

st.title("💰 Personal Budget Planner")




# -----------------------------
# SIMPLE PASSWORD AUTH
# -----------------------------

def check_password():

    def password_entered():

        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:

        st.text_input(
            "Enter password",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False

    elif not st.session_state["password_correct"]:

        st.text_input(
            "Enter password",
            type="password",
            on_change=password_entered,
            key="password",
        )
        st.error("😕 Password incorrect")
        return False

    else:
        return True


if not check_password():
    st.stop()







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
# CASHFLOW RISK DETECTION
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

categories = sorted(
    df["category"]
    .dropna()
    .astype(str)
    .unique()
)

if not df.empty:

    col1, col2, col3, col4 = st.columns(4)

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

    with col4:

        category_filter = st.selectbox(
            "Category",
            categories
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

    if category_filter != "All":

        filtered = filtered[
            filtered["category"] == category_filter
        ]
else:

    filtered = df

# -----------------------------
# EDITABLE TABLE
# -----------------------------

st.subheader("Transactions")

editable_df = filtered.sort_values("date").reset_index(drop=True)

# Ocultamos el UUID en la vista
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

# Reconstruimos dataframe con ID oculto
edited_df = edited_display_df.copy()
edited_df["id"] = editable_df["id"]

# -----------------------------
# SAVE CHANGES
# -----------------------------

for i in range(len(edited_df)):

    row = edited_df.loc[i]
    original = editable_df.loc[i]

    changed = False

    for col in ["date","description","type","category","subcategory","budget_amount","actual_amount"]:

        if str(row[col]) != str(original[col]):
            changed = True
            break

    if changed:

        update_data = {

            "date": str(row["date"]) if pd.notnull(row["date"]) else None,
            "description": str(row["description"]) if pd.notnull(row["description"]) else None,
            "type": str(row["type"]) if pd.notnull(row["type"]) else None,
            "category": str(row["category"]) if pd.notnull(row["category"]) else None,
            "subcategory": str(row["subcategory"]) if pd.notnull(row["subcategory"]) else None,
            "budget_amount": float(row["budget_amount"]) if pd.notnull(row["budget_amount"]) else None,
            "actual_amount": float(row["actual_amount"]) if pd.notnull(row["actual_amount"]) else None,

        }

        supabase.table("transactions").update(update_data).eq("id", row["id"]).execute()

st.success("Changes saved")
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
