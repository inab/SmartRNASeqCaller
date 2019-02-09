# SmartRNASeqCaller

SmartRNASeqCaller is a post-processing pipeline to improve germline variant calling from RNA-Seq data.
It takes as input the result from a variant calling pipeline (e.g. GATK best practices)  and outputs two VCF files:
 
 - One with the variants classified as potential germline variants xxx_ok.vcf
 - One with all the remaining variants xxx_ko.vcf

SmartRNASeqCaller can be executed locally with a shell script (SmartSeqCaller.sh) by editing the variables at the header of the file. It also includes **Nextflow** implementations that can be executed locally, or using a combination of Dockers to ensure reproducibility.

The classification is done with a Random Forest model [https://sandbox.zenodo.org/record/249252/files/RNA_Variant_RF_model.rds
] using several annotations from the VCF file, plus using criteria from previous works. SmartRNASeqCaller achieves better precision-recall results thanks to the classification module, that integrates several sources of information inferring non-linear dependencies.

**Suggestion**: download the Random forest module in the resource folder of this git repository so to keep everything tidy.


### Requirements:
SmartRNASeqCaller expects the user to have a processed reference fasta file as required by GATK guidelines, meaning having a .fai and .dict files before starting the process.

It also requires a set od bed files (provdied under resources/hg19) with:
 - Repmask from UCSC regions
 - Regions containing the first 4bp of each of intron ends 
 - RNAEdit positions

For local execution there are a set of tools which are required for a proper execution
 - GATK 3.6-0
 - Samtools
 - Bcftools
 - Bedtools
 - tabix
 - Python 2.7: (pysam, pandas)
 - R 3.5.0 (caret, ranger) 

### Docker: 
You can build a Docker with all necessary components (except fasta file of genome) with the Dockerfile in the Docker folder.
Fruther on you can test on an example using the examples scripts with nextflow execution with Docker straight away.

### Local execution:
The SmartRNASeq.sh file contains a sample pipeline with few parameters to set at the beginnign of hte script.

### Nextflow executions:  
For running with [Nextflow](https://www.nextflow.io/), we require also to have nextflow up and running. This will enable the execution with Docker containers [see [examples](https://github.com/inab/SmartRNASeqCaller/blob/master/Nextflow/exec_line.sh)  in Nextflow folder]
