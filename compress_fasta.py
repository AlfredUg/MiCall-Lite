"""
Collapse identical reads and track of read count.

Fasta headers are renamed to only reference the
sample, as determined by the prefix in the filename
of the fasta file itself (As opposed to the header)

Input: remap.sam.<qScore>.fasta
Output: remap.sam.<qScore>.fasta.<minCount>.seq
"""

import sys
from seqUtils import convert_fasta

helpOutput = """
Usage: python compress_fasta.py <minCount> <fasta_files_to_collapse>
Example (min count 3): python compress_fasta.py 3 ../path/to/files/*.fasta.5
Example (no min count): python compress_fasta.py 0 ../path/to/files/*.fasta.5
you can use $(ls PATH)
"""

if len(sys.argv) <= 2:
	print helpOutput
	sys.exit()

minCount = int(sys.argv[1])
files = sys.argv[2:]

if len(files) == 0:
	print helpOutput
	sys.exit()

for f in files:
	filename = f.split('/')[-1]
	prefix = filename.split('.')[0]
	
	infile = open(f, 'rU')
	try:
		print "convert_fasta({})".format(filename)
		fasta = convert_fasta(infile.readlines())
	except:
		print 'failed to convert', f
		continue
	
	infile.close()
	
	# Collect identical sequences
	d = {}
	for h, s in fasta:
		if d.has_key(s):
			d[s] += 1
		else:
			d.update({s: 1})
	
	intermed = [(count, s) for s, count in d.iteritems()]
	intermed.sort(reverse=True)

	outfilename = "{}.{}.seq".format(f,minCount)
	#outfile = open(f+'.seq', 'w')
	outfile = open(outfilename, 'w')

	for i, (count, seq) in enumerate(intermed):
		if count >= minCount:
			outfile.write('>%s_variant_%d_count_%d\n%s\n' % (prefix, i, count, seq))
	
	outfile.close()
