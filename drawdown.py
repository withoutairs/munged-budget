import subprocess
from dataclasses import dataclass
import logging
import xlsxwriter

# Set up logging handler
level = logging.INFO
logging.basicConfig(format='%(name)s: %(message)s', level=level)
logger = logging.getLogger('drawdown')

# Load the runtime info
with open('draw.txt', 'r') as file:
    r = file.read().rstrip()
with open('balances.txt', 'r') as file:
    b = file.read().rstrip()

@dataclass(order=True)
class Account:
    order: int
    name: str
    balance: int

accounts = []
for line in b.strip().splitlines():
    order, name, balance = line.split('\t')
    balance = balance.replace('$','')
    balance = balance.replace(',', '')
    balance = balance.split('.')[0]
    a = Account(int(order),name,int(balance))
    accounts.append(a)
accounts = sorted(accounts)

draws = []
for it in r.strip("\n").split("\t"):
    neg = not ('(') in it
    val = int(it.strip(" $()"))
    if neg:
        val *= -1
    draws.append(val)

# set up the worksheet
excel_filename = 'drawdown.xlsx'
workbook = xlsxwriter.Workbook(excel_filename)
worksheet = workbook.add_worksheet()

row = 1
col = 0

worksheet.write(row, 0, "Depletion order")
worksheet.write(row, 1, "Name")
worksheet.write(row, 2, "↓ Have // Want →")
worksheet.set_column('A:A', 10)
worksheet.set_column('B:B', 35)
worksheet.set_column('C:C', 17)
worksheet.set_column('D:AR', 11)
currency_format = workbook.add_format({'num_format': '$#,##0.00'})

row = 2

# the accounts on the left
for a in accounts:
    worksheet.write(row, 0, a.order)
    worksheet.write(row, 1, a.name)
    worksheet.write(row, 2, a.balance, currency_format)
    row += 1

# the months and draws across the top
row = 0
worksheet.write(row, 2, "Months From Now →")
col = 3
for d in draws:
    worksheet.write(0, col, col - 3)
    worksheet.write(1, col, d, currency_format)
    col += 1

# now run the drawdown analysis
col = 2
months = range(len(draws))
for m in months:
    logger.debug("\n\n" + "M" * 12)
    logger.debug("month " + str(m))
    logger.debug("accounts " + str(accounts))
    want = draws[m]
    logger.debug("want to draw " + str(want))
    lose = False
    row = 1
    col += 1
    for i in range(len(accounts)):
        row += 1
        logger.debug("B" * 12)
        if accounts[i].balance == 0:
            logger.debug("balance #" + str(i) + " (" + accounts[i].name + ") is 0, skipping")
            continue
        elif (accounts[i].balance - want) < 0:
            logger.info("month " + str(m) + ", balance #" + str(i) + " (" + accounts[i].name + ") of $" + str(accounts[i].balance) + " minus $" + str(
                want) + " is less than 0, depleting")
            want = want - accounts[i].balance
            accounts[i].balance = 0
            logger.debug("now want $" + str(want) + " and balances are " + str(accounts))
            worksheet.write(row, col, accounts[i].balance, currency_format)
            if accounts[len(accounts) - 1].balance == 0:
                lose = True
                logger.info("Out of money in month " + str(m))
                break
        else:
            logger.debug("balance #" + str(i) + " (" + accounts[i].name + ") of $" + str(accounts[i].balance) + " minus $" + str(
                want) + " is sufficient")
            accounts[i].balance = accounts[i].balance - want
            worksheet.write(row, col, accounts[i].balance, currency_format)
            want = 0
            logger.debug("now want $" + str(want) + " and balances are " + str(accounts))
            break
    if lose:
        break
logger.info("End---Lose? " + str(lose))
workbook.close()
subprocess.call(["open", excel_filename])