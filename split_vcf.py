#split files

import sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--vcf_in",'-v', dest='v',type=str,help="VCF file to split")
parser.add_argument("--csv_classified",'-c', dest='c',type=str,help="CSV file with classification")
parser.add_argument("--outprefix",'-o', dest='o',type=str, help="Output prefix for ok and ko files")

args = parser.parse_args()


var_dict = dict()
with open(args.c) as rd:
    for line in rd:
        ff= line.strip().split(',')
        var_dict[ff[0]] = ff[1]
        
        
with open(args.v ,'r') as rd, open(args.o + '_ok.vcf', 'w') as ok_file, open(args.o + '_ko.vcf','w') as ko_file:
    for line in rd:
        ff = line.strip().split('\t')
        if line.startswith('#'):
            ok_file.write(line)
            ko_file.write(line)
        else:
            ID=':'.join([ff[0],ff[1],ff[3],ff[4]])
            verdict= var_dict.get(ID,'NA') 
            if verdict =='yes':
                ok_file.write(line)
            elif verdict =='no':
                ko_file.write(line)
            else:
                print 'this %s variant has no classification'%ID
                ko_file.write(line)

                
        