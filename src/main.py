from flask import Flask, request, jsonify, render_template
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv
from utils import process_transaction_data, calculate_totals, plot_data

load_dotenv()
app = Flask(__name__)

# API Token
ACCESS_TOKEN = os.getenv("UP_API_TOKEN")

ACCOUNT_IDS = {
    "BILLS": os.getenv("BILLS"),
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


# Route to display the form and handle submissions
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        account_name = request.form["account_name"]
        feature_choice = request.form["feature_choice"]
        plot_type = request.form["plot_type"]
        since = request.form["since"]
        until = request.form["until"]

        # Fetch and process the transaction data
        account_id = ACCOUNT_IDS.get(account_name)
        if not account_id:
            return jsonify({"error": "Invalid account name"})

        transaction_data = fetch_transactions(account_id, since, until)
        if "error" in transaction_data:
            return jsonify(transaction_data)

        df = process_transaction_data(transaction_data)
        if feature_choice == "totals":
            calculate_totals(df, account_name)
        elif feature_choice == "plot":
            plot_data(df, plot_type)

        return jsonify({"message": "Data processed successfully"})

    return render_template("index.html", accounts=ACCOUNT_IDS)


if __name__ == "__main__":
    check_access_token()
    app.run(debug=True)
