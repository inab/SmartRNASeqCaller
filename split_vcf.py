#split files

import sys
import argparse
import gzip

parser = argparse.ArgumentParser()
parser.add_argument("--vcf_in",'-v', dest='v',type=str,help="VCF file to split")
parser.add_argument("--csv_classified",'-c', dest='c',type=str,help="CSV file with classification")
parser.add_argument("--outprefix",'-o', dest='o',type=str, help="Output prefix for ok and ko files")
parser.add_argument("--GTdict",'-g', dest='g',type=str, default = 'None', help="Dictionary with phased GT information")

args = parser.parse_args()


var_dict = dict()
#read the variant classification and store it in a dictionary
with open(args.c) as rd:
    for line in rd:
        ff= line.strip().split(',')
        var_dict[ff[0]] = ff[1]
        

#load the pickle dict of phased GT to convert them back
if(args.g != 'None'):
    import pickle
    GT_original = pickle.load(open(args.g,'rb'))
else:
    GT_original = dict()
    
#function to parse the genotype
def parse_genotype(line,ID,GT_dict):
    if ID in GT_dict.keys():
        ff = line.strip().split('\t')
        ff[9]  = GT_dict[ID]
        line = '\t'.join(ff) + '\n'
        

    return(line)
    

infile = args.v        
with  open(infile) if infile.endswith('vcf') else gzip.open(infile)  as rd, open(args.o + '_ok.vcf', 'w') as ok_file, open(args.o + '_ko.vcf','w') as ko_file:
    for line in rd:
        ff = line.strip().split('\t')
        if line.startswith('#'):
            ok_file.write(line)
            ko_file.write(line)
        else:
            ID=':'.join([ff[0],ff[1],ff[3],ff[4]])
            line =  parse_genotype(line,ID,GT_original)
            verdict= var_dict.get(ID,'NA') 
            if verdict =='1':
                ok_file.write(line)
            elif verdict =='0':
                ko_file.write(line)
            else:
                print 'this %s variant has no classification'%ID
                ko_file.write(line)

                
        
