import requests
import pandas as pd
import os
import matplotlib

matplotlib.use("Agg")  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import plotly.express as px

ACCESS_TOKEN = os.getenv("UP_API_TOKEN")


def check_access_token():
    if not os.getenv("UP_API_TOKEN"):
        raise ValueError(
            "Please set the UP_API_TOKEN environment variable in your .env file."
        )


def fetch_transactions(account_id, since, until):
    url = f"https://api.up.com.au/api/v1/accounts/{account_id}/transactions"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    params = {}
    params["filter[since]"] = f"{since}T00:00:00+10:00" if since else None
    params["filter[until]"] = f"{until}T23:59:59+10:00" if until else None

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve data"}


def process_transaction_data(transaction_data):
    if transaction_data and "data" in transaction_data:
        df = pd.json_normalize(
            transaction_data["data"],
            sep="_",
            meta=[
                ["attributes", "description"],
                ["attributes", "amount", "value"],
                ["attributes", "settledAt"],
                ["attributes", "createdAt"],
            ],
        )
        df.rename(
            columns={
                "attributes_description": "Description",
                "attributes_amount_value": "Amount",
                "attributes_settledAt": "Settled At",
                "attributes_createdAt": "Created At",
            },
            inplace=True,
        )
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df["Settled At"] = pd.to_datetime(df["Settled At"], errors="coerce")
        df["Created At"] = pd.to_datetime(df["Created At"], errors="coerce", utc=True)
        df.dropna(subset=["Created At"], inplace=True)
        df["Description"] = df["Description"].fillna("Unknown")
        df["Description_Date"] = (
            df["Description"].astype(str)
            + " ("
            + df["Created At"].dt.strftime("%Y-%m-%d")
            + ")"
        )
        return df
    else:
        return pd.DataFrame()


def calculate_totals(df, account_name):
    deposits = df[df["Amount"] > 0]["Amount"].sum()
    withdrawals = df[df["Amount"] < 0]["Amount"].sum()
    plot_totals(withdrawals, deposits, account_name)


def plot_totals(withdrawals, deposits, account_name):
    plt.figure(figsize=(8, 5))
    categories = ["Withdrawals", "Deposits"]
    values = [withdrawals, deposits]

    plt.bar(categories, values, color=["salmon", "skyblue"])
    plt.title("Total Withdrawals and Deposits")
    plt.ylabel("Amount (AUD)")
    plt.show()

    fig = px.bar(
        x=categories,
        y=values,
        title=f"Total Withdrawals & Deposits for {account_name}",
        labels={"x": "Transaction Type", "y": "Amount (AUD)"},
        color=categories,
        color_discrete_map={"Withdrawals": "salmon", "Deposits": "skyblue"},
    )
    fig.show()


def plot_data(df, plot_type, account_name):
    if df.empty:
        return
    # Ensure 'Settled At' is a valid date field
    df = df.dropna(subset=["Settled At"]).copy()
    df["Settled At"] = pd.to_datetime(df["Settled At"], errors="coerce")

    if plot_type == "bar":
        plot_bar(df, account_name)
    elif plot_type == "line":
        plot_line(df)
    elif plot_type == "pie":
        plot_pie(df)


def plot_bar(df, account_name):
    fig = px.bar(
        df,
        x="Description_Date",
        y="Amount",
        title=f"Transaction Details for {account_name}",
        labels={
            "Description_Date": "Description (Creation Date)",
            "Amount": "Amount (AUD)",
        },
    )
    fig.show()


def plot_line(df):
    fig = px.line(
        df,
        x="Settled At",
        y="Amount",
        title="Line Plot of Amount Over Time",
        labels={"Settled At": "Settled Date", "Amount": "Amount (AUD)"},
    )
    fig.show()


def plot_pie(df):
    df_filtered = df[df["Amount"] > 0]
    if df_filtered.empty:
        return
    df_filtered.groupby("Description")["Amount"].sum()
    fig = px.pie(
        df_filtered,
        names="Description_Date",
        values="Amount",
        title="Pie Chart of Amount by Description Date",
    )
    fig.show()
