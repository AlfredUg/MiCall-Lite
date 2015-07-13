#! /usr/bin/env python

import sys
import re
import argparse
from csv import DictReader
from micall.core.sam2aln import merge_pairs, cigar_re
from micall.utils.translation import translate

# screen for in-frame deletions
pat = re.compile('([A-Z])(---)+([A-Z])')

QMIN = 20   # minimum base quality within insertions
QCUT = 10   # minimum base quality to not be censored
QDELTA = 5

def parse_args():
    parser = argparse.ArgumentParser(description='Calculate g2p scores from amino acid sequences.')

    parser.add_argument('remap_csv', type=argparse.FileType('rU'),
                        help='<input> CSV containing remap output (modified SAM)')
    parser.add_argument('nuc_csv', type=argparse.FileType('rU'),
                        help='<input> CSV containing nucleotide frequency output from aln2counts.py')
    parser.add_argument('g2p_csv', type=argparse.FileType('w'),
                        help='<output> CSV containing g2p predictions.')
    return parser.parse_args()


class RegionTracker:
    def __init__(self, tracked_region):
        self.tracked_region = tracked_region
        self.ranges = {}

    def add_nuc(self, seed, region, query_pos):
        """
         # Add a nucleotide position to the tracker.
        :param seed: name of the seed region
        :param region: name of the coordinate region
        :param query_pos: query position in the consensus coordinates
        :return: unused
        """
        if region != self.tracked_region:
            return

        if seed in self.ranges:
            range = self.ranges[seed]
            if range[1] < query_pos:
                range[1] = query_pos
            elif query_pos < range[0]:
                range[0] = query_pos
        else:
            self.ranges.update({seed: [query_pos, query_pos]})

    def get_range(self, seed):
        """
        Get the minimum and maximum query positions that were seen for a seed.
        :param seed: name of the seed region
        :return: array of two integers
        """
        return self.ranges.get(seed, [None, None])


def apply_cigar_and_clip (cigar, seq, qual, pos=0, clip_from=0, clip_to=None):
    """
    Use CIGAR string (Compact Idiosyncratic Gapped Alignment Report) in SAM data
    to apply soft clips, insertions, and deletions to the read sequence.
    Any insertions relative to the sample consensus sequence are discarded to
    enforce a strict pairwise alignment, and returned separately in a
    dict object.
    """
    newseq = '-' * int(pos)  # pad on left
    newqual = '!' * int(pos)
    tokens = cigar_re.findall(cigar)
    if len(tokens) == 0:
        return None, None, None
    left = 0
    for token in tokens:
        length = int(token[:-1])
        # Matching sequence: carry it over
        if token[-1] == 'M':
            newseq += seq[left:(left+length)]
            newqual += qual[left:(left+length)]
            left += length
        # Deletion relative to reference: pad with gaps
        elif token[-1] == 'D':
            newseq += '-'*length
            newqual += ' '*length  # Assign fake placeholder score (Q=-1)
        # Insertion relative to reference
        elif token[-1] == 'I':
            its_quals = qual[left:(left+length)]
            if all([(ord(q)-33) >= QMIN for q in its_quals]):
                # accept only high quality insertions relative to sample consensus
                newseq += seq[left:(left+length)]
                newqual += its_quals
                if clip_to:
                    clip_to += length  # accommodate insertion
            left += length
        # Soft clipping leaves the sequence in the SAM - so we should skip it
        elif token[-1] == 'S':
            left += length
        else:
            print "Unable to handle CIGAR token: {} - quitting".format(token)
            sys.exit()

    return newseq[clip_from:clip_to], newqual[clip_from:clip_to]


def sam_g2p(pssm, remap_csv, nuc_csv, g2p_csv):
    pairs = {}  # cache read for pairing
    merged = {}  # tabular merged sequence variants
    tracker = RegionTracker('V3LOOP')

    # look up clipping region for each read
    reader = DictReader(nuc_csv)
    for row in reader:
        if row['query.nuc.pos'] == '':
            # skip deletions in query relative to reference
            continue
        tracker.add_nuc(row['seed'], row['region'], int(row['query.nuc.pos'])-1)

    # parse contents of remap CSV output
    reader = DictReader(remap_csv)
    for row in reader:
        clip_from, clip_to = tracker.get_range(row['rname'])
        if clip_from is None:
            # uninteresting region
            continue

        seq2, qual2 = apply_cigar_and_clip(row['cigar'], row['seq'], row['qual'], int(row['pos'])-1, clip_from, clip_to+1)

        mate = pairs.get(row['qname'], None)
        if mate:
            seq1 = mate['seq']
            qual1 = mate['qual']

            # merge pairs only if they are the same length
            if len(seq1) == len(seq2):
                mseq = merge_pairs(seq1, seq2, qual1, qual2)
            else:
                # implies an insertion not covered in one read mate
                mseq = seq1 if len(seq1) > len(seq2) else seq2

            if mseq not in merged:
                merged.update({mseq: 0})
            merged[mseq] += 1

        else:
            pairs.update({row['qname']: {'seq': seq2, 'qual': qual2}})


    sorted = [(v,k) for k, v in merged.iteritems()]
    sorted.sort(reverse=True)

    # apply g2p algorithm to merged reads
    with g2p_csv as f:
        f.write('rank,count,g2p,fpr,aligned,error\n')  # CSV header
        rank = 0
        for count, s in sorted:
            # remove in-frame deletions
            seq = re.sub(pat, r'\g<1>\g<3>', s)

            rank += 1
            prefix = '%d,%d' % (rank, count)
            seqlen = len(seq)
            if seq.upper().count('N') > (0.5*seqlen):
                # if more than 50% of the sequence is garbage
                f.write('%s,,,,low quality\n' % prefix)
                continue

            if seqlen == 0:
                f.write('%s,,,,zerolength\n' % prefix)
                continue

            prot = translate(seq, 0, ambig_char='X')

            # sanity check 1 - bounded by cysteines
            if not prot.startswith('C') or not prot.endswith('C'):
                f.write('%s,,,%s,cysteines\n' % (prefix, prot))
                continue

            # sanity check 2 - too many ambiguous codons
            if prot.count('X') > 2:
                f.write('%s,,,%s,>2ambiguous\n' % (prefix, prot))
                continue

            # sanity check 3 - no stop codons
            if prot.count('*') > 0:
                f.write('%s,,,%s,stop codons\n' % (prefix, prot))
                continue

            # sanity check 4 - V3 length in range 32-40 inclusive
            if len(prot) < 32 or len(prot) > 40:
                f.write('%s,,,%s,length\n' % (prefix, prot))
                continue

            score, aligned = pssm.run_g2p(seq)

            try:
                aligned2 = ''.join([aa_list[0] if len(aa_list) == 1 else '[%s]'%''.join(aa_list)
                                    for aa_list in aligned])
            except:
                # sequence failed to align
                f.write('%s,%s,,,failed to align\n' % (prefix, score))
                continue

            fpr = pssm.g2p_to_fpr(score)
            f.write(','.join(map(str, [prefix, score, fpr, aligned2, 'ambiguous' if '[' in aligned2 else '']))+'\n')

        f.close()


def main():
    args = parse_args()
    from micall.g2p.pssm_lib import Pssm
    pssm = Pssm()
    sam_g2p(pssm=pssm, remap_csv=args.remap_csv, nuc_csv=args.nuc_csv, g2p_csv=args.g2p_csv)

if __name__ == '__main__':
    # note, must be called from project root if executing directly
    # i.e., python micall/g2p/sam_g2p.py -h
    main()
