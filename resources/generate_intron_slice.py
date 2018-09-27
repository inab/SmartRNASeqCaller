import sys
offset =4
if len(sys.argv) !=2 :
    print 'USAGE:'
    print 'This files takes one bed file as argument with intronic regions: one per line'
    print 'This will print a new bed file with the 4bp extremities for each intron line'
    print 'The resulting BED file should be used with SmartRNASeqCaller as intron bed file'
    print 'Exiting'
else:
  with open(sys.argv[1]) as rd :
    for line in rd:
        ff= line.strip().split('\t')
        chr_ = ff[0]
        end1  = int(ff[1])
        end2  =int(ff[2])
        print '\t'.join([chr_  , str(end1 - offset),str(end1)] )
        print '\t'.join([chr_  , str(end2),str(end2 + offset)] )
