import sys
offset =4
with open(sys.argv[1]) as rd :
    for line in rd:
        ff= line.strip().split('\t')
        chr_ = ff[0]
        end1  = int(ff[1])
        end2  =int(ff[2])
        print '\t'.join([chr_  , str(end1 - offset),str(end1)] )
        print '\t'.join([chr_  , str(end2),str(end2 + offset)] )
