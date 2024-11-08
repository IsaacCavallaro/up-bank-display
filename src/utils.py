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
    if since:
        params["filter[since]"] = since
    if until:
        params["filter[until]"] = until

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


def plot_data(df, plot_type):
    if df.empty:
        return
    df = df.dropna(subset=["Settled At"]).copy()
    df.loc[:, "Settled At"] = pd.to_datetime(df["Settled At"], errors="coerce")
    if plot_type == "bar":
        plot_bar(df)
    elif plot_type == "line":
        plot_line(df)
    elif plot_type == "scatter":
        plot_scatter(df)
    elif plot_type == "pie":
        plot_pie(df)


def plot_bar(df):
    plt.figure(figsize=(10, 6))
    plt.bar(df["Description_Date"], df["Amount"], color="skyblue")
    plt.title("Transaction Description and Creation Date vs Amount")
    plt.xlabel("Description (Creation Date)")
    plt.ylabel("Amount (AUD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_line(df):
    plt.figure(figsize=(10, 6))
    plt.plot(df["Description_Date"], df["Amount"], marker="o", color="skyblue")
    plt.title("Amount vs Description Date")
    plt.xlabel("Description (Creation Date)")
    plt.ylabel("Amount (AUD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_scatter(df):
    plt.figure(figsize=(10, 6))
    plt.scatter(df["Description_Date"], df["Amount"], color="skyblue")
    plt.title("Transaction Scatter Plot")
    plt.xlabel("Description (Creation Date)")
    plt.ylabel("Amount (AUD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_pie(df):
    df_filtered = df[df["Amount"] > 0]
    if df_filtered.empty:
        return
    pie_data = df_filtered.groupby("Description")["Amount"].sum()
    plt.figure(figsize=(8, 8))
    plt.pie(
        pie_data,
        labels=pie_data.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=plt.cm.Paired.colors,
    )
    plt.title("Transaction Breakdown by Description")
    plt.tight_layout()
    plt.show()
