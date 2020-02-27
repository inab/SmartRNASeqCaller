# SmartRNASeqCaller

SmartRNASeqCaller is a post-processing pipeline to improve germline variant calling from RNA-Seq data.
It takes as input the result from a variant calling pipeline (e.g. GATK best practices)  and outputs two VCF files:
 
 - One with the variants classified as potential germline variants xxx_ok.vcf
 - One with all the remaining variants xxx_ko.vcf

SmartRNASeqCaller can be executed locally with a shell script (SmartSeqCaller.sh) by editing the variables at the header of the file. It also includes **Nextflow** implementations that can be executed locally, or using a combination of Dockers to ensure reproducibility.

The classification is done with a Random Forest model that you can download from `https://zenodo.org/record/1473507/files/RNA_Variant_RF_model.rds` ([![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1473507.svg)](https://doi.org/10.5281/zenodo.1473507)) using several annotations from the VCF file, plus using criteria from previous works. SmartRNASeqCaller achieves better precision-recall results thanks to the classification module, that integrates several sources of information inferring non-linear dependencies.

**Suggestion**: download the Random forest module in the resource folder of this git repository so to keep everything tidy.


### Requirements:
SmartRNASeqCaller expects the user to have a processed reference fasta file as required by GATK guidelines, meaning having a .fai and .dict files before starting the process.

It also requires a set of bed files (provided under `resources` both for [hg19](resources/hg19) and [GRCh38/hg38](resources/hg38)) with:
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
Further on you can test on an example using the examples scripts with nextflow execution with Docker straight away.
To build the docker image needed for SmartRNASeqCaller, execute the following statement from the base folder of SmartRNASeqCaller

```bash
docker build -t smartrnaseqcaller:latest Docker/.
```

This will build a Docker image named `smartrnaseqcaller:latest`, which can then be used in combination with nextflow `-with-docker` parameter.
You also need [GATK 3.6.0 Docker](https://hub.docker.com/r/broadinstitute/gatk3). This can be obtained running :

```bash
docker pull broadinstitute/gatk3:3.6-0
```

### Local execution:
The [SmartRNASeq.sh](SmartRNASeq.sh) file contains a sample pipeline with few parameters to set at the beginning of the script.

### Nextflow executions:  
For running with [Nextflow](https://www.nextflow.io/), we require also to have nextflow up and running. This will enable the execution with Docker containers (see [examples](https://github.com/inab/SmartRNASeqCaller/blob/master/Nextflow/exec_line.sh)  in `Nextflow` folder)
