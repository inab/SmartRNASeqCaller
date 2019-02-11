Follow the instructions from this file to :
 - Download some example data from Zenodo that contain:
    - Sample VCF, BAM files for RNASeq data
    - Gold standard VCF variants to compare against
    - Needed references for this example
    - params.yaml file for docker execution with Nextflow

- Download the prediction model from:
  https://sandbox.zenodo.org/record/249252/files/RNA_Variant_RF_model.rds
  and put it in the resources/ folder 

- Make sure you have the needed docker images:
   - smartrnaseqcaller:latest
   - broadinstitute/gatk3:3.6-0

- Make sure you have nextflow installed

- Edit the params.yaml file in the example folder with the neede paths

- To launch the example with docker:  
   - [add command here ] 
