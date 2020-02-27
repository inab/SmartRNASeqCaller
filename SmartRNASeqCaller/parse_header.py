# parse vcf hader
import gzip
import sys

outstr=''
ID_header = ['INFO=<ID=DP,','INFO=<ID=ClippingRankSum,','INFO=<ID=LikelihoodRankSum,','INFO=<ID=AC,','INFO=<ID=BaseQRankSum,','INFO=<ID=ReadPosRankSum,']
Annotations= ['Coverage','ClippingRankSumTest','LikelihoodRankSumTest','DepthPerAlleleBySample','BaseQualityRankSumTest','ReadPosRankSumTest']
fields_dict = dict(zip(ID_header,Annotations))

with open(sys.argv[1]) as rd: 
    for line in rd:
        if line.startswith('##'):
            for k,v in fields_dict.items():
                if line.replace('##','').startswith(k):
                    del fields_dict[k]

        elif line.startswith('#'):
            break

#now add only the needed annotations (i.e. those not found in header)
for k,v in fields_dict.items():
    outstr = outstr + ' -A %s'%(v)

sys.stdout.write(outstr)




