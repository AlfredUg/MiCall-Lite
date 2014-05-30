"""
settings_default.py
To make pipeline portable, allow user to specify
"""

pipeline_version = '6.2'

production = False  # set this to True to push results to NAS
filter_cross_contaminants = False

## Modify this path to your pipeline directory
base_path = '/usr/local/share/miseq/'
base_path += 'production/' if production else 'development/'

# Local path for writing data
home = '/data/miseq/'


## FIFO settings
path_to_fifo_scheduler = '/usr/local/share/fifo_scheduler'
mapping_factory_resources = [("bpsh -1", 6), ("bpsh 0", 6), ("bpsh 1", 8), ("bpsh 2", 8)]

# This factory is allocated with resources with single threaded applications in mind
single_thread_resources = [("bpsh -1", 24), ("bpsh 0", 24), ("bpsh 1", 32), ("bpsh 2", 32)]


## MISEQ_MONITOR settings

rawdata_mount = '/media/RAW_DATA/'  # NAS

delay = 3600  # Delay (seconds) for polling NAS for unprocessed runs

NEEDS_PROCESSING = 'needsprocessing'  # File flags
ERROR_PROCESSING = 'errorprocessing'


## Mapping parameters

# location of .bt2 files
mapping_ref_path = base_path + 'reference_sequences/cfe'

bowtie_threads = 4              # Bowtie performance roughly scales with number of threads
min_mapping_efficiency = 0.95   # Fraction of fastq reads mapped needed
max_remaps = 3                  # Number of remapping attempts if mapping efficiency unsatisfied
consensus_q_cutoff = 20         # Min Q for base to contribute to conseq (pileup2conseq)


## sam2csf parameters
sam2csf_q_cutoffs = [0, 10, 15]  # Q-cutoff for base censoring
max_prop_N = 0.5                 # Drop reads with more censored bases than this proportion
read_mapping_cutoff = 10         # Minimum bowtie read mapping quality

## g2p parameters (Amplicon only)
g2p_alignment_cutoff = 50               # Minimum alignment score during g2p scoring
g2p_fpr_cutoffs = [3.0, 3.5, 4.0, 5.0]  # FPR cutoff to determine R5/X4 tropism
v3_mincounts = [0, 50, 100, 1000]       # Min number of reads to contribute to %X4 calculation

## csf2counts parameters
conseq_mixture_cutoffs = [0.01, 0.02, 0.05, 0.1, 0.2, 0.25]
final_alignment_ref_path = mapping_ref_path.replace('/cfe', '/csf2counts_amino_refseqs.csv')
final_nuc_align_ref_path = mapping_ref_path.replace('/cfe', '/csf_to_fasta_by_nucref.csv')

# Intermediary files to delete when done processing this run (production only)
file_extensions_to_delete = ['bam', 'bt2', 'bt2_metrics', 'pileup', 'sam',
                             'filtering.sam', 'csf.fa']
