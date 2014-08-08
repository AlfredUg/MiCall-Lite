import StringIO
import unittest

import csf2counts

class Csf2CountsTest(unittest.TestCase):
    def setUp(self):
        self.aafile = StringIO.StringIO()
        self.amino_counts = {}
        self.qindex_to_refcoord = {}
        self.inserts = []
        self.refseqs = {'R1': 'XXX'}
        self.region = 'R1'
        self.qcut = 15
        
    def testUnmappedRegion(self):
        expected_text = ''
        
        csf2counts.write_amino_frequencies(self.aafile,
                                           self.amino_counts,
                                           self.qindex_to_refcoord,
                                           self.inserts,
                                           self.refseqs,
                                           self.region,
                                           self.qcut)
        
        self.assertEqual(self.aafile.getvalue(), expected_text)
        
    def testStartOfRegion(self):
        self.amino_counts = {0: {'Q': 1}, 1: {'R': 1}, 2: {'S': 1}}
        self.qindex_to_refcoord = {0:0, 1:1, 2:2}
        expected_text = """\
R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
R1,15,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
R1,15,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
"""

        
        csf2counts.write_amino_frequencies(self.aafile,
                                           self.amino_counts,
                                           self.qindex_to_refcoord,
                                           self.inserts,
                                           self.refseqs,
                                           self.region,
                                           self.qcut)
        
        self.assertEqual(self.aafile.getvalue(), expected_text)
