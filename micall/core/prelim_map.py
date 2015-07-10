#! /usr/bin/env python

"""
Shipyard-style bowtie2
Run bowtie2 on paired-end FASTQ data sets with user-supplied *.bt2
bowtie2 SAM format output to <stdout> for redirection via subprocess.Popen
Sort outputs by refname.
Convert to CSV format and write to file.

Dependencies: settings.py (derived from settings_default.py)
              *.bt2 files produced by bowtie2-align - pass as metapackage
"""

import argparse
import csv
import logging
import os
import subprocess
import sys

import miseq_logging
import project_config
from micall import settings  # settings.py is a CodeResourceDependency
from micall.utils.externals import Bowtie2, Bowtie2Build

logger = miseq_logging.init_logging_console_only(logging.DEBUG)

def resource_path(target):
    """
    Returns absolute path to target.
    See http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    :param relative:
    :return:
    """
    return os.path.join('' if not hasattr(sys, '_MEIPASS') else sys._MEIPASS, target)



def prelim_map(fastq1,
               fastq2,
               prelim_csv,
               cwd=None,
               nthreads=None,
               callback=None,
               rdgopen=None,
               rfgopen=None):
    if cwd is not None:
        os.chdir(cwd)
    nthreads = nthreads or settings.bowtie_threads

    bowtie2 = Bowtie2(settings.bowtie_version, settings.bowtie_path)
    bowtie2_build = Bowtie2Build(settings.bowtie_version,
                                 settings.bowtie_build_path,
                                 logger)

    # check that the inputs exist
    if not os.path.exists(fastq1):
        logger.error('No FASTQ found at %s', fastq1)
        sys.exit(1)

    if not os.path.exists(fastq2):
        logger.error('No FASTQ found at %s', fastq2)
        sys.exit(1)

    # generate initial reference files
    projects = project_config.ProjectConfig.loadDefault()
    ref_path = 'micall.fasta'
    with open(ref_path, 'w') as ref:
        projects.writeSeedFasta(ref)
    reffile_template = 'reference'
    bowtie2_build.log_call(['--quiet',
                            '-f',
                            ref_path,
                            reffile_template])

    # do preliminary mapping
    output = {}
    read_gap_open_penalty = rdgopen or settings.read_gap_open_prelim
    ref_gap_open_penalty = rfgopen or settings.ref_gap_open_prelim

    # stream output from bowtie2
    bowtie_args = ['--quiet',
                   '-x', reffile_template,
                   '-1', fastq1,
                   '-2', fastq2,
                   '--rdg', "{},{}".format(read_gap_open_penalty,
                                           settings.read_gap_extend_prelim),
                   '--rfg', "{},{}".format(ref_gap_open_penalty,
                                           settings.ref_gap_extend_prelim),
                   '--no-unal', # don't report reads that failed to align
                   '--no-hd', # no header lines (start with @)
                   '--local',
                   '-p', str(nthreads)]
    p = bowtie2.create_process(bowtie_args, stdout=subprocess.PIPE)
    with p.stdout:
        for i, line in enumerate(p.stdout):
            if callback and i%1000 == 0:
                callback(i)
            refname = line.split('\t')[2]  # read was mapped to this reference
            if not refname in output:
                output.update({refname: []})
            output[refname].append(line.split('\t')[:11])  # discard optional items

    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, bowtie_args)

    fieldnames = ['qname',
                  'flag',
                  'rname',
                  'pos',
                  'mapq',
                  'cigar',
                  'rnext',
                  'pnext',
                  'tlen',
                  'seq',
                  'qual']
    writer = csv.DictWriter(prelim_csv, fieldnames)
    writer.writeheader()
    
    # lines grouped by refname
    for refname, lines in output.iteritems():
        for line in lines:
            writer.writerow(dict(zip(fieldnames, line)))


def main():
    parser = argparse.ArgumentParser(
        description='Map contents of FASTQ R1 and R2 data sets to references using bowtie2.')
    
    parser.add_argument('fastq1', help='<input> FASTQ containing forward reads')
    parser.add_argument('fastq2', help='<input> FASTQ containing reverse reads')
    parser.add_argument('prelim_csv',
                        type=argparse.FileType('w'),
                        help='<output> CSV containing preliminary mapping from bowtie2 (modified SAM)')
    parser.add_argument("--rdgopen", default=None, help="<optional> read gap open penalty")
    parser.add_argument("--rfgopen", default=None, help="<optional> reference gap open penalty")
    
    args = parser.parse_args()
    prelim_map(args.fastq1, args.fastq2, args.prelim_csv, args.rdgopen, args.rfgopen)


    
if __name__ == '__main__':
    main()
