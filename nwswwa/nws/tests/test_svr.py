__author__ = 'Aaron Anderson'

import unittest
import datetime
import os

import pytz

from nwswwa.nws import product, ugc
from nwswwa.nws.product import WMO_RE
from nwswwa.nws.product import TextProductException
from nwswwa import parse as productparser

def get_file(name):
    ''' Helper function to get the text file contents '''
    basedir = os.path.dirname(__file__)
    fn = "%s/../../../data/product_examples/%s" % (basedir, name)
    return open(fn).read()

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.product = product.TextProduct(get_file('SVROK_453.txt'))

    def test_afos(self):
        self.assertEqual('SVROUN', self.product.afos)

    def test_segments(self):
        self.assertEqual(2,len(self.product.segments))


if __name__ == '__main__':
    unittest.main()
