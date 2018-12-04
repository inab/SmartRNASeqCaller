#Base image load
FROM biocontainers/biocontainers:latest

# Metadata
LABEL base.image="biocontainers:latest"
LABEL version="1"
LABEL software="SmartRNASeqCaller"
LABEL software.version="0.1"
LABEL description="SmartRNASeqCaller allows refining VCF calls for germline variants from RNASeq data"
LABEL description="This image comes with all required packages to run the tools in the github repo"
LABEL website=""
LABEL documentation=""
LABEL license=""
LABEL tags="Genomics;Transcriptomics"

# Maintainer
MAINTAINER Mattia Bosio <mattia.bosio@bsc.es>

RUN conda install bcftools=1.3.1
RUN conda install tabix
RUN conda install bedtools=2.25.0

RUN conda install pysam=0.13
RUN conda install pandas=0.20.3
RUN conda install -c conda-forge r=3.5.0
RUN conda install -c conda-forge r-caret 
RUN Rscript -e 'install.packages("ranger", repos="http://cran.us.r-project.org")'

WORKDIR /data/

#RUN conda install -c anaconda util-linux
RUN Rscript -e 'install.packages("caret", repos="http://cran.us.r-project.org")'
RUN Rscript -e 'install.packages("e1071", repos="http://cran.us.r-project.org")'

USER root
RUN mkdir -p /opt/SmartRNASeqCaller/

#COPY SmartRNASeqCaller/ /opt/SmartRNASeqCaller/
RUN Rscript -e 'install.packages("optparse", repos="http://cran.us.r-project.org")'
RUN cd /opt; git clone https://github.com/inab/SmartRNASeqCaller.git
RUN rm -rf /opt/SmartRNASeqCaller/*
RUN cd /opt/SmartRNASeqCaller/resources ; wget https://sandbox.zenodo.org/record/249252/files/RNA_Variant_RF_model.rds



USER biodocker
 
