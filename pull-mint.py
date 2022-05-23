import mintapi
import datetime
import os

username = os.environ['MINT_USERNAME']
password = os.environ['MINT_PASSWORD']
mfa_token = os.environ['MFA_TOKEN']
mint = mintapi.Mint(username, password, headless=False, mfa_method='soft-token', mfa_token=mfa_token)
t = mint.get_transactions()
filename = "mint-transactions-{}.csv".format(datetime.datetime.now().isoformat()[:10])
t.to_csv(filename)