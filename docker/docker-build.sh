#!/bin/sh

set -e

SCRIPTDIR="$(dirname "$0")"

if test $# -gt 0 ; then
	DESTDIR="$1"
fi

DESTDIR="${DESTDIR:-/opt/SmartRNASeqCaller/}"

case "$SCRIPTDIR" in
	/*)
		true
		;;
	*)
		SCRIPTDIR="${PWD}/${SCRIPTDIR}"
		;;
esac

conda install --file "${SCRIPTDIR}"/bioconda_spec-file.txt
conda install -c conda-forge --file "${SCRIPTDIR}"/conda-forge_spec-file.txt
cp "${SCRIPTDIR}" "${DESTDIR}"

# conda-forge 'r-ranger'
# Rscript -e 'install.packages("ranger", repos="http://cran.us.r-project.org")'

# conda-forge 'r-caret'
# Rscript -e 'install.packages("caret", repos="http://cran.us.r-project.org")'

# conda-forge 'r-e1071'
# Rscript -e 'install.packages("e1071", repos="http://cran.us.r-project.org")'

# conda-forge 'r-optparse'
# Rscript -e 'install.packages("optparse", repos="http://cran.us.r-project.org")'

# conda-forge 'r-upsetr'
# Rscript -e 'install.packages("UpSetR", repos="http://cran.us.r-project.org")'

#cd /opt/SmartRNASeqCaller/resources
#wget https://zenodo.org/record/1473507/files/RNA_Variant_RF_model.rds 
