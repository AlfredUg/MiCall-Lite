import sys

import argparse
from csv import DictWriter

from struct import unpack
import csv
import os
from operator import itemgetter
import math
from itertools import groupby


def read_records(data_file, min_version):
    """ Read records from an Illumina Interop file.
    :param file data_file: an open file-like object. Needs to have a two-byte
    header with the file version and the length of each record, followed by the
    records.
    :param int min_version: the minimum accepted file version.
    :return: an iterator over the records in the file. Each record will be a raw
    byte string of the length from the header.
    """
    header = data_file.read(2)
    version, record_length = unpack('!BB', header)
    if version < min_version:
        raise IOError(
            'File version {} is less than minimum version {} in {}.'.format(
                version,
                min_version,
                data_file.name))
    while True:
        data = data_file.read(record_length)
        read_length = len(data)
        if read_length == 0:
            break
        if read_length < record_length:
            raise IOError('Partial record of length {} found in {}.'.format(
                read_length,
                data_file.name))
        yield data


def read_errors(data_file):
    """ Read error rate data from a phiX data file.

    :param file data_file: an open file-like object. Needs to have a two-byte
    header with the file version and the length of each record, followed by the
    records.
    :return: an iterator over the records of data in the file. Each record is a
    dictionary with the following keys:
    - lane [uint16]
    - tile [uint16]
    - cycle [uint16]
    - error_rate [float]
    - num_0_errors [uint32]
    - num_1_error [uint32]
    - num_2_errors [uint32]
    - num_3_errors [uint32]
    - num_4_errors [uint32]
    """
    PARSED_LENGTH = 30
    for data in read_records(data_file, min_version=3):
        fields = unpack('<HHHfLLLLL', data[:PARSED_LENGTH])
        yield dict(lane=fields[0],
                   tile=fields[1],
                   cycle=fields[2],
                   error_rate=fields[3],
                   num_0_errors=fields[4],
                   num_1_error=fields[5],
                   num_2_errors=fields[6],
                   num_3_errors=fields[7],
                   num_4_errors=fields[8])


def _yield_cycles(records, read_lengths):
    sorted_records = list(map(itemgetter('tile', 'cycle', 'error_rate'), records))
    try:
        sorted_records.sort()
    except:
        print (sorted_records)
        raise
    max_forward_cycle = read_lengths and read_lengths[0] or sys.maxint
    min_reverse_cycle = read_lengths and sum(read_lengths[:-1])+1 or sys.maxint
    for record in sorted_records:
        cycle = record[1]
        if cycle >= min_reverse_cycle:
            cycle = min_reverse_cycle - cycle - 1
            yield record[0], cycle, record[2]
        elif cycle <= max_forward_cycle:
            yield record


def _record_grouper(record):
    # Group by tile and sign of cycle (forward or reverse).
    return (record[0], int(math.copysign(1, record[1])))


def write_phix_csv(out_file, records, read_lengths=None, summary=None):
    """ Write phiX error rate data to a comma-separated-values file.

    Missing cycles are written with blank error rates, index reads are not
    written, and reverse reads are written with negative cycles.

    :param out_file: an open file to write to
    :param records: a sequence of dictionaries like those yielded from
    read_phix().
    :param read_lengths: a list of lengths for each type of read: forward,
    indexes, and reverse
    :param dict summary: a dictionary to hold the summary values:
    error_rate_fwd and error_rate_rev.
    """
    writer = csv.writer(out_file, lineterminator=os.linesep)
    writer.writerow(['tile', 'cycle', 'errorrate'])

    error_sums = [0.0, 0.0]
    error_counts = [0, 0]
    #TODO: determine read_lengths from file
    for (_tile, sign), group in groupby(_yield_cycles(records, read_lengths),
                                        _record_grouper):
        previous_cycle = 0
        for record in group:
            cycle = record[1]
            previous_cycle += sign
            while previous_cycle*sign < cycle*sign:
                writer.writerow((record[0], previous_cycle))
                previous_cycle += sign
            writer.writerow(record)
            summary_index = (sign+1)//2
            error_sums[summary_index] += record[2]
            error_counts[summary_index] += 1
        if read_lengths:
            read_length = read_lengths[0] if sign == 1 else -read_lengths[-1]
            while previous_cycle*sign < read_length*sign:
                previous_cycle += sign
                writer.writerow((record[0], previous_cycle))
    if error_counts[1] > 0 and summary is not None:
        summary['error_rate_fwd'] = error_sums[1]/error_counts[1]
    if error_counts[0] > 0 and summary is not None:
        summary['error_rate_rev'] = error_sums[0]/error_counts[0]


def parse_interop(handle, outfile):
    writer = DictWriter(outfile, fieldnames=['num_3_errors', 'error_rate', 'lane', 'num_4_errors', 'num_0_errors',
                                             'tile', 'num_2_errors', 'num_1_error', 'cycle'])
    writer.writeheader()
    for record in read_errors(handle):
        writer.writerow(record)

def read_tiles(handle):
    PARSED_LENGTH = 10
    for data in read_records(handle, min_version=2):
        fields = unpack('<HHHf', data[:PARSED_LENGTH])
        yield dict(
            lane=fields[0],
            tile=fields[1],
            metric_code=fields[2],
            metric_value=fields[3]
        )

def main():
    aparser = argparse.ArgumentParser(description='Extract phiX174 error rates from InterOp file')
    aparser.add_argument('bin', type=argparse.FileType('rb'), help='ErrorMetricsOut.bin file from run')
    aparser.add_argument('output', type=argparse.FileType('w'), help='File to write CSV output')
    args = aparser.parse_args()

    #parse_interop(args.bin, args.output)
    records = read_errors(args.bin)
    write_phix_csv(args.output, records, [300, 8, 8, 300], {})

if __name__ == '__main__':
    main()

