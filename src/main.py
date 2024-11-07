import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("UP_API_TOKEN")

ACCOUNT_IDS = {
    "BILLS_SAVER": os.getenv("BILLS_SAVER"),
    "GIFTS": os.getenv("GIFTS"),
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
        # Normalize JSON data to create a DataFrame
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

        # Rename and handle missing columns
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

        # Drop rows where Created At is missing to avoid issues in plots
        df.dropna(subset=["Created At"], inplace=True)

        # Ensure Description is a string and Created At is in date format
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


def plot_bar(df):
    """Generate a bar plot for Description_Date vs Amount."""
    plt.figure(figsize=(10, 6))
    plt.bar(df["Description_Date"], df["Amount"], color="skyblue")
    plt.title("Transaction Description and Creation Date vs Amount")
    plt.xlabel("Description (Creation Date)")
    plt.ylabel("Amount (AUD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

    # Plotly Bar Plot
    fig = px.bar(
        df,
        x="Description_Date",
        y="Amount",
        title="Transaction Description and Creation Date vs Amount",
        labels={
            "Description_Date": "Description (Creation Date)",
            "Amount": "Amount (AUD)",
        },
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()


def plot_line(df):
    """Generate a line plot for Amount over Time."""
    plt.plot(df["Settled At"], df["Amount"], marker="o")
    plt.title("Amount Over Time")
    plt.xlabel("Date")
    plt.ylabel("Amount (AUD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    fig = px.line(df, x="Settled At", y="Amount", title="Amount Over Time")
    fig.show()


def plot_scatter(df):
    """Generate a scatter plot for Description vs Amount."""
    fig = px.scatter(df, x="Description", y="Amount", title="Transaction Scatter Plot")
    fig.show()


def plot_data(df, plot_type):
    """Generate a plot based on the given DataFrame and plot type."""
    if df.empty:
        print("No data to plot.")
        return

    # Filter out rows where 'Settled At' has missing values
    df = df.dropna(subset=["Settled At"]).copy()

    # Ensure 'Settled At' is in datetime format using .loc to avoid SettingWithCopyWarning
    df.loc[:, "Settled At"] = pd.to_datetime(df["Settled At"], errors="coerce")

    if plot_type == "bar":
        plot_bar(df)
    elif plot_type == "line":
        plot_line(df)
    elif plot_type == "scatter":
        plot_scatter(df)
    else:
        print(f"Plot type '{plot_type}' is not supported.")


def main(account_name, plot_type, since, until):
    """Main function to fetch, process, and plot data for a specified account."""
    account_id = ACCOUNT_IDS.get(account_name)
    if not account_id:
        print(f"Account '{account_name}' not found in environment variables.")
        return

    transaction_data = fetch_transactions(account_id, since, until)
    df = process_transaction_data(transaction_data)

    plot_data(df, plot_type)


if __name__ == "__main__":
    check_access_token()
    print("Available accounts:", ", ".join(ACCOUNT_IDS.keys()))
    account_name = input("Enter account name: ").strip().upper()
    plot_type = input("Enter plot type (bar, line, scatter): ").strip().lower()
    since = input(
        "Enter start date (YYYY-MM-DD format) or leave blank for no start date: "
    ).strip()
    until = input(
        "Enter end date (YYYY-MM-DD format) or leave blank for no end date: "
    ).strip()

    since = f"{since}T00:00:00+10:00" if since else None
    until = f"{until}T23:59:59+10:00" if until else None

    main(account_name=account_name, plot_type=plot_type, since=since, until=until)
