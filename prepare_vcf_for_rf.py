 ## 
import pysam
import argparse
import gzip
import sys
import os
import subprocess
import pandas as pd

parser = argparse.ArgumentParser(description = 'Parses RNA for RF later')
parser.add_argument('--dna', type=str, dest='dna', required=False,default = 'None', help='DNA file with ground truth variants to compare against [optional]')
parser.add_argument('--vcf', type=str, dest='vcf', required=True, help='Input vcf file [required] Needs tobe bgzip and tabix if --dna argument is used')
parser.add_argument('--outfile', type=str, dest='outfile', required=True, help='Output file with all variants in csv format. [required]')
args = parser.parse_args()

# steps arr 

def parse_info_field(info_field, columns):
    out_dict = {k : 'NA' for k in columns}
    tmp_dict = { (x.split('=')[0] if len(x.split('='))>1 else x.split('=')[0]) : (x.split('=')[1] if len(x.split('='))>1 else 'NA'        )for x in info_field.split(';')}
    for k,v in tmp_dict.items():
        out_dict[k] =v
    
    out_list = [out_dict[k] for k in columns]
    return out_list

def parse_gt_field(gt_field,format_field):
    out_list =[]
    
    if gt_field.startswith('0/0') or gt_field.startswith('./.') or gt_field.startswith('0|0') or gt_field.startswith('.|.'):
        #it's not a variant!
        return 'skip'
    else:
        ff = gt_field.split(':')
        #print format_field
        try:
          AD_idx = format_field.split(':').index('AD')
          AD= [float(x) for x in ff[AD_idx].split(',')]
        except:
            try:
            #case of platypus NR:NV 
            #ratio is NV/NR
              NV   =(ff[format_field.split(':').index('NV')])
              NR   =(ff[format_field.split(':').index('NR')])
              NV = float(NV.split(',')[0])
              NR = float(NR.split(',')[0])
              AD = [NR-NV,NV]
            except : 
              AD=[0,0]
#              print NV
#              print NR
#              print format_field
#              print gt_field

              #raise

        out_list.append(ff[0])
       
        if sum(AD) <= 0 : return 'skip' #no coverage at all
        try :
            ratio = str(AD[1] / (AD[1] + AD[0]))
        except:
            print AD
            print gt_field
            raise
            ratio = '0.0'
        out_list.append(ratio)
    return out_list


def parse_filter_field(field,names):
    out_list = ['1'  if x in field.split(';')  else '0' for x in names]
    return out_list

def add_extra_fields(ID_):
    chr_,pos,ref,alt=ID_.split(':')
    #out = type, len(ref), len(alt), len(alt-len(re))
    if len(ref)+len(alt) ==2 :
        type_ = 'snp'
    else : type_ = 'indel'
    
    out_list = [type_,str(len(ref)), str(len(alt)), str(len(alt) - len(ref))]
    return out_list

def in_dna(line):
    return out_list

def main(args):
    # steps are line by line in args.vcf
    # extract ID as chr:pos:ref:alt
    # Parse info field in a way that all needed columns are represented
    #   done by parsing ##INFO fields in the header
    
    output_dictionary  = dict()
    print '###############################################################'
    print ' Generating annotation '
    print '###############################################################'
    
    info_colnames = list()
    #add a list with skipped variants
    skipped_list = list()
    #add a dictionary with  the original GT for phased variants
    # this dictionary should be saved and removed at the end
    var_GT_phased_dict = dict()
    
    with  open(args.vcf) if args.vcf.endswith('vcf') else gzip.open(args.vcf) as rd,open(args.outfile,'w') as wr:
        if args.vcf.endswith('vcf') and args.dna !='None':
            print 'Please bgzip and tabix your RNA variant file if you want to compare with a DNA ground truth. Exiting'
            raise
        for line in rd:
            if line.startswith('##'):
                if line.startswith('##INFO'):
                    info_colnames.append(line.split('##INFO=<ID=')[1].split(',')[0])
             
            elif line.startswith('#'):
                #check individual sample
                ff= line.strip().split('\t')
                if len(ff) != 10:
                    print ff
                    print 'Error, this tool only works with single sample VCF'
                    raise
                # generate header
                features_rna = ['First_bases','Splice','RNAEdit','RepMask','Homopolymer']
                header = ['ID']
                header.extend(info_colnames)
                header.extend(['Genotype','Allele_ratio'])
                header.extend(features_rna)
                header.extend(['Type', 'RefLen','AltLen','Alt_ref_length_diff'])
                
                if args.dna != 'None':
                    header.append('inDNA')
                wr.write('\t'.join(header) + '\n')
            else:
                ff= line.strip().split('\t')
                ID_ = ':'.join([ff[0],ff[1],ff[3],ff[4]])
                
                if len(ff[3].split(','))>1:
                    print 'Skipping %s because it is multiallelic.'%(ID_)
                    skipped_list.append(line)
                    continue
                ######################################################3
                #info field parsing
                ######################################################3
                
                field_output = parse_info_field(ff[7],info_colnames)
                
                ######################################################3
                # GT parsing:
                ######################################################3
                
                #pre_check to convert phased genotypes:
                # phasing only for 0|1 1|0 0|0 or 1|1
                # Other more complex genotypes are not processed by this version of the tool
                gt = ff[9].split(':')
                if gt[0] in  ['1|0','0|1','1|1']:
                    var_GT_phased_dict[ID_] = ff[9]
                    if gt[0] == '1|1' :
                        gt[0] = '1/1'
                    else:
                        gt[0] = '0/1'
                    ff[9] = ':'.join(gt)
                        
                
                #now that we have changed GT from phased to unphased and stored
                #in the dict, skip all those not matchnig
                if gt[0] not in ['0/1','1/1']:
                    print 'Skipping %s because of genotype parsing problems ; Not a variant or not a biallelic genotype'%(ID_)
                    print ff[9]
                    skipped_list.append(line)
                    continue
                
                out_list = parse_gt_field(ff[9],ff[8])
                if out_list =='skip':
                    print 'Skipping %s because of genotype parsing problems.'%(ID_)
                    print ff[9]
                    skipped_list.append(line)
                    continue
                else :
                    field_output.extend(out_list)
                    
                ######################################################
                ##    Filter field parsing
                ######################################################
                out_list = parse_filter_field(ff[6],features_rna) 
                field_output.extend(out_list)
                
                
                ######################################################3
                # Extra fields:
                ######################################################3
                out_list = add_extra_fields(ID_)
                
                field_output.extend(out_list)
                
                # If --dna: add a column 
                if args.dna  != 'None':
                    field_output.append('0')
                    output_dictionary[ID_] = field_output
                else:
                    wr.write(ID_+'\t'+ '\t'.join(field_output)+ '\n')
                
        ###
        # Step in which we store the skipped lines and the dictionary of 
        ###
        with open(args.outfile + '.skipped.vcf','w') as wr:
            for line in skipped_list:
                wr.write(line.strip())
        import pickle
        out_s = open(args.outfile + 'GT_dict.pk', 'wb')
        pickle.dump(var_GT_phased_dict, out_s)   
        
        # now open the dna file and one by one try to find them
        if args.dna  != 'None':
            print '###############################################################'
            print ' Looking for DNA match'
            print '###############################################################'
            
            #faster way: intersect 2 vcfs
            syscall = '''bcftools isec -n=2 %s %s | awk -F'\t' '{print $1 ":" $2 ":" $3 ":" $4}'  > %s  '''%(args.vcf,args.dna,args.outfile+'.tmp')
            return_code = subprocess.call(syscall,shell =True)
            print syscall
            
            with  open(args.outfile+'.tmp') as  dna:
                refvals =output_dictionary.keys()
                for line in dna:
                    if line.startswith('#') : continue
                    else:
                        # ff= line.strip().split('\t')
                        # if ff[4]=='<NON_REF>' : continue
                        #ID_ = ':'.join([ff[0],ff[1],ff[3],ff[4]])
                        ID_ = line.strip()
                        if ID_ in refvals:
                            tmp = output_dictionary[ID_]
                            tmp[-1] = '1'
                            output_dictionary[ID_] = tmp
                            #refvals.remove(ID_)
                            #del output_dictionary[ID_]
            print '###############################################################'
            print ' Writing now to output file w/ DNA information'
            print '###############################################################'
            for key,field_output in output_dictionary.items():
                wr.write(key +'\t'+ '\t'.join(field_output)+ '\n')
            os.unlink(args.outfile+'.tmp')

    return None


main(args)
