import pandas as pd
import unittest
import yaml
import glob
import datetime
from subprocess import call

class Munger():
    "Adds our budget category and generally cleans up the Mint data"
    def __init__(self, filename=None):
        csv = sorted(glob.glob('*.csv'))[-1]
        print ("Reading from %s" % csv)
        self.df = pd.read_csv(csv)
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df['year'] = self.df['date'].apply(lambda x: x.year)
        self.df = self.df[self.df.year >= 2017]

    def munge(self):
        file = open('category_map.yaml', 'r')
        map = yaml.load(file)
        file.close()
        self.df['budget_category'] = self.df['category'].apply(map.get)
        excel = "munged-{}.xlsx".format(datetime.datetime.now().isoformat()[:10])
        self.df.to_excel(excel)

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