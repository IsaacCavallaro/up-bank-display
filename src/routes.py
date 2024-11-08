from flask import Blueprint, request, render_template, jsonify
from utils import (
    fetch_transactions,
    process_transaction_data,
    calculate_totals,
    plot_data,
    fetch_accounts,
)
import os

main_routes = Blueprint("main_routes", __name__)

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


@main_routes.route("/", methods=["GET", "POST"])
def index():
    accounts_data = fetch_accounts()
    if request.method == "POST":
        account_name = request.form["account_name"]
        feature_choice = request.form["feature_choice"]
        plot_type = request.form["plot_type"]
        since = request.form["since"]
        until = request.form["until"]

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
            plot_data(df, plot_type, account_name)

    return render_template(
        "index.html", accounts=ACCOUNT_IDS, accounts_data=accounts_data
    )
