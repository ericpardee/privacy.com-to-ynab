import pytest
from app import ynab_to_privacy_amount, get_privacy_transaction_details

# Sample mock data
mock_privacy_transactions = [
    {"amount": 7188, "merchant": {"descriptor": "WASTE MGMT WM EZPAY"}},
    {"amount": 5000, "merchant": {"descriptor": "SOME MERCHANT"}}
]

def test_ynab_to_privacy_amount():
    # Existing tests
    assert ynab_to_privacy_amount(71880) == 7188
    assert ynab_to_privacy_amount(-71880) == 7188

    # Test zero amount
    assert ynab_to_privacy_amount(0) == 0

    # Test decimal amounts
    assert ynab_to_privacy_amount(71885) == 7188  # I don't know how YNAB rounds, so I'm just going to round down
    assert ynab_to_privacy_amount(71882) == 7188  # Rounding down

    # Test very large amounts
    assert ynab_to_privacy_amount(1000000000) == 100000000
    assert ynab_to_privacy_amount(-1000000000) == 100000000

def test_get_privacy_transaction_details():
    # Existing tests
    assert get_privacy_transaction_details(7188, mock_privacy_transactions.copy()) == "WASTE MGMT WM EZPAY"
    assert get_privacy_transaction_details(5000, mock_privacy_transactions.copy()) == "SOME MERCHANT"
    assert get_privacy_transaction_details(9999, mock_privacy_transactions.copy()) == None
    assert get_privacy_transaction_details(7188, mock_privacy_transactions.copy() * 2) == "WASTE MGMT WM EZPAY"
    assert get_privacy_transaction_details(7188, mock_privacy_transactions.copy() * 2) == "WASTE MGMT WM EZPAY"

    # Test with empty transaction list
    assert get_privacy_transaction_details(7188, []) == None

    # Test with transactions missing 'amount' or 'merchant' keys
    broken_transactions = [{"merchant": {"descriptor": "MISSING AMOUNT"}}]
    assert get_privacy_transaction_details(0, broken_transactions) == None

    broken_transactions = [{"amount": 1234}]
    assert get_privacy_transaction_details(1234, broken_transactions) == None

    # Test with transactions having malformed descriptors
    malformed_transactions = [{"amount": 9999, "merchant": {"descriptor": 12345}}]  # descriptor as int
    assert get_privacy_transaction_details(9999, malformed_transactions) == None
