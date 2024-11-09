from flask import Blueprint, request, render_template, jsonify
from utils import (
    fetch_transactions,
    process_transaction_data,
    calculate_totals,
    plot_data,
    fetch_accounts,
    plot_accounts_bar,
    inital_fetch_transactions,
)
import os
from datetime import date, datetime, timedelta

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
    "2UP": os.getenv("2UP"),
}


@main_routes.route("/", methods=["GET", "POST"])
def index():
    ACCOUNT_2UP_ID = os.getenv("2UP")
    since = (date.today() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00+10:00")
    until = datetime.today().strftime("%Y-%m-%dT23:59:59+10:00")

    initial_two_up_data = inital_fetch_transactions(ACCOUNT_2UP_ID, since, until)

    bar_chart_html = ""
    if initial_two_up_data:
        bar_chart_html = plot_accounts_bar(initial_two_up_data)

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
        if feature_choice == "plot":
            plot_data(df, plot_type, account_name)

    return render_template(
        "index.html",
        accounts=ACCOUNT_IDS,
        accounts_data=initial_two_up_data,
        bar_chart_html=bar_chart_html,
    )
