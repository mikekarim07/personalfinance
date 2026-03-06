import pandas as pd
from datetime import date

def generate_recurring(recurring_df, transactions_df):

    today = date.today()

    new_rows = []

    for _, r in recurring_df.iterrows():

        if r["frequency"] == "monthly":

            tx_date = date(
                today.year,
                today.month,
                r["day_of_month"]
            )

            exists = transactions_df[
                (transactions_df["description"] == r["description"])
                &
                (transactions_df["date"] == pd.Timestamp(tx_date))
            ]

            if exists.empty:

                new_rows.append({

                    "date": tx_date,
                    "description": r["description"],
                    "type": r["type"],
                    "category": r["category"],
                    "subcategory": r["subcategory"],
                    "budget_amount": r["amount"],
                    "actual_amount": None

                })

    return new_rows
