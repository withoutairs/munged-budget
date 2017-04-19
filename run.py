import mintapi
import keyring
import datetime

username = keyring.get_keyring().get_password("budget", "username")
password = keyring.get_keyring().get_password("budget", "password")
ius_session = keyring.get_keyring().get_password("budget", "ius_session")
thx_guid = keyring.get_keyring().get_password("budget", "thx_guid")
mint = mintapi.Mint(username, password, ius_session, thx_guid)
t = mint.get_transactions()
filename = "mint-transactions-{}.csv".format(datetime.datetime.now().isoformat()[:10])
t.to_csv(filename)

grouped = t.groupby(['category','transaction_type', t.date.dt.year, t.date.dt.month])
grouped.aggregate(sum)
