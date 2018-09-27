set -e
############################################################
##  Required resources
############################################################
REF='myfasta.fa'  #needs to have .fai and .dict files too
REPMASK='repmask.bed'
SPLICE4BP='splice.bed'
RNAEDIT='rnaedit.bed'
MODEL='model.rds'
CODEFOLDER='PATH to SmartRNASeqCaller'
GATK='path to GATK/GenomeAnalysisTK.jar'

############################################################
##  Your input files
############################################################
BAM='your_bam_file.bam'   
VCF='your VCF file'

############################################################
##  Extra parameters
############################################################
RESFOLDER='output_folder'
OUTPREFIX='output_prefix_for_files'
RESFOLDER=$(realpath $RESFOLDER)
echo "Output path : $RESFOLDER"

############################################################
# EXECUTION
############################################################

# generating the output folder in case it does not exist

mkdir -p $RESFOLDER
if [ "$(ls -A $RESFOLDER)" ]; then
     echo "RESFOLDER must be empty"
     exit 1
fi


echo '-----------------------------------------------------'
echo 'Normalizing and splitting to biallelic sites'
echo '-----------------------------------------------------'
echo ' -- Check log :'$RESFOLDER/"Normalization.log"
    BNAME=$(basename $VCF)
    
    bgzip -c $VCF > $RESFOLDER/$BNAME".gz"
    tabix -f $RESFOLDER/$BNAME".gz"
    
    bcftools norm  -m - \
    --fasta $REF \
    -o $RESFOLDER/$OUTPREFIX"_normalized.vcf"  \
    $RESFOLDER/$BNAME".gz" > $RESFOLDER/"Normalization.log" 2>&1

echo '-----------------------------------------------------'
echo 'Adding GATK annotation fields'
echo '-----------------------------------------------------'
echo ' -- Check log :'$RESFOLDER/"Annotation.log" 2>&1

java -jar $GATK \
       -R $REF \
       -T VariantAnnotator \
       -I $BAM \
       -V $RESFOLDER/$OUTPREFIX"_normalized.vcf"  \
       -o $RESFOLDER/$OUTPREFIX"_normalized.annotated.vcf" \
       -A Coverage \
       -A LikelihoodRankSumTest \
       -A ReadPosRankSumTest \
       -A BaseQualityRankSumTest \
       -L $RESFOLDER/$OUTPREFIX"_normalized.vcf" > $RESFOLDER/"Annotation.log" 2>&1

echo '-----------------------------------------------------'
echo 'Post process analysis'
echo '-----------------------------------------------------'
echo ' -- Check log :' $RESFOLDER/"Classification.log"
/home/mbosio/anaconda2/bin/python  $CODEFOLDER/RNA_post_analysis.py \
 --bam $BAM \
 --vcf $RESFOLDER/$OUTPREFIX"_normalized.annotated.vcf"  \
 --outfile $RESFOLDER/$OUTPREFIX  \
 --ref $REF  \
 --repmask $REPMASK  \
 --intron $SPLICE4BP  \
 --rnaedit $RNAEDIT > $RESFOLDER/"Postprocess.log" 2>&1

echo '-----------------------------------------------------'
echo 'Prepare input for classification'
echo '-----------------------------------------------------'
echo ' -- Check log : ' $RESFOLDER/"Classification.log"
 /home/mbosio/anaconda2/bin/python $CODEFOLDER/prepare_vcf_for_rf.py \
    --vcf $RESFOLDER/$OUTPREFIX"_filtered_file.vcf.gz"  \
     --outfile $RESFOLDER/$OUTPREFIX"_postprocessed.csv"  > $RESFOLDER/"Prepare_input_classification.log" 2>&1
 
echo '-----------------------------------------------------'
echo 'Classification' 
echo '-----------------------------------------------------'
echo ' -- Check log : ' $RESFOLDER/"Classification.log"
Rscript $CODEFOLDER/predict_variants.R \
      $MODEL \
      $RESFOLDER/$OUTPREFIX"_postprocessed.csv"  \
      $RESFOLDER/$OUTPREFIX"_classified.tmp.csv"  > $RESFOLDER/"Classification.log" 2>&1

echo '-----------------------------------------------------'
echo 'Final step: output vcf files generation'
echo '-----------------------------------------------------'
echo ' -- Check log : ' $RESFOLDER/"Output_generation.log"
/home/mbosio/anaconda2/bin/python $CODEFOLDER/split_vcf.py \
        -c $RESFOLDER/$OUTPREFIX"_classified.tmp.csv" \
        -v $RESFOLDER/$OUTPREFIX"_filtered_file.vcf.gz" \
        -o $RESFOLDER/$OUTPREFIX  > $RESFOLDER/"Output_generation.log" 2>&1


echo '-----------------------------------------------------'
echo 'Finished processing the sample:'
echo '  The VCF file with passed variants is: ' $RESFOLDER/$OUTPREFIX"_ok.vcf"
echo '  The VCF file with filtered variants is: ' $RESFOLDER/$OUTPREFIX"_ko.vcf"
echo '-----------------------------------------------------'

echo '-----------------------------------------------------'
echo 'Cleanup'
echo '-----------------------------------------------------'

for i in  $RESFOLDER/*
 do if [ ${i: -4} != ".log" ] && [ ${i: -7} != "_ok.vcf" ] && [ ${i: -7} != "_ko.vcf" ] 
  then
     rm $i
   fi
 done


 

