import StringIO
import unittest

import csf2counts

class AminoWriterTest(unittest.TestCase):
    def setUp(self):
        self.writer = csf2counts.AminoFrequencyWriter(aafile=StringIO.StringIO(),
                                                      refseqs = {'R1': 'XXX',
                                                                 'R2': 'YYYY'})
        
    def testUnmappedRegion(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
"""
        
        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={},
                          amino_counts={},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)
        
    def testWriteAminosFullRegion(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
E1234_S1,R1,15,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
E1234_S1,R1,15,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
"""
        
        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:0, 1:1, 2:2},
                          amino_counts={0: {'Q': 1}, 1: {'R': 1}, 2: {'S': 1}},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)
        
    def testWriteAminosEndOfRegion(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
E1234_S1,R1,15,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
E1234_S1,R1,15,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
"""

        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:1, 1:2},
                          amino_counts={1: {'R': 1}, 2: {'S': 1}},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)
        
    def testWriteAminosStartOfRegion(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
E1234_S1,R1,15,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
E1234_S1,R1,15,,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
"""

        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:0, 1:1},
                          amino_counts={0: {'Q': 1}, 1: {'R': 1}},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)
        
    def testWriteAminosWithInsert(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
E1234_S1,R1,15,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
E1234_S1,R1,15,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
"""

        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:0, 2:1, 3:2},
                          amino_counts={0: {'Q': 1},
                                        1: {'F': 1}, # This is the insert
                                        2: {'R': 1},
                                        3: {'S': 1}},
                          inserts=[1])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)
        
    def testWriteAminosWithDeletion(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
E1234_S1,R1,15,,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
E1234_S1,R1,15,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
"""

        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:0, 1:2},
                          amino_counts={0: {'Q': 1}, 1: {'S': 1}},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)
        
    def testWriteAminosWithGap(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
E1234_S1,R1,15,,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
E1234_S1,R1,15,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
"""
        
        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:0, 2:2},
                          amino_counts={0: {'Q': 1}, 2: {'S': 1}},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)

        
    def testWriteAminosTwoRegions(self):
        expected_text = """\
sample,region,q-cutoff,query.aa.pos,refseq.aa.pos,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y,*
E1234_S1,R1,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
E1234_S1,R1,15,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
E1234_S1,R1,15,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
E1234_S1,R2,15,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0
E1234_S1,R2,15,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
E1234_S1,R2,15,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0
E1234_S1,R2,15,3,4,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
"""
        
        self.writer.write(sample_name = 'E1234_S1',
                          region='R1',
                          qcut=15,
                          qindex_to_refcoord={0:0, 1:1, 2:2},
                          amino_counts={0: {'Q': 1}, 1: {'R': 1}, 2: {'S': 1}},
                          inserts=[])
        self.writer.write(sample_name = 'E1234_S1',
                          region='R2',
                          qcut=15,
                          qindex_to_refcoord={0:0, 1:1, 2:2, 3:3},
                          amino_counts={0: {'T': 1}, 1: {'S': 1}, 2: {'R': 1}, 3: {'Q': 1}},
                          inserts=[])
        
        self.assertEqual(self.writer.aafile.getvalue(), expected_text)

class CoordinateMapTest(unittest.TestCase):
    def testStraightMapping(self):
        query_sequence =     'CTRPNNN'
        reference_sequence = 'CTRPNNN'
        expected_inserts = []
        expected_mapping = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(qindex_to_refcoord, expected_mapping)
        self.assertEqual(inserts, expected_inserts)
        
    def testInsertion(self):
        query_sequence =     'CTNPRPNNN'
        reference_sequence = 'CT--RPNNN'
        expected_inserts = [2, 3]
        expected_mapping = {0:0, 1:1, 4:2, 5:3, 6:4, 7:5, 8:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(expected_mapping, qindex_to_refcoord)
        self.assertEqual(expected_inserts, inserts)
        
    def testDeletion(self):
        query_sequence =     'CT--NNN'
        reference_sequence = 'CTRPNNN'
        expected_inserts = []
        expected_mapping = {0:0, 1:1, 2:4, 3:5, 4:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(expected_mapping, qindex_to_refcoord)
        self.assertEqual(expected_inserts, inserts)
        
    def testDeletionAndInsertion(self):
        query_sequence =     'CT--NNCPN'
        reference_sequence = 'CTRPNN--N'
        expected_inserts = [4, 5] # note that these are the non-blank indexes
        expected_mapping = {0:0, 1:1, 2:4, 3:5, 6:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(qindex_to_refcoord, expected_mapping)
        self.assertEqual(inserts, expected_inserts)
        
    def testQueryStartsBeforeReference(self):
        query_sequence =     'NPCTRPNNN'
        reference_sequence = '--CTRPNNN'
        expected_inserts = []
        expected_mapping = {2:0, 3:1, 4:2, 5:3, 6:4, 7:5, 8:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(expected_mapping, qindex_to_refcoord)
        self.assertEqual(expected_inserts, inserts)
        
    def testQueryEndsAfterReference(self):
        query_sequence =     'CTRPNNNNP'
        reference_sequence = 'CTRPNNN--'
        expected_inserts = []
        expected_mapping = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(expected_mapping, qindex_to_refcoord)
        self.assertEqual(expected_inserts, inserts)
        
    def testAmbiguous(self):
        query_sequence =     'CT?PNNN'
        reference_sequence = 'CTRPNNN'
        expected_inserts = []
        expected_mapping = {0:0, 1:1, 3:3, 4:4, 5:5, 6:6}
        
        qindex_to_refcoord, inserts = csf2counts.coordinate_map(
            query_sequence,
            reference_sequence)
        
        self.assertEqual(qindex_to_refcoord, expected_mapping)
        self.assertEqual(inserts, expected_inserts)

class IndelWriterTest(unittest.TestCase):
    def setUp(self):
        self.writer = csf2counts.IndelWriter(indelfile=StringIO.StringIO())
        self.writer.start_group(sample_name='E1234_S1', region='R1', qcut=15)
        
    def testNoInserts(self):
        expected_text = """\
sample,region,qcut,left,insert,count
"""
        
        self.writer.add_read(offset_sequence='ACDEF', count=1)
        self.writer.write(inserts=[])
        
        self.assertEqual(expected_text, self.writer.indelfile.getvalue())
        
    def testInsert(self):
        expected_text = """\
sample,region,qcut,left,insert,count
E1234_S1,R1,15,2,D,1
"""
        
        self.writer.add_read(offset_sequence='ACDEF', count=1)
        self.writer.write(inserts=[2])
        
        self.assertMultiLineEqual(expected_text, self.writer.indelfile.getvalue())
        
    def testInsertWithOffset(self):
        expected_text = """\
sample,region,qcut,left,insert,count
E1234_S1,R1,15,2,D,1
"""
        
        self.writer.add_read(offset_sequence='-CDEFG', count=1)
        self.writer.write(inserts=[1], min_offset=1)
        
        self.assertMultiLineEqual(expected_text, self.writer.indelfile.getvalue())
        
    def testTwoInsertsWithOffset(self):
        expected_text = """\
sample,region,qcut,left,insert,count
E1234_S1,R1,15,2,D,1
E1234_S1,R1,15,4,F,1
"""
        
        self.writer.add_read(offset_sequence='-CDEFG', count=1)
        self.writer.write(inserts=[1, 3], min_offset=1)
        
        self.assertMultiLineEqual(expected_text, self.writer.indelfile.getvalue())
