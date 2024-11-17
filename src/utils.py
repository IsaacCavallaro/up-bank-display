import requests
import pandas as pd
import os
import matplotlib

matplotlib.use("Agg")  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
from src.config import ACCOUNT_IDS, NOTION_API_KEY, DATABASE_ID
import requests
from datetime import datetime


ACCESS_TOKEN = os.getenv("UP_API_TOKEN")


def check_access_token():
    if not os.getenv("UP_API_TOKEN"):
        raise ValueError(
            "Please set the UP_API_TOKEN environment variable in your .env file."
        )


def is_category_match(category_info, parent_category_info, parent_category):
    if not parent_category:
        return True
    return any(
        (parent_category_info and parent_category_info["id"] == cat)
        or (category_info and category_info["id"] == cat)
        for cat in parent_category
    )


def is_description_match(transaction_description, description):
    if not description:
        return True
    return (
        description.replace(" ", "").strip().lower()
        in transaction_description.replace(" ", "").strip()
    )


def is_food_match(
    transaction_description,
    category_info,
    parent_category_info,
    food_related,
    food_keywords,
    food_child_categories,
    food_parent_category,
):
    if not food_related:
        return True
    return any(keyword in transaction_description for keyword in food_keywords) or (
        category_info
        and (
            category_info["id"] in food_child_categories
            or (
                parent_category_info
                and parent_category_info["id"] == food_parent_category
            )
        )
    )


def fetch_transactions(
    account_id=None,
    since=None,
    until=None,
    parent_category=None,
    description=None,
    all_accounts=False,
    min_amount=None,
    max_amount=None,
    food_related=False,
):
    accounts_to_fetch = (
        account_id if account_id else ACCOUNT_IDS.values() if all_accounts else []
    )
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    food_keywords = ["coles", "woolworths"]
    food_child_categories = {"restaurants-and-cafes", "takeaway"}
    food_parent_category = "good-life"
    all_transactions = []

    for account in accounts_to_fetch:
        url = f"https://api.up.com.au/api/v1/accounts/{account}/transactions"
        params = {
            "filter[since]": since if since else None,
            "filter[until]": until if until else None,
            "page[size]": 100,
        }

        while url:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                transactions = data["data"]

                for transaction in transactions:
                    transaction_description = (
                        transaction.get("attributes", {}).get("description", "").lower()
                    )
                    transaction_id = transaction.get("id")
                    category_info = (
                        transaction.get("relationships", {})
                        .get("category", {})
                        .get("data")
                    )
                    parent_category_info = (
                        transaction.get("relationships", {})
                        .get("parent", {})
                        .get("data")
                    )

                    # Check if amount is within the specified range
                    amount = (
                        transaction.get("attributes", {})
                        .get("amount", {})
                        .get("value", None)
                    )
                    amount_match = True
                    if amount is not None:
                        amount = float(amount)
                        if min_amount is not None and amount < min_amount:
                            amount_match = False
                        if max_amount is not None and amount > max_amount:
                            amount_match = False

                    # Include transaction if all conditions match
                    if (
                        is_category_match(
                            category_info, parent_category_info, parent_category
                        )
                        and is_description_match(transaction_description, description)
                        and amount_match
                        and is_food_match(
                            transaction_description,
                            category_info,
                            parent_category_info,
                            food_related,
                            food_keywords,
                            food_child_categories,
                            food_parent_category,
                        )
                    ):
                        all_transactions.append(transaction)

                url = data["links"].get("next", None)
                params = {}  # Reset params for the next page
            else:
                print("Error:", response.json())
                return {"error": "Failed to retrieve data"}

    return {"transactions": all_transactions}


def push_to_notion(transaction_data):
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    amount = transaction_data.get("amount")
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            amount = None

    created_at = transaction_data.get("createdAt")
    if created_at is None:
        print("Invalid 'createdAt' format:", transaction_data.get("createdAt"))
        return

    if isinstance(created_at, str):
        try:
            created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            created_at = None

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": transaction_data["description"]}}]},
            "Amount": {"number": amount},
            "createdAt": {
                "date": {"start": (created_at.isoformat() if created_at else None)}
            },
        },
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Successfully pushed data to Notion")
    else:
        print("Failed to push data:", response.json())


# def fetch_transactions(account_id, since, until):
#     url = f"https://api.up.com.au/api/v1/accounts/{account_id}/transactions"
#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json",
#     }
#     params = {}
#     params["filter[since]"] = f"{since}T00:00:00+10:00" if since else None
#     params["filter[until]"] = f"{until}T23:59:59+10:00" if until else None

#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return {"error": "Failed to retrieve data"}


# def fetch_accounts():
#     url = "https://api.up.com.au/api/v1/accounts"
#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "application/json",
#     }

#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()["data"]
#     else:
#         return []


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
    try:
        if "Amount" not in df.columns:
            raise ValueError("DataFrame is missing the 'Amount' column.")

        deposits = df[df["Amount"] > 0]["Amount"].sum()
        withdrawals = df[df["Amount"] < 0]["Amount"].sum()

        if df.empty:
            print("Warning: The DataFrame is empty. No transactions to process.")
            return

        plot_totals(withdrawals, deposits, account_name)

    except Exception as e:
        print(f"An error occurred in calculate_totals: {e}")
        raise


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


def plot_dashboard_bar(accounts_data, account_name):
    transactions = accounts_data["transactions"]

    # Store withdrawals as negative values
    withdrawals = [
        float(txn["attributes"]["amount"]["value"])
        for txn in transactions
        if float(txn["attributes"]["amount"]["value"]) < 0
    ]
    deposits = [
        float(txn["attributes"]["amount"]["value"])
        for txn in transactions
        if float(txn["attributes"]["amount"]["value"]) > 0
    ]

    # Dynamically set the title with the selected account name
    fig = px.bar(
        x=["Withdrawals", "Deposits"],
        y=[sum(withdrawals), sum(deposits)],
        labels={"x": "Transaction Type", "y": "Amount (AUD)"},
        title=f"Total Withdrawals and Deposits for '{account_name}' Account",
    )

    # Update colors for each bar
    fig.update_traces(marker_color=["red", "green"])

    # Return the HTML div of the bar chart
    bar_chart_html = fig.to_html(full_html=False)
    return bar_chart_html
