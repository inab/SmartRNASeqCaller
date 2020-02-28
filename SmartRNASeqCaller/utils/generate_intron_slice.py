#!/usr/bin/env python

from __future__ import print_function, with_statement

import sys, gzip

if sys.version_info[0] == 2:
    # py2
    import codecs
    import warnings
    
    def open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        if newline is not None:
            warnings.warn('newline is not supported in py2')
        if not closefd:
            warnings.warn('closefd is not supported in py2')
        if opener is not None:
            warnings.warn('opener is not supported in py2')
        return codecs.open(filename=file, mode=mode, encoding=encoding, errors=errors, buffering=buffering)
    
    def gzip_open(file, mode='rb', encoding=None, newline=None):
        if newline is not None:
            warnings.warn('newline is not supported in py2')
        func = None
        if encoding is not None:
            if mode == 'rt':
                mode = 'rb'
                func = codecs.getreader
            elif mode == 'wt':
                mode = 'wb'
                func = codecs.getwriter
        
        fd0 = gzip.open(file,mode=mode)
        
        if func is not None:
            retval = func(encoding)(fd0)
        else:
            retval = fd0
        
        return retval
else:
    gzip_open = gzip.open


offset=4



if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('USAGE:', file=sys.stderr)
    print('This files takes one bed file as argument with intronic regions: one per line', file=sys.stderr)
    print('This will print a new bed file with the 4bp extremities for each intron line', file=sys.stderr)
    print('The resulting BED file should be used with SmartRNASeqCaller as intron bed file', file=sys.stderr)
    print('Exiting', file=sys.stderr)
else:
    infile = sys.argv[1]
    with gzip_open(infile,mode="rt",encoding="latin-1",newline="\n")  if infile.endswith(".gz")  else open(infile,encoding="latin-1")  as rd:
        if len(sys.argv) == 2:
            outfile = None
            outf = sys.stdout
        else:
            outfile = sys.argv[2]
            outf = gzip_open(outfile,mode="wt",encoding="latin-1",newline="\n")  if outfile.endswith(".gz")  else open(outfile,mode="w",encoding="latin-1")
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
