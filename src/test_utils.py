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
    ACCESS_TOKEN,
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


@pytest.fixture
def mock_requests_get(mocker):
    """Fixture to mock requests.get."""
    return mocker.patch("requests.get")


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data returned by the API."""
    return {
        "data": [
            {
                "id": "tx1",
                "attributes": {
                    "description": "Coles Supermarket",
                },
                "relationships": {
                    "category": {"data": {"id": "groceries"}},
                    "parentCategory": {"data": {"id": "good-life"}},
                },
            },
            {
                "id": "tx2",
                "attributes": {
                    "description": "Movie Theater",
                },
                "relationships": {
                    "category": {"data": {"id": "entertainment"}},
                    "parentCategory": {"data": {"id": "good-life"}},
                },
            },
        ],
        "links": {"next": None},  # Simulate single-page response
    }


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def sample_transaction_data():
    return {
        "data": [
            {
                "id": "tx1",
                "attributes": {
                    "description": "Coles Supermarket",
                    "amount": {"value": "100.00", "currency": "AUD"},
                    "createdAt": "2023-01-01T12:00:00+10:00",
                },
                "relationships": {
                    "category": {"data": {"id": "groceries"}},
                    "parentCategory": {"data": {"id": "good-life"}},
                },
            }
        ],
        "links": {"next": None},
    }


@patch("src.config.ACCOUNT_IDS", {"account_id": "12345"})
@patch("src.utils.ACCESS_TOKEN", "mock_access_token")
def test_fetch_transactions(mock_requests_get, sample_transaction_data):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_transaction_data
    mock_requests_get.return_value = mock_response

    result = fetch_transactions(account_id=["12345"], since=None, until=None)
    mock_requests_get.assert_called_once_with(
        "https://api.up.com.au/api/v1/accounts/12345/transactions",
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/json",
        },
        params={"filter[since]": None, "filter[until]": None, "page[size]": 100},
    )

    assert "transactions" in result
    assert len(result["transactions"]) == 1
    assert result["transactions"][0]["id"] == "tx1"


@patch("src.config.ACCOUNT_IDS", {"account_id": "12345"})
@patch("src.utils.ACCESS_TOKEN", "mock_access_token")
def test_fetch_transactions_failing_get_request(mock_requests_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not Found"}
    mock_requests_get.return_value = mock_response

    result = fetch_transactions(account_id=["12345"], since=None, until=None)
    mock_requests_get.assert_called_once_with(
        "https://api.up.com.au/api/v1/accounts/12345/transactions",
        headers={
            "Authorization": "Bearer mock_access_token",
            "Content-Type": "application/json",
        },
        params={"filter[since]": None, "filter[until]": None, "page[size]": 100},
    )

    assert result == {"error": "Failed to retrieve data"}
