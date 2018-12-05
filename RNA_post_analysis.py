# Filtering steps
import pysam
import argparse
import gzip
import sys
import os
import subprocess
import pandas as pd


parser = argparse.ArgumentParser(description = 'filter SNPs according to their family distribution')
parser.add_argument('--bam', type=str, dest='bam', required=True, help='Input bam file [required]')
parser.add_argument('--vcf', type=str, dest='vcf', required=True, help='Input vcf file [required]')
parser.add_argument('--outfile', type=str, dest='outfile', required=True, help='Output file wit all variants. [required]')
parser.add_argument('--ref', type=str, dest='ref', required=True, help='Input ref fasta file')

parser.add_argument('--repmask', type=str, dest='repmask', required=True, help='Input rep masker bed file')
parser.add_argument('--intron', type=str, dest='intron', required=True, help='Input 4bp intronic region bed file')
parser.add_argument('--rnaedit', type=str, dest='rnaedit', required=True, help='Input  common RNA edit bed file')


args = parser.parse_args()

def process_align(pileupread,ref,delta):
    a_read=pileupread.alignment
    base_at_pos = a_read.query_sequence[pileupread.query_position]
    if not(base_at_pos == ref):
        #if pileupread.alignment.is_reverse: #negative
        if a_read.query_length - pileupread.query_position <= delta: return 1
        #else:
        if pileupread.query_position <= delta  : return 1
        return 0
    else: return -1
    return -1


def process_pcol(pileupcolumn,delta,ref):
    alt_support = [ process_align(x,ref,delta) for x in pileupcolumn.pileups if not x.is_del and not x.is_refskip   ]
    alt_support = filter(lambda a: a != -1, alt_support)
    ret_val = float(len(alt_support))
    if ret_val > 0:
        ret_val = alt_support.count(1) / ret_val
    return ret_val

def step1_start_end_read(samfile,sites,outf):
    delta = 6 ## first 6bp
    with open(outf,'w') as wr:
        wr.write('\t'.join(['Chr','Pos','Ref','Alt','First_bases_percent_support']) + '\n')
        for chr_,pos,ref,alt in sites:
            
            if alt=='<NON_REF>' : continue
            #print "%s,%s,%s,%s"%(chr_,pos,ref,alt )
            alt_support = 0
            alt_in_ends = 0
            for pileupcolumn in samfile.pileup( chr_, int(pos)-1 , int(pos)):
                if pileupcolumn.pos == int(pos) -1  :
                    bad_pct  = process_pcol(pileupcolumn,delta,ref)
                    # print bad_pct
            wr.write('\t'.join([chr_,pos,ref,alt,str(bad_pct)]) + '\n')
    return None

def overlap_vcf_with_bed(vcf,bed,outfile):
    syscall= "bedtools intersect  -a %s -b %s -wa 2>/dev/null |grep -v '0/0' | awk -F '\\t' '{print $1,$2,$4,$5}'|sed -e 's/ /\\t/g' - > %s "%(vcf,bed,outfile)
    
    print syscall
    return_code = subprocess.call(syscall,shell =True)
    if return_code != 0:
        raise
    return None

def  step4_homopolymer(fasta,sites,outf,outf_context):
    offset = 4
    site_dict = dict()
    #step 1 generate bed file with
    print 'generate dictionary of sites and bed file'
    with open(outf+'tmp.bed','w')  as wr:
        for chr_,pos,ref,alt in sites:
            if alt=='<NON_REF>' : continue
            site_dict[':'.join([chr_,pos,ref,alt])] = 0
            wr.write('\t'.join([chr_,str(int(pos)-1 -offset),  str(int(pos) + offset), ':'.join([chr_,pos,ref,alt])])+'\n')
    tmpfile=outf+'tmp.fa'
    
    print 'generate the fasta sequences of variants'
    syscall='bedtools getfasta -fi %s -bed %s -fo %s -name'%(fasta,outf+'tmp.bed',tmpfile)
    print syscall
    return_code = subprocess.call(syscall,shell =True)
    if return_code != 0:
        raise
    #how that I have the fasta sequences of the ref around variant pos, check if homopolymer
    seq = []
    homopol = None
    
    print ' now scan all of them to see which ones are in homopolymer region and report variant context'
    with open(tmpfile) as rd, open(outf,'w') as wr, open(outf_context,'w') as wr_context:
        for line in rd:
            if line.startswith('>'):
                key = line.strip().replace('>','',1)

            else:
                seq = line.strip()
                char_ = seq[offset]
                if char_*(offset+1) in seq:
                    #homopolymer region affecting our nucleotide
                    homopol = 1
                    wr.write(key.replace(':','\t') + '\t' + str(homopol) + '\n')
                    context = ''.join(seq[offset-1:offset+2]).upper()
                    wr_context.write(key.replace(':','\t') + '\t' + context + '\n')
                else:
                    homopol=0
                    #more relaxed, any homopolymer is enough (size offset)
                    nt = ['A','T','G','C']
                    homopol = [x*4 for x in nt]
                    if any(x in seq for x in homopol):
                        homopol = 1
                        wr.write(key.replace(':','\t') + '\t' + str(homopol) + '\n')                            
                    #context part of it
                    context = ''.join(seq[offset-1:offset+2]).upper()
                    wr_context.write(key.replace(':','\t') + '\t' + context + '\n')   
                key = None
                    
                           
            
    
    os.unlink(tmpfile)
    os.unlink(outf+'tmp.bed')
    
    return None



def add_filter_field(infile,outfile,ID_info,context_file):
    
    #idea of this is
    # scan ID_info to gather all variants into a dictionary
    # then scan infile and alter filter
    var_dict = dict()
    
    df = pd.read_csv(ID_info,sep='\t', low_memory=False))
    #columns : ['Splice','RNAEdit, RepMask,]
    colnames = list(df.columns)
    print colnames
    dict_of_vars = {key:  df[key].dropna().tolist() for key in colnames}
    print colnames
    
    global_dict = dict()
    for  key in colnames:
        tmpdict = { id_ : key for id_ in dict_of_vars[key]}
        
        #now we have to merge it with the global dict
        shared = {k: global_dict[k] +';'+ v for k, v in tmpdict.iteritems() if k in global_dict}
        #now let's update stuff:
        tmpdict.update(global_dict)
        tmpdict.update(shared)
        global_dict = tmpdict
    
    context_dict= dict()
    with open(context_file) as rd:
        for line in rd:
            ff= line.strip().split('\t')
            key = ':'.join(ff[0:4])
            val = ff[4]
            context_dict[key] = val

        
    with  open(infile) if infile.endswith('vcf') else gzip.open(infile) as rd, open(outfile,'w') as wr:
        for line in rd:
            if "1/2" in line :
                print line
                print infile
                print 'ERROR ###########################'
                print 'The VCF file input of this tool should only be composed of biallelic sites'
                print '#################################'
                raise
            if line.startswith('##'): wr.write(line)
            elif line.startswith('#'):
                for i in set(global_dict.values()):
                    Filter_str = i.split(';')
                    Filter_str  = [ x.replace('All_var','.') for x in Filter_str if x ]
                    Filter_str = ';'.join(Filter_str).replace(';.','').replace('.;','')
                    wr.write('##FILTER=<ID=%s,Description="Dummy"\n'%Filter_str)
                wr.write('##INFO=<ID=Context,Number=1,Type=String,Description="Variant trinucleotide context">\n')

                wr.write(line)
            else:
                ff= line.strip().split('\t')
                if ff[4]=='<NON_REF>' : continue
                ID_ = ':'.join([ff[0],ff[1],ff[3],ff[4]])
                #Filter_str = [key if ID_ in dict_of_vars[key] else '' for key in colnames ]
                Filter_str = global_dict.get(ID_,'').split(';')
                Filter_str  = [ x.replace('All_var','.') for x in Filter_str if x ]
                ff[6] = ';'.join(Filter_str).replace(';.','').replace('.;','')
                
                #add context:
                val_context = context_dict.get(ID_,'NA')
                ff[7] = ff[7]+';Context=%s'%val_context
                
                wr.write('\t'.join(ff) + '\n')
    
    
    return None

def main (args):
    samfile = pysam.Samfile(args.bam, "rb")
    sites = []
    print '###############################################################'
    print ' Step 0 generate sites from VCF for steps validation'
    print '###############################################################'
    
    with  open(args.vcf) if args.vcf.endswith('vcf') else gzip.open(args.vcf) as rd:
        for line in rd:
            if line.startswith('#'): continue
            
            else:
                ff= line.strip().split('\t')
                if ff[4]=='<NON_REF>' : continue
                sites.append((ff[0],ff[1],ff[3],ff[4]))

    
    #run the pysam stuff
    print '###############################################################'
    print '# Step 1 : support from first 6 bp of reads'
    print '###############################################################'

    with open(args.outfile +'_step1.csv','w') as wr:
       wr.write('skipped step')
    step1_start_end_read(samfile,sites,args.outfile +'_step1.csv')
    
    # Step 2 : Repeat Masker overlap
    print '###############################################################'
    print '# Step 2 : Repeat Masker overlap'
    print '###############################################################'
    overlap_vcf_with_bed(args.vcf,args.repmask,args.outfile+'_step2_repmask.csv')
    
    #Step 3: Overlap with 4bp intronic regions
    print '###############################################################'
    print '# Step 3: Overlap with 4bp intronic regions'
    print '###############################################################'
    overlap_vcf_with_bed(args.vcf,args.intron,args.outfile+'_step3_splice_site.csv')
     
    #Step 4: Homopolymer identification
    print '###############################################################'
    print '# Step 4: Homopolymer identification and Context report'
    print '###############################################################'
    step4_homopolymer(args.ref,sites,args.outfile + '_step4_homopolymer.csv',args.outfile + '_step6_context.csv')
    
    #Step 5: Overlap common RNA editing values:
    print '###############################################################'
    print '# Step 5: Overlap common RNA editing values'
    print '###############################################################'
    overlap_vcf_with_bed(args.vcf,args.rnaedit,args.outfile+'_step5_RNA_edit.csv')
    
 
    
    #Evaluate output some standard VCF file with all and only the variants
    #homogeneize IDs and run some Rscript statistics of overlaps
    #maybe plots with UpSetR
    import os
    scriptpath = (os.path.dirname(os.path.realpath(__file__)))
    realpath  = (os.path.dirname(os.path.realpath(args.outfile +'_step1.csv')))
    with open(args.outfile +'All_var_idx.txt','w') as wr:
        for chr_,pos,ref,alt in sites:
            wr.write(':'.join([chr_,pos,ref,alt])+'\n')
         
    try:
        os.unlink("%s"%(args.outfile + '_allIDs.csv'))
    except:
        pass
    syscall = """
    cd %s
    awk '$5>=0.5 {print $1 ":" $2 ":" $3 ":" $4}' %s |grep -v Ref > %s/First_bases_idx.txt
    awk  '{print $1 ":" $2 ":" $3 ":" $4}' %s > %s/RepMask_idx.txt
    awk  '{print $1 ":" $2 ":" $3 ":" $4}' %s > %s/Splice_idx.txt
    awk  '{print $1 ":" $2 ":" $3 ":" $4}' %s > %s/Homopolymer_idx.txt
    awk  '{print $1 ":" $2 ":" $3 ":" $4}' %s | grep -e ":A:G$" -e ":T:C$" > %s/RNAEdit_idx.txt
    for i in *_idx.txt; do echo $i > tmp.txt ; cat $i >> tmp.txt; mv tmp.txt $i ;done
    paste *_idx.txt > all_IDs    
    #touch all_IDs ; for i in *_idx.txt ; do echo $i > a.txt ; awk -F '\\t' '{print $1}' $i | sort |uniq|grep -v ID  >> a.txt; paste  a.txt  all_IDs| column -s $';' -t > b.txt; rm a.txt ; mv b.txt all_IDs ; echo $i ; done
    sed -i 's/_idx.txt//g' all_IDs
    sed -i "s/\\t%sAll_var/\\tAll_var/g" all_IDs
    sed  -i 's/\t$//' all_IDs
    mv all_IDs %s
    #Rscript %s/Rplot.R %s %s
    rm *_idx.txt
    
    """%(realpath,
         args.outfile +'_step1.csv',realpath,
         args.outfile+'_step2_repmask.csv',realpath,
         args.outfile+'_step3_splice_site.csv' ,realpath,
         args.outfile + '_step4_homopolymer.csv',realpath,
         args.outfile +'_step5_RNA_edit.csv',realpath,
         args.outfile.split('/')[-1],
         args.outfile + '_allIDs.csv',
         scriptpath,
         args.outfile + '_allIDs.csv',
         args.outfile+'_Rplot.pdf')
    print syscall
     
    return_code = subprocess.call(syscall,shell =True)
    print 'adding filter'
    add_filter_field( args.vcf, args.outfile.replace('.vcf.gz','')+'_filtered_file.vcf', args.outfile + '_allIDs.csv',args.outfile + '_step6_context.csv')
    
    syscall = """
    bgzip -f %s
    tabix -f %s
    """%(args.outfile.replace('.vcf.gz','')+'_filtered_file.vcf',args.outfile.replace('.vcf.gz','')+'_filtered_file.vcf.gz')
    
    return_code = subprocess.call(syscall,shell =True)
    print syscall
    return None


main(args)




