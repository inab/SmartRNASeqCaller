set -e
############################################################
##  Required resources
############################################################
REPOSITORY_PATH='./' # base path of SmartRNASeqCaller
REF='myfasta.fa'  #needs to have .fai and .dict files too
REPMASK=$REPOSITORY_PATH'/resources/hg19/repmasker_hg19.bed.gz'
SPLICE4BP=$REPOSITORY_PATH'/resources/hg19/ens_intron_hg19_slice_4bp.bed.gz'
RNAEDIT=$REPOSITORY_PATH'/resources/hg19/merged_RNA_edit.bed.gz'
MODEL=$REPOSITORY_PATH'/resources/RNA_Variant_RF_model.rds'
REPOSITORY_PATH=$REPOSITORY_PATH
GATK='path to GATK/GenomeAnalysisTK.jar' #GATK 3.6.0!

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
    if [[ $BNAME == *".vcf" ]] ;
    then 
      bgzip -c $VCF > $RESFOLDER/$BNAME".gz"
      INFILE=$BNAME".gz"
    else
      INFILE=$BNAME
      cp $BNAME $RESFOLDER/$BNAME
    fi

    tabix -f $RESFOLDER/$INFILE      
    
    bcftools norm  -m - \
    --fasta $REF \
    -o $RESFOLDER/$OUTPREFIX"_normalized.vcf"  \
    $RESFOLDER/$BNAME > $RESFOLDER/"Normalization.log" 2>&1

echo '-----------------------------------------------------'
echo 'Adding GATK annotation fields'
echo '-----------------------------------------------------'
echo ' -- Check log :'$RESFOLDER/"Annotation.log" 2>&1

ANNOTATIONS=$(python $REPOSITORY_PATH/parse_header.py $RESFOLDER/$OUTPREFIX"_normalized.vcf")

java -jar $GATK \
       -R $REF \
       -T VariantAnnotator \
       -I $BAM \
       -V $RESFOLDER/$OUTPREFIX"_normalized.vcf"  \
       -o $RESFOLDER/$OUTPREFIX"_normalized.annotated.vcf"  \
       -L $RESFOLDER/$OUTPREFIX"_normalized.vcf" $ANNOTATIONS \
         > $RESFOLDER/"Annotation.log" 2>&1

echo '-----------------------------------------------------'
echo 'Post process analysis'
echo '-----------------------------------------------------'
echo ' -- Check log :' $RESFOLDER/"Classification.log"
python  $REPOSITORY_PATH/RNA_post_analysis.py \
 --bam $BAM \
 --vcf $RESFOLDER/$OUTPREFIX"_normalized.annotated.vcf"  \
 --outfile $RESFOLDER/$OUTPREFIX  \
 --ref $REF  \
 --repmask $REPMASK  \
 --intron $SLICE4BP  \
 --rnaedit $RNAEDIT > $RESFOLDER/"Postprocess.log" 2>&1

echo '-----------------------------------------------------'
echo 'Prepare input for classification'
echo '-----------------------------------------------------'
echo ' -- Check log : ' $RESFOLDER/"Classification.log"
 python $REPOSITORY_PATH/prepare_vcf_for_rf.py \
    --vcf $RESFOLDER/$OUTPREFIX"_filtered_file.vcf.gz"  \
     --outfile $RESFOLDER/$OUTPREFIX"_postprocessed.csv"  > $RESFOLDER/"Prepare_input_classification.log" 2>&1
 
echo '-----------------------------------------------------'
echo 'Classification' 
echo '-----------------------------------------------------'
echo ' -- Check log : ' $RESFOLDER/"Classification.log"
Rscript $REPOSITORY_PATH/predict_variants.R \
      --model $MODEL \
      --input $RESFOLDER/$OUTPREFIX"_postprocessed.csv"  \
      --out $RESFOLDER/$OUTPREFIX"_classified.tmp.csv"  > $RESFOLDER/"Classification.log" 2>&1

echo '-----------------------------------------------------'
echo 'Final step: output vcf files generation'
echo '-----------------------------------------------------'
echo ' -- Check log : ' $RESFOLDER/"Output_generation.log"
python $REPOSITORY_PATH/split_vcf.py \
        -c $RESFOLDER/$OUTPREFIX"_classified.tmp.csv" \
        -v $RESFOLDER/$OUTPREFIX"_filtered_file.vcf.gz" \
	--GTdict $RESFOLDER/$OUTPREFIX"_postprocessed.csvGT_dict.pk"\
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
 do if [ ${i: -4} != ".log" ] && [ ${i: -7} != "_ok.vcf" ] && [ ${i: -7} != "_ko.vcf" ]  && [ ${i: -11} != "skipped.vcf"  ] 
  then
     rm $i
   fi
 done


 


