from flask import Blueprint, request, render_template, jsonify
from utils import (
    fetch_transactions,
    process_transaction_data,
    calculate_totals,
    plot_data,
    plot_initial_bar,
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

    if request.method == "POST":
        since = request.form.get("since")
        until = request.form.get("until")
    else:
        since = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        until = date.today().strftime("%Y-%m-%d")

    accounts_data = inital_fetch_transactions(
        ACCOUNT_2UP_ID, f"{since}T00:00:00+10:00", f"{until}T23:59:59+10:00"
    )

    bar_chart_html = plot_initial_bar(accounts_data)

    return render_template(
        "index.html",
        accounts_data=accounts_data,
        bar_chart_html=bar_chart_html,
        default_since=since,
        default_until=until,
    )
