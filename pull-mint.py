import mintapi
import keyring
import datetime

username = keyring.get_keyring().get_password("budget-username", "username")
password = keyring.get_keyring().get_password("budget-password", "password")
ius_session = keyring.get_keyring().get_password("budget-ius_session", "ius_session")
thx_guid = keyring.get_keyring().get_password("budget-thx_guid", "thx_guid")
mint = mintapi.Mint(username, password, ius_session, thx_guid)
t = mint.get_transactions()
filename = "mint-transactions-{}.csv".format(datetime.datetime.now().isoformat()[:10])
t.to_csv(filename)
