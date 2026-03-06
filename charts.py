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

    monthly = df.copy()

    monthly["month"] = monthly["date"].dt.to_period("M")

    monthly = monthly.groupby(
        ["month","type"]
    )["effective_amount"].sum().reset_index()

    fig = px.bar(
        monthly,
        x="month",
        y="effective_amount",
        color="type"
    )

    return fig
