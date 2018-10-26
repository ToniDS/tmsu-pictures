import unittest
import sys, os
import subprocess
testdir = os.path.dirname(__file__)
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
import database


class DataBaseTestCase(unittest.TestCase):
    def setUp(self):
        """Create a new database with the pictures that are in this directory.
        """
        subprocess.Popen(['tmsu', 'init'],
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def test_database_connection(self):
        tm = db.TmsuConnect()
        self.assertTrue(len(tm.get_tags()) == 0)

    def cleanUp(self):
        subprocess.Popen(['rm', '-rf', '.tmsu'])
