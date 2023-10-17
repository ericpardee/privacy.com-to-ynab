import requests
import os
import sys
from datetime import datetime, timedelta

# Constants
PRIVACY_API_ENDPOINT = "https://api.privacy.com/v1/"
YNAB_API_ENDPOINT = "https://api.youneedabudget.com/v1/"
PRIVACY_AUTH_TOKEN = os.environ.get('PRIVACY_API_TOKEN') or "PRIVACY_API_TOKEN"
YNAB_AUTH_TOKEN = os.environ.get('YNAB_API_TOKEN') or "YNAB_API_TOKEN"
YNAB_BUDGET_ID = os.environ.get('YNAB_BUDGET_ID') or "YNAB_BUDGET_ID"
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
PRIVACY_DESCRIPTOR = os.environ.get('PRIVACY_DESCRIPTOR', 'Pwp*privacy.com') # how privacy.com transactions appear in YNAB
PRIVACY_PAGE_SIZE = int(os.environ.get('PRIVACY_PAGE_SIZE', '50')) # how many transactions to fetch from privacy.com at a time

def debug_print(*args, **kwargs):
    """Prints only if DEBUG flag is set."""
    if DEBUG:
        print(*args, **kwargs, end='\n\n')

# Connect to YNAB and fetch transactions
def get_ynab_transactions():
    headers = {
        "Authorization": f"Bearer {YNAB_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{YNAB_API_ENDPOINT}budgets/{YNAB_BUDGET_ID}/transactions", headers=headers)
        response.raise_for_status()  # Raise an error if the response contains an HTTP error status
        data = response.json()

        privacy_transactions = [txn for txn in data["data"]["transactions"] if PRIVACY_DESCRIPTOR in txn["payee_name"] and txn["memo"] in [None, ""]]
        debug_print("YNAB privacy transactions:\n", privacy_transactions)
        return privacy_transactions
    except requests.RequestException as e:
        print(f"Error fetching transactions from YNAB: {e}")
        sys.exit(1)

# Get detailed transaction info from Privacy.com
def get_privacy_transaction_details(date, ynab_amount):
    headers = {
        "Authorization": f"api-key {PRIVACY_AUTH_TOKEN}",
        "Accept": "application/json"
    }

    # Convert the date to the desired 8601 format
    txn_date = datetime.strptime(date, "%Y-%m-%d")
    begin_date = txn_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Start of the day
    end_date = (txn_date + timedelta(days=1) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # End of the day
    
    # Fetching the list of transactions
    response = requests.get(f"{PRIVACY_API_ENDPOINT}transactions?begin={begin_date}&end={end_date}&page=1&page_size={PRIVACY_PAGE_SIZE}", headers=headers)
    data = response.json()
    
    debug_print("Privacy API response:\n", data)

    # Convert ynab amount to privacy.com format
    privacy_amount = abs(int(ynab_amount)) // 10  # Convert milli units to cent units
    debug_print(f"Privacy amount: {privacy_amount}")

    # Find the transaction with the matching amount
    for txn in data["data"]:
        if txn["amount"] == privacy_amount:
            debug_print(f"Found transaction: {txn['merchant']['descriptor']}")
            return txn["merchant"]["descriptor"]

    # If no transaction is found
    return None

# Update YNAB transaction
def update_ynab_transaction(transaction_id, memo):
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

# Main routine
def main():
    ynab_transactions = get_ynab_transactions()
    for txn in ynab_transactions:
        date = txn["date"]
        amount = txn["amount"]
        memo = get_privacy_transaction_details(date, amount)

        if memo:
            update_ynab_transaction(txn["id"], memo)

if __name__ == "__main__":
    main()
