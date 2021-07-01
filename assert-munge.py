import pandas as pd
import unittest
import yaml
import glob
import datetime
import os

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
        self.df['category'] = self.df['category'].apply(lambda x: str(x).lower())
        self.df['month'] = self.df['date'].apply(lambda x: x.month)
        self.df['month-year'] = self.df['date'].apply(lambda x: str(x.year) + '-' + ("%02d" % (x.month)))
        self.df['year-week'] = self.df['date'].apply(lambda x: str(x.year) + '-' + ("%02d" % x.weekofyear))
        self.df = self.df[self.df.year >= 2017]

    def fix_paychecks(self, row):
        if row['transaction_type'] == 'debit':
            return row['amount'] * -1
        else:
            return row['amount']

    def munge(self):
        file = open('category_map.yaml', 'r')
        map = yaml.load(file, Loader=yaml.FullLoader)
        file.close()
        self.df['budget_category'] = self.df['category'].apply(map.get)
        self.df['amount'] = self.df.apply(lambda row: self.fix_paychecks(row), axis=1)
        self.df['description'] = self.df.apply(lambda row: self.fix_descriptions(row), axis=1)
        self.df.to_excel(excel_name())

    def fix_descriptions(self, row):
        if row['description'].startswith('OCULUS *'):
            return "Oculus"
        if row['description'].startswith('RALLY HEALTH INC '):
            return "RALLY HEALTH INC "
        if row['description'].startswith('Prime Video'):
            return "Prime Video"
        if row['description'].startswith('POTOMAC ELEC'):
            return "POTOMAC ELEC"
        if row['description'].startswith('To Loan 01'):
            return "To Loan 01"
        if row['description'].startswith('AMZNGrocery'):
            return "AMZNGrocery"
        if row['description'].startswith('UNITED 016'):
            return "UNITED"

        if row['description'].startswith('Prime Now'):
            return "Prime Now"
        if row['description'].startswith('PrimeNowTips'):
            return "Prime Now"
        if row['description'].startswith('PrimeNowMktp'):
            return "Prime Now"

        else:
            return row['description']

class AssertMungeTestCase(unittest.TestCase):
    def setUp(self):
        self.m = Munger()
        self.m.munge()

    def test_all_transactions_have_budget_categories(self):
        no_budget_category = self.m.df[self.m.df.budget_category.isnull()]
        pd.set_option('display.max_columns', 500)
        no_budget_category = no_budget_category[['date', 'description', 'amount', 'category']]
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
        os.system("open " + excel_name())