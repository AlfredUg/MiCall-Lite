"""
Slice 4_csf2counts.py output (Count CSVs + conseq files) into sub-regions.
"""

import os, sys,time
from glob import glob

# Define slices with (Label, region to slice, start, end)
# Coordinates are in nucleotide space: start/end are inclusive (Relative to HXB2 aligned sequences)
region_slices = [	("PROTEASE", "HIV1B-pol", 1, 297),
			("PRRT", "HIV1B-pol", 1, 1617),
			("INTEGRASE", "HIV1B-pol", 1978, 2844),
			("P17", "HIV1B-gag", 1, 396),
			("P24", "HIV1B-gag", 397, 1089),
			("P2P7P1P6","HIV1B-gag", 1090, 1502),
			("GP120","HIV1B-env", 1, 1533),
			("GP41", "HIV1B-env", 1534, 2570),
			("V3", "HIV1B-env", 887, 993)]

if len(sys.argv) != 2:
	print 'Usage: python {} /path/to/outputs'.format(sys.argv[0])
	sys.exit()

root = sys.argv[1]

for rule in region_slices:
	slice, region, start, end = rule
	files = glob(root + '/*.{}.*nuc.csv'.format(region))
	files += glob(root + '/*.{}.*amino.csv'.format(region))

	for path in files:
		fileName = os.path.basename(path)
		sample,old_region = fileName.split(".")[:2]

		with open(path, 'rU') as f:
			lines = f.readlines()

		newFileName = fileName.replace(region,slice)
		dirName = os.path.dirname(path)

		f = open("{}/{}".format(dirName, newFileName), 'w')
		f_conseq = open("{}/{}".format(dirName, newFileName.replace(".csv",".conseq")), 'w')
		conseq = ""

		for i,line in enumerate(lines):
			line = line.rstrip("\n")

			# Determine dictionary from header
			if (i == 0):
				f.write("{}\n".format(line))
				dictionary = line.split(",")[2:]
				continue

			# For nuc.csv, hxb2_pos is in nucleotide space
			query_pos, hxb2_pos = map(int, line.split(",")[:2])
			if "nuc.csv" in path:
				if hxb2_pos < start or hxb2_pos > end+1: continue
				region_pos = hxb2_pos - start + 1

			# For amino.csv, hxb2_pos is in amino space
			elif "amino.csv" in path:
				if hxb2_pos < (start+2)/3 or hxb2_pos > end/3: continue
				region_pos = hxb2_pos - (start+2)/3 + 1

			# Generate consensus sequence
			counts = line.split(",")[2:]
			max_count = max(map(int,counts))
			max_char = filter(lambda x: int(x) == max_count, counts)
			index = counts.index(max_char[0])
			majority_char = dictionary[index]
			conseq += majority_char
			f.write("{},{},{}\n".format(query_pos,region_pos,",".join(counts)))

		f.close()
		f_conseq.write(">{}_{}\n{}".format(sample, slice, conseq))
		f_conseq.close()
