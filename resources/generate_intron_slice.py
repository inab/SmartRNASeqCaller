#!/usr/bin/env python

from __future__ import print_function, with_statement

import sys, gzip

offset =4
if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('USAGE:', file=sys.stderr)
    print('This files takes one bed file as argument with intronic regions: one per line', file=sys.stderr)
    print('This will print a new bed file with the 4bp extremities for each intron line', file=sys.stderr)
    print('The resulting BED file should be used with SmartRNASeqCaller as intron bed file', file=sys.stderr)
    print('Exiting', file=sys.stderr)
else:
    infile = sys.argv[1]
    with gzip.open(infile,mode="rt",encoding="latin-1",newline="\n")  if infile.endswith(".gz")  else open(infile,encoding="latin-1")  as rd:
        if len(sys.argv) == 2:
            outfile = None
            outf = sys.stdout
        else:
            outfile = sys.argv[2]
            outf = gzip.open(outfile,mode="wt",encoding="latin-1",newline="\n")  if outfile.endswith(".gz")  else open(outfile,mode="w",encoding="latin-1")
        try:
            for line in rd:
                ff= line.strip().split('\t')
                chr_ = ff[0]
                end1 = int(ff[1])
                end2 = int(ff[2])
                print('\t'.join([chr_  , str(end1 - offset),str(end1)] ), file=outf)
                print('\t'.join([chr_  , str(end2),str(end2 + offset)] ), file=outf)
        finally:
            if outfile is not None:
                outf.close()
