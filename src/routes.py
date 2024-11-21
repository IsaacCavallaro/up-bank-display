from datetime import date, timedelta
from flask import Blueprint, request, render_template
from src.utils import (
    plot_dashboard_bar,
    fetch_transactions,
    push_to_notion,
)
from src.config import ACCOUNT_IDS, CATEGORIES

main_routes = Blueprint("main_routes", __name__)


@main_routes.route("/", methods=["GET", "POST"])
def index():
    selected_account_name = "2UP"
    all_accounts = False
    send_to_notion = False
    food_related = False

    if request.method == "POST":
        since = request.form.get("since")
        until = request.form.get("until")
        selected_accounts = request.form.getlist("account[]")
        selected_categories = request.form.getlist("category[]")
        description = request.form.get("description")
        min_amount = request.form.get("min_amount", type=float)
        max_amount = request.form.get("max_amount", type=float)
        all_accounts = request.form.get("all_accounts") == "on"
        send_to_notion = request.form.get("send_to_notion") == "on"
        food_related = request.form.get("food_related") == "on"
    else:
        since = (date.today() - timedelta(days=8)).strftime("%Y-%m-%d")
        until = date.today().strftime("%Y-%m-%d")
        selected_accounts = [selected_account_name]
        selected_categories = []
        description = None
        min_amount = None
        max_amount = None

    account_ids = (
        [ACCOUNT_IDS[acc] for acc in selected_accounts if acc in ACCOUNT_IDS]
        if not all_accounts
        else None
    )

    accounts_data = fetch_transactions(
        account_id=account_ids,
        since=f"{since}T00:00:00+10:00",
        until=f"{until}T23:59:59+10:00",
        parent_category=selected_categories,
        description=description,
        min_amount=min_amount,
        max_amount=max_amount,
        all_accounts=all_accounts,
        food_related=food_related,
    )

    bar_chart_html = plot_dashboard_bar(accounts_data, ", ".join(selected_accounts))

    account_names = list(ACCOUNT_IDS.keys())

    if request.method == "POST" and send_to_notion:
        for transaction in accounts_data["transactions"]:
            transaction_data = {
                "description": transaction["attributes"]["description"],
                "amount": transaction["attributes"]["amount"]["value"],
                "createdAt": transaction["attributes"]["createdAt"],
            }
            push_to_notion(transaction_data)

    return render_template(
        "index.html",
        accounts_data=accounts_data,
        bar_chart_html=bar_chart_html,
        default_since=since,
        default_until=until,
        account_names=account_names,
        selected_accounts=selected_accounts,
        selected_categories=selected_categories,
        send_to_notion=send_to_notion,
        all_accounts=all_accounts,
        food_related=food_related,
        description=description,
        min_amount=min_amount,
        max_amount=max_amount,
        categories=CATEGORIES,
    )
