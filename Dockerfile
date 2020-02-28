#Base image load
FROM continuumio/miniconda2:4.7.12
# FROM biocontainers/biocontainers:latest

# Metadata
LABEL base.image="continuumio/miniconda2:4.7.12" \
	version="2" \
	software="SmartRNASeqCaller" \
	software.version="0.2" \
	description="SmartRNASeqCaller allows refining VCF calls for germline variants from RNASeq data" \
	description="This image comes with all required packages to run the tools in the github repo" \
	website="https://github.com/inab/SmartRNASeqCaller" \
	documentation="" \
	license="LGPL-3" \
	tags="Genomics;Transcriptomics"

# Maintainer
MAINTAINER Mattia Bosio <mattia.bosio@bsc.es>
MAINTAINER José María Fernández <jose.m.fernandez@bsc.es>

ARG	DESTDIR=/opt/SmartRNASeqCaller/
ARG	BUILDDIR=/tmp/build/

#USER root
COPY docker/ /tmp/build/
RUN /tmp/build/docker-build.sh "${DESTDIR}"
COPY SmartRNASeqCaller/ ${DESTDIR}
RUN cp -p "${BUILDDIR}"/docker-entrypoint.sh "${DESTDIR}" && mkdir -p "${DESTDIR}"/resources && rm -rf "${BUILDDIR}"


#RUN conda install bcftools=1.6
#RUN conda install tabix
#RUN conda install bedtools=2.25.0
#
#RUN conda install pysam=0.13
#RUN conda install pandas=0.20.3
#RUN conda install -c conda-forge r=3.5.0
## RUN conda install -c conda-forge/label/cf201901 r-caret  
#RUN Rscript -e 'install.packages("ranger", repos="http://cran.us.r-project.org")'
#
#WORKDIR /data/
#
##RUN conda install -c anaconda util-linux
#RUN Rscript -e 'install.packages("caret", repos="http://cran.us.r-project.org")'
#RUN Rscript -e 'install.packages("e1071", repos="http://cran.us.r-project.org")'
#
#USER root
#RUN mkdir -p /opt/SmartRNASeqCaller/
#
##COPY SmartRNASeqCaller/ /opt/SmartRNASeqCaller/
#RUN Rscript -e 'install.packages("optparse", repos="http://cran.us.r-project.org")'
#RUN Rscript -e 'install.packages("UpSetR", repos="http://cran.us.r-project.org")'




#RUN rm -rf /opt/SmartRNASeqCaller/*
#RUN cd /opt; git clone https://github.com/inab/SmartRNASeqCaller.git
#RUN cd /opt/SmartRNASeqCaller/resources ; wget https://zenodo.org/record/1473507/files/RNA_Variant_RF_model.rds
#RUN echo 'update'
#RUN cd /opt/SmartRNASeqCaller; git pull


#USER biodocker

ENTRYPOINT	[ "/opt/SmartRNASeqCaller/docker-entrypoint.sh" ]
