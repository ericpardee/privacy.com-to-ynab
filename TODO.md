# TODO

- [ ] There's an issue with checking on the date...

Here's a privacy.com transaction:
> {'amount': 1800, 'authorization_amount': 1800, 'merchant_amount': 1800, 'merchant_authorization_amount': 1800, 'merchant_currency': 'USD', 'acquirer_fee': 0, 'created': '2023-10-13T00:45:40Z', 'events': [], 'merchant': {'acceptor_id': '382339000217339', 'city': '800-624-1662', 'country': 'USA', 'descriptor': 'AAA LIFE INSURANCE', 'mcc': '6300', 'state': 'MI'}, 'network': 'VISA', 'result': 'APPROVED', 'settled_amount': 1800, 'status': 'SETTLED', 'token': 'f3802f75-c841-402f-aeb5-28b6e2d36c72', 'card_token': '8d4e5348-0d1f-4625-ba01-f7f6293b99af', 'authorization_code': '195497', 'cardholder_authentication': None, 'acquirer_reference_number': None}

but if you look in YNAB, it's Date is 10/16/2023
> {'id': '901e31d4-1508-4dfb-b106-6b69ebc26d66', 'date': '2023-10-16', 'amount': -18000, 'memo': None, 'cleared': 'cleared', 'approved': False, 'flag_color': None, 'account_id': '26cdae1f-0bec-40ee-bd2b-de10204bbc67', 'account_name': 'NFCU EveryDay Checking Eric', 'payee_id': 'fbe98463-471c-4bcf-b2d2-731d164ac280', 'payee_name': 'Pos Debit- 0597 0597 Pwp*privacy.com', 'category_id': None, 'category_name': 'Uncategorized', 'transfer_account_id': None, 'transfer_transaction_id': None, 'matched_transaction_id': None, 'import_id': 'YNAB:-18000:2023-10-16:1', 'import_payee_name': 'Pos Debit- 0597 0597 Pwp*privacy.com', 'import_payee_name_original': 'Pos Debit-    0597 0597 Pwp*privacy.com 844-7718229 NY', 'debt_transaction_type': None, 'deleted': False, 'subtransactions': []}

If I give the privacy window room, the code as of (72e1ba9e4) will work, but it gets a lot more messy because it's very plausible that there's a same amount spent on transactions on different days. Ultimately though, since YNAB has the 'made aware' date, not the date of transaction, that might not matter. It just gets really sloppy.

- [ ] Update YNAB Category for known merchants
- [ ] Add tests
