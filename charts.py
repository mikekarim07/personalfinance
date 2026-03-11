import plotly.express as px


def balance_chart(df):

    fig = px.line(
        df,
        x="date",
        y="running_balance",
        title="Balance Forecast"
    )

    return fig



def monthly_cashflow(df):

    df = df.copy()

    # asegurar formato fecha
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # eliminar filas sin fecha
    df = df.dropna(subset=["date"])

    # crear columna mes como string (no Period)
    df["month"] = df["date"].dt.strftime("%Y-%m")

    # asegurar números puros
    df["effective_amount"] = pd.to_numeric(df["effective_amount"], errors="coerce").fillna(0)

    # agrupar
    summary = (
        df.groupby(["month", "type"])["effective_amount"]
        .sum()
        .reset_index()
    )

    # pivot
    summary = summary.pivot(index="month", columns="type", values="effective_amount").fillna(0)

    # reset index
    summary = summary.reset_index()

    # convertir a float puro
    for col in summary.columns:
        if col != "month":
            summary[col] = summary[col].astype(float)

    fig = px.bar(
        summary,
        x="month",
        y=[col for col in summary.columns if col != "month"],
        barmode="group",
        title="Monthly Cashflow"
    )

    fig.update_layout(
        yaxis_title="Amount",
        xaxis_title="Month",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f"
    )

    return fig
