import requests, os

# Constants
PRIVACY_API_ENDPOINT = "https://api.privacy.com/v1/"
YNAB_API_ENDPOINT = "https://api.youneedabudget.com/v1/"
PRIVACY_AUTH_TOKEN = os.environ.get('PRIVACY_API_TOKEN') or "PRIVACY_API_TOKEN"
YNAB_AUTH_TOKEN = os.environ.get('YNAB_API_TOKEN') or "YNAB_API_TOKEN"
YNAB_BUDGET_ID = os.environ.get('YNAB_BUDGET_ID') or "YNAB_BUDGET_ID"

# Connect to YNAB and fetch transactions
def get_ynab_transactions():
    headers = {
        "Authorization": f"Bearer {YNAB_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"{YNAB_API_ENDPOINT}budgets/{YNAB_BUDGET_ID}/transactions", headers=headers)
    data = response.json()

    # Filter for transactions from Privacy.com
    privacy_transactions = [txn for txn in data["data"]["transactions"] if "Pwp*privacy.com" in txn["payee_name"]]

    print(privacy_transactions)  # <--- Add this line to inspect the response
    
    return privacy_transactions

# Get detailed transaction info from Privacy.com
def get_privacy_transaction_details(date, amount):
    headers = {
        "Authorization": f"Bearer {PRIVACY_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    # You might need to adjust this based on the actual structure and capabilities of the Privacy.com API
    response = requests.get(f"{PRIVACY_API_ENDPOINT}transaction?date={date}&amount={amount}", headers=headers)
    data = response.json()

    return data

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

    response = requests.put(f"{YNAB_API_ENDPOINT}budgets/{YNAB_BUDGET_ID}/transactions/{transaction_id}", headers=headers, json=payload)
    return response.status_code == 200

# Main routine
def main():
    ynab_transactions = get_ynab_transactions()
    exit() # <--- Remove this line to continue
    for txn in ynab_transactions:
        date = txn["date"]
        amount = txn["amount"]
        privacy_details = get_privacy_transaction_details(date, amount)
        
        # Assuming 'description' is a field in the returned privacy details. Adjust if necessary.
        memo = privacy_details.get("description", "")
        update_ynab_transaction(txn["id"], memo)

if __name__ == "__main__":
    main()

