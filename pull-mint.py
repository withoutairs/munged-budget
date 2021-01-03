import mintapi
import keyring
import datetime
import os

username = keyring.get_keyring().get_password("budget-username", "username")
password = keyring.get_keyring().get_password("budget-password", "password")
mint = mintapi.Mint(username, password, headless=True, mfa_method='soft-token', mfa_token=os.environ['MFA_TOKEN'])
t = mint.get_transactions()
filename = "mint-transactions-{}.csv".format(datetime.datetime.now().isoformat()[:10])
t.to_csv(filename)
