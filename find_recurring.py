import glob
import csv
import logging
import os
import sys
import sqlite3

# Set up logging handler
level = logging.DEBUG
logging.basicConfig(format='%(name)s %(levelname)s: %(message)s', level=level)
logger = logging.getLogger(os.path.basename(sys.argv[0]).split(os.extsep)[0])

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table transactions (id, date, description, amount)")

# load the CSV
fname = sorted(glob.glob('*.csv'))[-1]
since = "2023-01"
logger.info("Reading from %s, all transactions since %s" % (fname, str(since)))

n = 1
with open(fname, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # header
    for row in reader:
        if row[0][:7] >= since:
            cur.execute("insert into transactions values (?, ?, ?, ?)", (n, row[0], row[1], float(row[2])))
            con.commit()
            n = n + 1

cur.execute("select count(*) from transactions")
transaction_count = cur.fetchall()[0][0]
logger.info("transaction_count=" + str(transaction_count))

# same name and amount but different ID's
# for row in con.execute("select * from transactions t1 where exists (select * from transactions t2 where t1.id <> t2.id and t1.description = t2.description and t1.amount = t2.amount"") order by t1.description, t1.id desc"): print(row)


# same amount but different ID's
with open('maybe_recurring.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(con.execute("""
select *
from transactions t1
where exists (
select *
from transactions t2
where t1.id <> t2.id and abs(t1.amount - t2.amount) < 0.01)
order by t1.amount
"""))

con.close()
