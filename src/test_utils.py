import pytest
from .app import check_access_token
from unittest.mock import Mock
from .utils import fetch_transactions, calculate_totals
from unittest.mock import patch
import pandas as pd


def test_access_token_missing(monkeypatch):
    """Test that ValueError is raised if UP_API_TOKEN is not set."""
    monkeypatch.delenv("UP_API_TOKEN", raising=False)

    with pytest.raises(
        ValueError,
        match="Please set the UP_API_TOKEN environment variable in your .env file.",
    ):
        check_access_token()


def test_fetch_transactions_success(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"transactions": [{"id": "1", "amount": 100}]}
    mocker.patch("requests.get", return_value=mock_response)
    result = fetch_transactions("1234", since="2024-01-01", until="2024-12-31")
    assert result == {"transactions": [{"id": "1", "amount": 100}]}
    mock_response.json.assert_called_once()  # Ensure json() was called


def test_fetch_transactions_failure(mocker):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mocker.patch("requests.get", return_value=mock_response)
    result = fetch_transactions("1234", since="2024-01-01", until="2024-12-31")
    assert result == {"error": "Failed to retrieve data"}


def test_calculate_totals_exceptions():
    df_missing_column = pd.DataFrame({"Transaction": [100, -50, 200]})
    with pytest.raises(ValueError, match="DataFrame is missing the 'Amount' column."):
        calculate_totals(df_missing_column, "Test Account")

    df_empty = pd.DataFrame(columns=["Amount"])
    with patch("builtins.print") as mock_print:
        calculate_totals(df_empty, "Test Account")
        mock_print.assert_called_once_with(
            "Warning: The DataFrame is empty. No transactions to process."
        )
