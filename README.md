# SmartRNASeqCaller

SmartRNASeqCaller is a post-processing pipeline to improve germline variant calling from RNA-Seq data.
It takes as input the result from a variant calling pipeline (e.g. GATK best practices)  and outputs two VCF files:
 

 - One with the variants classified as potential germline variants xxx_ok.vcf
 - One with all the remaining variants xxx_ko.vcf

SmartRNASeqCaller can be executed locally with a shell script (SmartSeqCaller.sh) by editing the variants at the header of the file. It also includes **Nextflow** implementations that can be executed locally, or using a combination of Dockers to ensure reproducibility.
The classification is done with a Random Forest model [https://sandbox.zenodo.org/record/249252/files/RNA_Variant_RF_model.rds
] using several annotations from the VCF file, plus using criteria from previous works like [1  -add link and ref]. SmartRNASeqCaller achieves better precision-recall results thanks to the classification module, that integrates several sources of information inferring non-linear dependencies.
### Installation 
...

### Usage examples

 - Local w/ script
 - Nextflow with local
 - Nextflow with Docker (implies building dockers before)

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
 
For running with Nextflow, we require also to have nextflow up and running. This will enable the execution with Docker containers [see [examples](https://github.com/inab/SmartRNASeqCaller/blob/master/Nextflow/exec_line.sh)  in Nextflow folder]
