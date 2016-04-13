from cStringIO import StringIO
from struct import pack
from unittest import TestCase
from micall.monitor.phix_parser import read_phix, write_phix_csv


class PhixParserTest(TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(str, self.assertMultiLineEqual)
        self.sample_data = [3,      # file version
                            30,     # record size
                            1,      # lane
                            2,      # tile
                            3,      # cycle
                            0.5,    # error rate
                            4,      # num reads with 0 errors
                            5,      # num reads with 1 error
                            6,      # num reads with 2 errors
                            7,      # num reads with 3 errors
                            8]      # num reads with 4 errors
        format_string = '<bbHHHfLLLLL'
        self.sample_stream = StringIO(pack(format_string, *self.sample_data))

    def test_load(self):
        expected_records = [dict(lane=1,
                                 tile=2,
                                 cycle=3,
                                 error_rate=0.5,
                                 num_0_errors=4,
                                 num_1_error=5,
                                 num_2_errors=6,
                                 num_3_errors=7,
                                 num_4_errors=8)]

        records = list(read_phix(self.sample_stream))

        self.assertEqual(expected_records, records)

    def test_old_version(self):
        self.sample_data[0] = 2
        format_string = '<bbHHHfLLLLL'
        self.sample_stream = StringIO(pack(format_string, *self.sample_data))

        try:
            list(read_phix(self.sample_stream))

            self.fail('Should have thrown.')
        except IOError as ex:
            self.assertEqual('Old phiX error file version: 2', str(ex))

    def test_new_version(self):
        self.sample_data[:2] = [4, 31]
        self.sample_data.append(42)
        self.sample_data.extend(self.sample_data[2:])
        format_string = '<bbHHHfLLLLLbHHHfLLLLLb'
        self.sample_stream = StringIO(pack(format_string, *self.sample_data))
        expected_records = [dict(lane=1,
                                 tile=2,
                                 cycle=3,
                                 error_rate=0.5,
                                 num_0_errors=4,
                                 num_1_error=5,
                                 num_2_errors=6,
                                 num_3_errors=7,
                                 num_4_errors=8)] * 2

        records = list(read_phix(self.sample_stream))

        self.maxDiff = 1000
        self.assertEqual(expected_records, records)

    def test_partial_record(self):
        self.sample_data = self.sample_data[:3]
        format_string = '<bbH'
        self.sample_stream = StringIO(pack(format_string, *self.sample_data))

        try:
            list(read_phix(self.sample_stream))

            self.fail('Should have thrown.')
        except IOError as ex:
            self.assertEqual('Partial record of length 2 found in phiX error file.',
                             str(ex))

    def test_write(self):
        out_file = StringIO()
        records = [dict(tile=2, cycle=1, error_rate=0.1),
                   dict(tile=2, cycle=2, error_rate=0.2)]
        expected_csv = """\
tile,cycle,errorrate
2,1,0.1
2,2,0.2
"""

        write_phix_csv(out_file, records)

        self.assertEqual(expected_csv, out_file.getvalue())

    def test_write_sorted(self):
        out_file = StringIO()
        records = [dict(tile=2, cycle=2, error_rate=0.4),
                   dict(tile=2, cycle=1, error_rate=0.5)]
        expected_csv = """\
tile,cycle,errorrate
2,1,0.5
2,2,0.4
"""

        write_phix_csv(out_file, records)

        self.assertEqual(expected_csv, out_file.getvalue())

    def test_write_reverse(self):
        out_file = StringIO()
        records = [dict(tile=2, cycle=1, error_rate=0.1),
                   dict(tile=2, cycle=2, error_rate=0.2),
                   dict(tile=2, cycle=3, error_rate=0.3),
                   dict(tile=2, cycle=4, error_rate=0.4)]
        read_lengths = [2, 2]
        expected_csv = """\
tile,cycle,errorrate
2,1,0.1
2,2,0.2
2,-1,0.3
2,-2,0.4
"""

        write_phix_csv(out_file, records, read_lengths)

        self.assertEqual(expected_csv, out_file.getvalue())

    def test_write_skip_indexes(self):
        out_file = StringIO()
        records = [dict(tile=2, cycle=1, error_rate=0.1),
                   dict(tile=2, cycle=2, error_rate=0.2),
                   dict(tile=2, cycle=3, error_rate=0.3),
                   dict(tile=2, cycle=4, error_rate=0.4),
                   dict(tile=2, cycle=5, error_rate=0.5),
                   dict(tile=2, cycle=6, error_rate=0.6)]
        read_lengths = [2, 1, 1, 2]
        expected_csv = """\
tile,cycle,errorrate
2,1,0.1
2,2,0.2
2,-1,0.5
2,-2,0.6
"""

        write_phix_csv(out_file, records, read_lengths)

        self.assertEqual(expected_csv, out_file.getvalue())

    def test_write_missing(self):
        out_file = StringIO()
        records = [dict(tile=2, cycle=1, error_rate=0.1),
                   dict(tile=2, cycle=4, error_rate=0.4)]
        expected_csv = """\
tile,cycle,errorrate
2,1,0.1
2,2
2,3
2,4,0.4
"""

        write_phix_csv(out_file, records)

        self.assertEqual(expected_csv, out_file.getvalue())

    def test_write_missing_end(self):
        out_file = StringIO()
        records = [dict(tile=2, cycle=1, error_rate=0.1),
                   dict(tile=2, cycle=2, error_rate=0.2),
                   dict(tile=2, cycle=4, error_rate=0.4),
                   dict(tile=2, cycle=5, error_rate=0.5)]
        read_lengths = [3, 0, 0, 3]
        expected_csv = """\
tile,cycle,errorrate
2,1,0.1
2,2,0.2
2,3
2,-1,0.4
2,-2,0.5
2,-3
"""

        write_phix_csv(out_file, records, read_lengths)

        self.assertEqual(expected_csv, out_file.getvalue())
