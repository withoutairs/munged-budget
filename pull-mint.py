import mintapi
import datetime
import os
import pandas

username = os.environ['MINT_USERNAME']
password = os.environ['MINT_PASSWORD']
mfa_token = os.environ['MFA_TOKEN']
mint = mintapi.Mint(username, password, headless=False, mfa_method='soft-token', mfa_token=mfa_token)
t = mint.get_transaction_data()
filename = "mint-transactions-{}.csv".format(datetime.datetime.now().isoformat()[:10])
pandas.json_normalize(t)[['date','description','amount','category.name','isExpense']].to_csv(index=False,path_or_buf=filename)
