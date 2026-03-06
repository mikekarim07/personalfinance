import pandas as pd


def calculate_financials(df):

    df = df.sort_values("date")

    df["effective_amount"] = df["actual_amount"].fillna(
        df["budget_amount"]
    )

    df["running_balance"] = df["effective_amount"].cumsum()

    df["variance"] = df["actual_amount"] - df["budget_amount"]

    return df


def detect_cashflow_risk(df,threshold=500):

    risk = df[df["running_balance"] < threshold]

    if not risk.empty:

        return risk.iloc[0]

    return None
