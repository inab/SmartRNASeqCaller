#!/bin/sh

RESDIR=/opt/SmartRNASeqCaller/resources
MODELFILE=RNA_Variant_RF_model.rds
MODEL_BASEURL=https://zenodo.org/record/1473507/files/
ASSEMBLIES_BASEURL=https://raw.githubusercontent.com/inab/SmartRNASeqCaller/master/resources/
ASSEMBLIES="hg19 hg38"

if [ ! -r "${RESDIR}"/"${MODELFILE}" ] ; then
	(
		mkdir -p "${RESDIR}"
		cd "${RESDIR}"
		# One: materialize the directory
		for assemb in $ASSEMBLIES ; do
			mkdir -p "$assemb"
			DURL_PREFIX="${ASSEMBLIES_BASEURL}${assemb}/"
			for prefix in ens_intron_ repmasker_ ; do
				DURL_FILE_PREFIX="${prefix}${assemb}"
				DURL_FILE="${DURL_FILE_PREFIX}.bed.gz"
				NOCHR_DURL_FILE="${DURL_FILE_PREFIX}_nochr.bed.gz"
				
				if [ ! -r "$DURL_FILE" ] ; then
					wget -nv "${DURL_PREFIX}${DURL_FILE}"
					if [ $? != 0 ] ; then
						rm -f "$DURL_FILE"
						failed=1
						break
					fi
				fi
				
				if [ ! -r "$NOCHR_DURL_FILE" ] ; then
					wget -nv "${DURL_PREFIX}${NOCHR_DURL_FILE}"
					if [ $? != 0 ] ; then
						rm -f "$NOCHR_DURL_FILE"
						failed=1
						break
					fi
				fi
			done
			
			for indprefix in intron_4bp_splice_overlap merged_RNA_edit ; do
				DURL_FILE_PREFIX="${prefix}$"
				DURL_FILE="${DURL_FILE_PREFIX}.bed.gz"
				NOCHR_DURL_FILE="${DURL_FILE_PREFIX}_nochr.bed.gz"
				
				if [ ! -r "$DURL_FILE" ] ; then
					wget -nv "${DURL_PREFIX}${DURL_FILE}"
					if [ $? != 0 ] ; then
						rm -f "$DURL_FILE"
						failed=1
						break
					fi
				fi
				
				if [ ! -r "$NOCHR_DURL_FILE" ] ; then
					wget -nv "${DURL_PREFIX}${NOCHR_DURL_FILE}"
					if [ $? != 0 ] ; then
						rm -f "$NOCHR_DURL_FILE"
						failed=1
						break
					fi
				fi
			done
		done
		# Two: get the model
		if [ -z "$failed" ] ; then
			wget -nv "${MODEL_BASEURL}""${MODELFILE}" || rm -f "${MODELFILE}"
		fi
	)
fi

exec "$@"
