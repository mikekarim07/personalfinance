import plotly.express as px


def balance_chart(df):

    fig = px.line(
        df,
        x="date",
        y="running_balance",
        title="Balance Forecast"
    )

    return fig


import pandas as pd
import plotly.express as px


def monthly_cashflow(df):

    df = df.copy()

    # asegurar tipo datetime
    df["date"] = pd.to_datetime(df["date"])

    # crear columna mes segura para Plotly
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # calcular ingresos y gastos
    summary = df.groupby(["month", "type"])["effective_amount"].sum().reset_index()

    # pivot para gráfico
    summary = summary.pivot(index="month", columns="type", values="effective_amount").fillna(0)

    summary = summary.reset_index()

    fig = px.bar(
        summary,
        x="month",
        y=[col for col in summary.columns if col != "month"],
        barmode="group",
        title="Monthly Cashflow"
    )

    fig.update_layout(
        yaxis_title="Amount",
        xaxis_title="Month"
    )

    return fig
