import pandas as pd
import unittest
class Munger():
    "Adds our budget category and generally cleans up the Mint data"
    def __init__(self, filename=None):
        self.df = pd.read_csv('mint-transactions-2017-09-22.csv')
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
    def munge(self):
        print("here")

class AssertMungeTestCase(unittest.TestCase):
    def setUp(self):
        self.m = Munger()

    def test_not_too_many_budget_categories(self):
        grouped = self.m.df.groupby(['category'])
        too_many = 30
        how_many = len(grouped.aggregate(sum))
        unittest.TestCase.assertLessEqual(self, how_many, too_many,
                                          "How can you think about %s budget categories?" % how_many)