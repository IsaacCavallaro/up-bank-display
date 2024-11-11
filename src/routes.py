import os
from datetime import date, timedelta
from flask import Blueprint, request, render_template
from utils import (
    plot_dashboard_bar,
    fetch_transactions,
)


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
    # default on GET
    selected_account_name = "2UP"

    if request.method == "POST":
        since = request.form.get("since")
        until = request.form.get("until")
        selected_account_name = request.form.get("account")
    else:
        since = (date.today() - timedelta(days=8)).strftime("%Y-%m-%d")
        until = date.today().strftime("%Y-%m-%d")

    ACCOUNT_ID = ACCOUNT_IDS.get(
        selected_account_name, os.getenv(selected_account_name)
    )

    accounts_data = fetch_transactions(
        ACCOUNT_ID, f"{since}T00:00:00+10:00", f"{until}T23:59:59+10:00"
    )

    bar_chart_html = plot_dashboard_bar(accounts_data, selected_account_name)

    account_names = list(ACCOUNT_IDS.keys())

    return render_template(
        "index.html",
        accounts_data=accounts_data,
        bar_chart_html=bar_chart_html,
        default_since=since,
        default_until=until,
        account_names=account_names,
        selected_account_name=selected_account_name,
    )
