import os
from datetime import date, timedelta
from flask import Blueprint, request, render_template
from src.utils import (
    plot_dashboard_bar,
    fetch_transactions,
)
from src.config import ACCOUNT_IDS, CATEGORIES

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/", methods=["GET", "POST"])
def index():
    selected_account_name = "2UP"
    all_accounts = False

    if request.method == "POST":
        since = request.form.get("since")
        until = request.form.get("until")
        selected_account_name = request.form.get("account")
        category = request.form.get("category")
        description = request.form.get("description")
        all_accounts = request.form.get("all_accounts") == "on"
    else:
        since = (date.today() - timedelta(days=8)).strftime("%Y-%m-%d")
        until = date.today().strftime("%Y-%m-%d")
        category = None
        description = None

    ACCOUNT_ID = ACCOUNT_IDS.get(selected_account_name) if not all_accounts else None

    accounts_data = fetch_transactions(
        account_id=ACCOUNT_ID,
        since=f"{since}T00:00:00+10:00",
        until=f"{until}T23:59:59+10:00",
        parent_category=category,
        description=description,
        all_accounts=all_accounts,
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
        selected_category=category,
        all_accounts=all_accounts,
        description=description,
        categories=CATEGORIES,
    )
