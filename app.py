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

def ynab_to_privacy_amount(ynab_amount):
    """Convert YNAB's milliunit format to Privacy.com's integer representation."""
    return abs(int(ynab_amount)) // 10

# Connect to YNAB and fetch transactions matching the privacy descriptor
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

def fetch_privacy_transactions(start_date, end_date):
    headers = {
        "Authorization": f"api-key {PRIVACY_AUTH_TOKEN}",
        "Accept": "application/json"
    }
    
    begin_date = start_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    end_date = (end_date + timedelta(days=1) - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    try:
        response = requests.get(f"{PRIVACY_API_ENDPOINT}transactions?begin={begin_date}&end={end_date}&page=1&page_size={PRIVACY_PAGE_SIZE}", headers=headers)
        response.raise_for_status() # Ensure valid response
        data = response.json()
        debug_print(f"Privacy transactions between {begin_date} and {end_date}:\n", data)
        return data["data"]
    except requests.RequestException as e:
        print(f"Error fetching transactions from Privacy.com: {e}")
        sys.exit(1)

# Find the privacy transaction description based on the ynab_amount from the locally fetched list
def get_privacy_transaction_details(privacy_amount, privacy_transactions):
    for index, txn in enumerate(privacy_transactions):
        if txn["amount"] == privacy_amount:
            # Remove the transaction from the list and return the descriptor
            privacy_transactions.pop(index)
            return txn["merchant"]["descriptor"]
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
