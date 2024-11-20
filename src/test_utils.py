import pytest
from .app import check_up_token, check_notion_token
from unittest.mock import MagicMock
from .utils import (
    is_description_match,
    is_category_match,
    is_food_match,
    is_amount_match,
    push_to_notion,
    fetch_transactions,
    calculate_totals,
)
from unittest.mock import patch
import pandas as pd
import os

from .config import DATABASE_ID, NOTION_API_KEY


# Token Tests
def test_up_token_missing(monkeypatch):
    """Test that ValueError is raised if UP_API_TOKEN is not set."""
    monkeypatch.delenv("UP_API_TOKEN", raising=False)

    with pytest.raises(
        ValueError,
        match="Please set the UP_API_TOKEN environment variable in your .env file.",
    ):
        check_up_token()


def test_notion_token_missing(monkeypatch):
    """Test that ValueError is raised if NOTION_API_KEY is not set."""
    monkeypatch.delenv("NOTION_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="Please set the NOTION_API_KEY environment variable in your .env file.",
    ):
        check_notion_token()


@pytest.fixture
def mock_requests_post(mocker):
    """Fixture to mock requests.post."""
    return mocker.patch("requests.post")


def test_push_to_notion_valid_data(mock_requests_post):
    """Test push_to_notion with valid transaction data."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests_post.return_value = mock_response

    transaction_data = {
        "description": "Test Transaction",
        "amount": "100.50",
        "createdAt": "2024-11-19T12:34:56+0000",
    }

    push_to_notion(transaction_data)

    # Ensure requests.post was called with correct data
    expected_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": "Test Transaction"}}]},
            "Amount": {"number": 100.50},
            "createdAt": {"date": {"start": "2024-11-19T12:34:56+00:00"}},
        },
    }

    mock_requests_post.assert_called_once_with(
        "https://api.notion.com/v1/pages",
        headers={
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        json=expected_data,
    )


def test_push_to_notion_api_failure(mock_requests_post):
    """Test push_to_notion when the API call fails."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Invalid request"}
    mock_requests_post.return_value = mock_response

    transaction_data = {
        "description": "Test Transaction",
        "amount": "100.50",
        "createdAt": "2024-11-19T12:34:56+0000",
    }

    push_to_notion(transaction_data)

    # Ensure requests.post was called
    assert mock_requests_post.called


# Matching Test
def test_is_description_match():
    assert is_description_match("test", "test") is True
    assert is_description_match("test", "TEST") is True
    assert is_description_match("test description", "testdescription") is True
    assert is_description_match("  test  ", "test") is True
    # Test empty description (should match anything)
    assert is_description_match("test", "") is True
    assert is_description_match("", "") is True

    # Test partial matches
    assert is_description_match("this is a test description", "test") is True

    # Test when description does not match
    assert is_description_match("this is a test", "notfound") is False

    # Test empty transaction description (should not match anything)
    assert is_description_match("", "test") is False


def test_is_category_match():
    # Case 1: parent_category matches parent_category_info ID
    category_info = {"id": "fitness-and-wellbeing"}
    parent_category_info = {"id": "personal"}
    parent_category = ["personal"]
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is True
    )

    # Case 2: parent_category matches category_info ID
    category_info = {"id": "fitness-and-wellbeing"}
    parent_category_info = {"id": "personal"}
    parent_category = ["fitness-and-wellbeing"]
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is True
    )

    # Case 3: parent_category does not match any IDs
    category_info = {"id": "fitness-and-wellbeing"}
    parent_category_info = {"id": "personal"}
    parent_category = ["travel", "groceries"]
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is False
    )

    # Case 4: parent_category is empty
    category_info = {"id": "fitness-and-wellbeing"}
    parent_category_info = {"id": "personal"}
    parent_category = []
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is False
    )

    # Case 5: parent_category_info is None
    category_info = {"id": "fitness-and-wellbeing"}
    parent_category_info = None
    parent_category = ["fitness-and-wellbeing"]
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is True
    )

    # Case 6: category_info is None
    category_info = None
    parent_category_info = {"id": "personal"}
    parent_category = ["personal"]
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is True
    )

    # Case 7: Both category_info and parent_category_info are None
    category_info = None
    parent_category_info = None
    parent_category = ["personal"]
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is False
    )

    # Case 8: parent_category is None
    category_info = {"id": "fitness-and-wellbeing"}
    parent_category_info = {"id": "personal"}
    parent_category = None
    assert (
        is_category_match(category_info, parent_category_info, parent_category) is False
    )


def test_is_food_match():
    # Case 1: Match on "takeaway"
    transaction_description = "Test"
    category_info = {"id": "takeaway"}
    parent_category_info = {"id": "good-life"}

    # These are hard coded
    food_keywords = ["coles", "woolworths"]
    food_child_categories = {"restaurants-and-cafes", "takeaway"}
    food_parent_category = "good-life"
    assert (
        is_food_match(
            transaction_description,
            category_info,
            parent_category_info,
            food_keywords,
            food_child_categories,
            food_parent_category,
        )
        is True
    )

    # Case 2: Match on "restaurants-and-cafes"
    transaction_description = "Test"
    category_info = {"id": "restaurants-and-cafes"}
    parent_category_info = {"id": "good-life"}

    # These are hard coded
    food_keywords = ["coles", "woolworths"]
    food_child_categories = {"restaurants-and-cafes", "takeaway"}
    food_parent_category = "good-life"
    assert (
        is_food_match(
            transaction_description,
            category_info,
            parent_category_info,
            food_keywords,
            food_child_categories,
            food_parent_category,
        )
        is True
    )

    # Case 3: "booze" not a vaild food_child_categories
    transaction_description = "Test"
    category_info = {"id": "booze"}
    parent_category_info = {"id": "good-life"}

    # These are hard coded
    food_keywords = ["coles", "woolworths"]
    food_child_categories = {"restaurants-and-cafes", "takeaway"}
    food_parent_category = "good-life"
    assert (
        is_food_match(
            transaction_description,
            category_info,
            parent_category_info,
            food_keywords,
            food_child_categories,
            food_parent_category,
        )
        is False
    )

    # Case 4: "personal" not a vaild food_parent_category
    transaction_description = "Test"
    category_info = {"id": "life-admin"}
    parent_category_info = {"id": "personal"}

    # These are hard coded
    food_keywords = ["coles", "woolworths"]
    food_child_categories = {"restaurants-and-cafes", "takeaway"}
    food_parent_category = "good-life"
    assert (
        is_food_match(
            transaction_description,
            category_info,
            parent_category_info,
            food_keywords,
            food_child_categories,
            food_parent_category,
        )
        is False
    )


def test_is_amount_match():
    # within the range
    transaction = {"attributes": {"amount": {"value": "50"}}}
    assert is_amount_match(transaction, 30, 100) is True

    # min_amount as None, but amount within range
    transaction = {"attributes": {"amount": {"value": "100"}}}
    assert is_amount_match(transaction, None, 100) is True

    # max_amount as None, but amount within range
    transaction = {"attributes": {"amount": {"value": "1000"}}}
    assert is_amount_match(transaction, 30, None) is True

    # amount below the min_amount
    transaction = {"attributes": {"amount": {"value": "20"}}}
    assert is_amount_match(transaction, 30, 100) is False

    # Amount above the max_amount
    transaction = {"attributes": {"amount": {"value": "150"}}}
    assert is_amount_match(transaction, 30, 100) is False


# def test_fetch_transactions_success(mocker):
#     mock_response = Mock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = {"transactions": [{"id": "1", "amount": 100}]}
#     mocker.patch("requests.get", return_value=mock_response)
#     result = fetch_transactions("1234", since="2024-01-01", until="2024-12-31")
#     assert result == {"transactions": [{"id": "1", "amount": 100}]}
#     mock_response.json.assert_called_once()  # Ensure json() was called


# def test_fetch_transactions_failure(mocker):
#     mock_response = Mock()
#     mock_response.status_code = 400
#     mock_response.text = "Bad Request"
#     mocker.patch("requests.get", return_value=mock_response)
#     result = fetch_transactions("1234", since="2024-01-01", until="2024-12-31")
#     assert result == {"error": "Failed to retrieve data"}


# def test_calculate_totals_exceptions():
#     df_missing_column = pd.DataFrame({"Transaction": [100, -50, 200]})
#     with pytest.raises(ValueError, match="DataFrame is missing the 'Amount' column."):
#         calculate_totals(df_missing_column, "Test Account")

#     df_empty = pd.DataFrame(columns=["Amount"])
#     with patch("builtins.print") as mock_print:
#         calculate_totals(df_empty, "Test Account")
#         mock_print.assert_called_once_with(
#             "Warning: The DataFrame is empty. No transactions to process."
#         )
