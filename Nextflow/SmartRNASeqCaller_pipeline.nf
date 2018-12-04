/*
 *
 *   This file takes care to postrprocess a VCF call + BAM file for RNA seq Germline variant calling.
 */
 
/* 
 * 
 * Authors:
 * - Mattia Bosio <mattia-.bosio85@gmail.com>
 */ 

 
/*
 * Default pipeline parameters. They can be overriden on the command line eg. 
 * given `params.foo` specify on the run command line `--foo some_value`.  
*/


/ my inputs - outputs/
python = params.python

OUTPREFIX = params.OUTPREFIX
log.info """
         
                   P I P E L I N E    
         ===================================
         ## Input data and prefix
         Input BAM file:  ${params.bam}
         Input BAI file:  ${params.bai}
         Input VCF file:  ${params.vcf}
         Output folder :  ${params.outdir}
         Output prefix :  ${params.OUTPREFIX}
         
         ## Reference resuources
         Genome fasta :  ${params.ref}
         Fasta index  :  ${params.ref_fai}
         Faste Dict   :  ${params.ref_dict}
         Bed repmask  :  ${params.repmask_bed}
         Bed introns  :  ${params.intron_bed}
         Bed RNA edit :  ${params.rnaedit_bed}
         Model file   :  ${params.model}
         
         ## Paths to tools
         GATK             : ${params.GATK}
         SmartRNASeqCaller:  ${params.pp_path}  
         
         """
         .stripIndent()

postprocess_path = params.pp_path

bam_file  = file(params.bam)
bai_file  = file(params.bai)
vcf_file  = file(params.vcf)

ref_file_ch  = Channel.fromPath(params.ref)
ref_file_ch.into { ref_file; ref_file_2;ref_file_3 }

ref_fai_ch  = Channel.fromPath(params.ref_fai)
ref_fai_ch.into {ref_fai_1; ref_fai_2 ; ref_fai_3}

ref_dict_ch  = Channel.fromPath(params.ref_dict)

repmask_bed_ch = Channel.fromPath(params.repmask_bed)
intron_bed_ch  = Channel.fromPath(params.intron_bed)
rnaedit_bed_ch = Channel.fromPath(params.rnaedit_bed)

model_ch  = Channel.fromPath(params.model)

/*
*  Step 1 : split VCF and normalize variants, all biallelic
*  Step 2 : take BAM and VCF and add GATK annotations needed for model
*  Step 3 : Filter variants with GATK
*  Step 4 : Annotate VCF: RNA_post_analysis.py
*  Step 5 :  Add RF model estimation : [to do]
*  Step 6 : Use the R estimations to filter VCF
*/
 
process normalize {
    tag "Normalization"
     
    input:
    file vcf_in from vcf_file
    file fasta_ref from ref_file
     
    output:
    file("normalized.vcf") into normalized_vcf
 
    script:
    """
    bgzip $vcf_in
    tabix $vcf_in".gz"
    bcftools norm  -m - --threads $task.cpus --fasta $fasta_ref -o normalized.vcf  $vcf_in".gz"
    """ 
}




process GATK_annotate {
    tag "GATK annotation"
				
    input:
    file fasta_ref from ref_file_2
    file fai_ref from ref_fai_1
    file dict_ref from ref_dict_ch
    file vcf_in from normalized_vcf
				file bam_in_annotate from bam_file
				file bai_in_annotate from bai_file
				
    output:
    file( "normalized.annotated.vcf") into normalized_annotated_vcf


    script:
    """
				 java -jar $params.GATK \
       -R $fasta_ref \
       -T VariantAnnotator \
       -I $bam_in_annotate \
       -V $vcf_in  \
       -o normalized.annotated.vcf \
       -A Coverage \
       -A LikelihoodRankSumTest \
       -A ReadPosRankSumTest \
       -A BaseQualityRankSumTest \
       -A DepthPerAlleleBySample \
       -L $vcf_in \
    """  
}  
  
  
/*expand normalized channel into two because I need it
* for later 2 processes, postprocess and classify
*/
normalized_annotated_vcf.into {
  normalized_annotated_vcf_2
  normalized_annotated_vcf_3
}



process variant_post_process{
  tag "Variant Call postprocess "

  
  input:
    file bam_in_annotate from bam_file
				file bai_in_annotate from bai_file
				file vcf_file_pp from normalized_annotated_vcf_2
				file ref_pp from ref_file_3
				file fai_pp from ref_fai_2
				
				file bed_repmask from repmask_bed_ch
				file bed_intron from intron_bed_ch
				file bed_rnaedit from rnaedit_bed_ch
   
  output:
    file("postprocess_filtered_file.vcf.gz") into filtered_vcf_gz
    file("postprocessed.csv") into pp_csv_out
    
   
  script:
  """ 
    echo "post analysis Step 1"
    # require samtools, bcftools, python with pysam etc, look at Readme

    #export PATH=$PATH:$postprocess_path
    
    
    $python  $postprocess_path/RNA_post_analysis.py \
     --bam $bam_in_annotate \
     --vcf $vcf_file_pp  \
     --outfile ${OUTPREFIX}  \
     --ref $ref_pp  \
     --repmask  $bed_repmask  \
     --intron   $bed_intron  \
     --rnaedit  $bed_rnaedit
    
     $python $postprocess_path/prepare_vcf_for_rf.py --vcf ${OUTPREFIX}_filtered_file.vcf.gz --outfile postprocessed.csv
     
  """
   

}
 
 

process classify_variants{
  tag "Variant Classify "

  publishDir params.outdir, mode:'copy'
  
  input:
				file vcf_file_classify from filtered_vcf_gz
				file csv_file_pp  from pp_csv_out
				file model_ch_file from model_ch
  output:
    file(params.OUTPREFIX + "_ok.vcf") into vcf_ok
    file(params.OUTPREFIX + "_ko.vcf") into vcf_ko
    
   
  script:
  """ 
    echo "post analysis Step 2"
    Rscript $postprocess_path/predict_variants.R --model $model_ch_file --input $csv_file_pp --out classified.tmp.csv
    
    echo "Now I have to filter VCF for ok and filtered samples"
    $python $postprocess_path/split_vcf.py \
        -c classified.tmp.csv \
        -v $vcf_file_classify \
        -o ${OUTPREFIX}
  """
   
} 

 
workflow.onComplete { 
	println ( workflow.success ? "\nDone! Open the following report\n" : "Oops .. something went wrong" )

} 
