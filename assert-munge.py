import pandas as pd
import unittest
import yaml
import glob
import datetime
from subprocess import call
from subprocess import Popen

def excel_name():
    "OO w/e"
    return "munged-{}.xlsx".format(datetime.datetime.now().isoformat()[:10])

class Munger():
    "Adds our budget category and generally cleans up the Mint data"
    def __init__(self, filename=None):
        csv = sorted(glob.glob('*.csv'))[-1]
        print ("Reading from %s" % csv)
        self.df = pd.read_csv(csv)
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df['year'] = self.df['date'].apply(lambda x: x.year)
        self.df['month'] = self.df['date'].apply(lambda x: x.month)
        self.df['month-year'] = self.df['date'].apply(lambda x: str(x.year) + '-' + ("%02d" % (x.month)))
        self.df = self.df[self.df.year >= 2017]

    def fix_paychecks(self, row):
        if row['transaction_type'] == 'debit':
            return row['amount'] * -1
        else:
            return row['amount']

    def munge(self):
        file = open('category_map.yaml', 'r')
        map = yaml.load(file)
        file.close()
        self.df['budget_category'] = self.df['category'].apply(map.get)
        self.df['amount'] = self.df.apply(lambda row: self.fix_paychecks(row), axis=1)
        self.df.to_excel(excel_name())

class AssertMungeTestCase(unittest.TestCase):
    def setUp(self):
        call(["taskkill", "/F", "/IM", "EXCEL.EXE"])
        self.m = Munger()
        self.m.munge()

    def test_all_transactions_have_budget_categories(self):
        no_budget_category = self.m.df[self.m.df.budget_category.isnull()]
        if len(no_budget_category) > 0:
            print("The following transactions have no budget category")
            print(no_budget_category)
            unittest.TestCase.assertEqual(self, 0, len(no_budget_category))

    def test_not_too_many_budget_categories(self):
        grouped = self.m.df.groupby(['budget_category'])
        too_many = 30
        how_many = len(grouped.aggregate(sum))
        unittest.TestCase.assertLessEqual(self, how_many, too_many,
                                          "How can you think about %s budget categories?" % how_many)

    @classmethod
    def tearDownClass(self):
        Popen(["C:/Program Files (x86)/Microsoft Office/root/Office16/EXCEL.EXE", excel_name()])