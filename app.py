import requests
import os
import sys
from datetime import datetime, timedelta
import json

# Constants
# API endpoints for Privacy.com and YNAB
PRIVACY_API_ENDPOINT = "https://api.privacy.com/v1/"
YNAB_API_ENDPOINT = "https://api.youneedabudget.com/v1/"

# Get authentication tokens and budget ID from environment variables or default values
PRIVACY_AUTH_TOKEN = os.environ.get('PRIVACY_API_TOKEN') or "PRIVACY_API_TOKEN"
YNAB_AUTH_TOKEN = os.environ.get('YNAB_API_TOKEN') or "YNAB_API_TOKEN"
YNAB_BUDGET_ID = os.environ.get('YNAB_BUDGET_ID') or "YNAB_BUDGET_ID"

# Debug flag for verbose output
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# Descriptor to identify Privacy.com transactions in YNAB
PRIVACY_DESCRIPTOR = os.environ.get('PRIVACY_DESCRIPTOR', 'Pwp*privacy.com')

# Setting the number of transactions to fetch from privacy.com at once
PRIVACY_PAGE_SIZE = int(os.environ.get('PRIVACY_PAGE_SIZE', '50'))

def debug_print(*args, **kwargs):
    """Utility function to print debug messages if the DEBUG flag is set."""
    if DEBUG:
        print(*args, **kwargs, end='\n\n')

def ynab_to_privacy_amount(ynab_amount):
    """
    Convert YNAB's milliunit format to Privacy.com's integer representation.
    For example, YNAB represents $71.88 outflow as -71880, which is converted to 7188 for Privacy.com.
    """
    return abs(int(ynab_amount)) // 10

def get_ynab_transactions():
    """
    Fetch transactions from YNAB that match the PRIVACY_DESCRIPTOR.
    
    Returns:
        List of transactions that match the PRIVACY_DESCRIPTOR.
    """
    headers = {
        "Authorization": f"Bearer {YNAB_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{YNAB_API_ENDPOINT}budgets/{YNAB_BUDGET_ID}/transactions", headers=headers)
        response.raise_for_status()
        data = response.json()
        privacy_transactions = [txn for txn in data["data"]["transactions"] if PRIVACY_DESCRIPTOR in txn["payee_name"] and txn["memo"] in [None, ""]]
        # Count of transactions
        transaction_count = len(privacy_transactions)
        if transaction_count > 1:
            start_date = privacy_transactions[0]['date']
            end_date = privacy_transactions[-1]['date']
            message = f"YNAB privacy transactions ({transaction_count} total) between {start_date} and {end_date}:\n"
        else:
            message = f"YNAB privacy transactions ({transaction_count} total):\n"
        # Formatting the transactions for more readable output
        formatted_transactions = json.dumps(privacy_transactions, indent=2)
        debug_print(message, formatted_transactions)
        return privacy_transactions
    except requests.RequestException as e:
        print(f"Error fetching transactions from YNAB: {e}")
        sys.exit(1)

def fetch_privacy_transactions(start_date, end_date):
    """
    Fetch transactions from Privacy.com within a specified date range.

    Args:
        start_date: Start date for transaction range.
        end_date: End date for transaction range.

    Returns:
        List of transactions from Privacy.com within the specified date range.
    """
    headers = {
        "Authorization": f"api-key {PRIVACY_AUTH_TOKEN}",
        "Accept": "application/json"
    }
    begin_date = start_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    end_date = (end_date + timedelta(days=1) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    try:
        # Fetch Privacy.com transactions in the date range where YNAB transactions were marked as Privacy.com transactions and not updated
        response = requests.get(f"{PRIVACY_API_ENDPOINT}transactions?begin={begin_date}&end={end_date}&page=1&page_size={PRIVACY_PAGE_SIZE}", headers=headers)
        response.raise_for_status()
        data = response.json()
        # Exclude transactions that have "authorization_amount": 0, as they are not actual transactions
        filtered_transactions = [transaction for transaction in data["data"] if transaction['authorization_amount'] != 0]
        # Sorting transactions in ascending order based on the 'created' timestamp
        sorted_transactions = sorted(filtered_transactions, key=lambda x: x['created'])
        transaction_count = len(sorted_transactions)
        # Formatting the response data for more readable output
        formatted_data = json.dumps(sorted_transactions, indent=2)
        debug_print(f"Privacy transactions between {begin_date} and {end_date} ({transaction_count} transactions):\n", formatted_data)
        return sorted_transactions
    except requests.RequestException as e:
        print(f"Error fetching transactions from Privacy.com: {e}")
        sys.exit(1)

def get_privacy_transaction_details(privacy_amount, privacy_transactions):
    """
    Retrieve the merchant descriptor for a Privacy.com transaction based on its amount.

    Args:
        privacy_amount: Transaction amount to search for.
        privacy_transactions: List of Privacy.com transactions to search through.

    Returns:
        Merchant descriptor for the matching transaction or None if not found.
    """
    for index, txn in enumerate(privacy_transactions):
        if txn["amount"] == privacy_amount:
            # Remove the matched transaction from the list to prevent multiple matches
            privacy_transactions.pop(index)
            return txn["merchant"]["descriptor"]
    return None

def update_ynab_transaction(transaction_id, memo):
    """
    Update the memo of a YNAB transaction.

    Args:
        transaction_id: ID of the YNAB transaction to update.
        memo: New memo to set for the transaction.
    """
    headers = {
        "Authorization": f"Bearer {YNAB_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "transaction": {
            "memo": memo
        }
    }
    try:
        response = requests.put(f"{YNAB_API_ENDPOINT}budgets/{YNAB_BUDGET_ID}/transactions/{transaction_id}", headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error updating YNAB transaction {transaction_id}: {e}")

def main():
    """Main routine to update YNAB transactions' memos based on Privacy.com data."""
    ynab_transactions = get_ynab_transactions()
    if not ynab_transactions:
        return

    dates = [datetime.strptime(txn["date"], "%Y-%m-%d") for txn in ynab_transactions]
    start_date = min(dates)
    end_date = max(dates)
    privacy_transactions = fetch_privacy_transactions(start_date, end_date)

    for txn in ynab_transactions:
        privacy_amount = ynab_to_privacy_amount(txn["amount"])
        memo = get_privacy_transaction_details(privacy_amount, privacy_transactions)

        if memo:
            update_ynab_transaction(txn["id"], memo)
            debug_print(f"Updated transaction {txn['id']} on {txn['date']} for amount ${privacy_amount / 100:.2f} with memo {memo}")

if __name__ == "__main__":
    main()
