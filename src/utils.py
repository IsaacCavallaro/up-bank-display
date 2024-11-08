import os
import requests
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv

import io
import matplotlib.pyplot as plt
from flask import Response, jsonify
import base64

load_dotenv()
ACCESS_TOKEN = os.getenv("UP_API_TOKEN")

ACCOUNT_IDS = {
    "BILLS": os.getenv("BILLS"),
    "GIFTS": os.getenv("GIFTS"),  # TODO: Bug GIFTS not foound
    "KIDS": os.getenv("KIDS"),
    "EXTRAS": os.getenv("EXTRAS"),
    "HOLIDAYS": os.getenv("HOLIDAYS"),
    "SUPER": os.getenv("SUPER"),
    "INVESTMENTS": os.getenv("INVESTMENTS"),
    "RAINY_DAY": os.getenv("RAINY_DAY"),
    "EMERGENCY": os.getenv("EMERGENCY"),
    "HOME_DEPOSIT": os.getenv("HOME_DEPOSIT"),
    "TRANSPORT": os.getenv("TRANSPORT"),
    "HEALTH": os.getenv("HEALTH"),
    "GROCERIES": os.getenv("GROCERIES"),
    "PERSONAL_ACCOUNT": os.getenv("PERSONAL_ACCOUNT"),
    "RENT": os.getenv("RENT"),
}


def check_access_token():
    if not os.getenv("UP_API_TOKEN"):
        raise ValueError(
            "Please set the UP_API_TOKEN environment variable in your .env file."
        )


def fetch_transactions(account_id, since, until):
    """Fetch transactions from the Up API for a specific account and optional date filtering."""
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
        print(f"Failed to retrieve data: {response.status_code}")
        print(response.text)
        return None


def process_transaction_data(transaction_data):
    """Convert transaction data to a DataFrame and prepare it for plotting."""
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
        print("No transaction data found.")
        return pd.DataFrame()


def calculate_totals(df, account_name):
    deposits = df[df["Amount"] > 0]["Amount"].sum()
    withdrawals = df[df["Amount"] < 0]["Amount"].sum()
    plot_totals(withdrawals, deposits, account_name)
    return {"deposits": deposits, "withdrawals": withdrawals}


# Plotting functions
def plot_totals(withdrawals, deposits, account_name):
    """Plot a bar chart for total withdrawals and deposits."""
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


def plot_bar(df):
    # Generate the plot
    plt.figure(figsize=(10, 6))
    plt.bar(df["Description_Date"], df["Amount"], color="skyblue")
    plt.title("Transaction Description and Creation Date vs Amount")
    plt.xlabel("Description (Creation Date)")
    plt.ylabel("Amount (AUD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the plot to a BytesIO object (in-memory file-like object)
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)  # Rewind the BytesIO object to the beginning

    # Close the plot to release resources
    plt.close()

    # Encode the image to base64
    plot_base64 = base64.b64encode(img.getvalue()).decode("utf-8")

    # Return the base64-encoded image
    return jsonify({"plotUrl": "data:image/png;base64," + plot_base64})


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
        print("No positive transaction amounts to plot.")
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


def plot_data(df, plot_type):
    """Generate a plot based on the given DataFrame and plot type."""
    if df.empty:
        print("No data to plot.")
        return (
            jsonify({"error": "No data to plot"}),
            400,
        )
    df = df.dropna(subset=["Settled At"]).copy()
    df.loc[:, "Settled At"] = pd.to_datetime(df["Settled At"], errors="coerce")
    if plot_type == "bar":
        return plot_bar(df)
    return jsonify({"error": "Invalid plot type"}), 400
