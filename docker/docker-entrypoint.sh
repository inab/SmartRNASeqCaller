#!/bin/sh

BASEDIR="$(dirname "$0")"
case "$BASEDIR" in
	/*)
		true
		;;
	*)
		BASEDIR="${PWD}/${BASEDIR}"
		;;
esac

RESDIR="${BASEDIR}"/resources

# Bootstrapping the resources
"${BASEDIR}"/utils/SmartRNASeqCaller_bootstrap_resources.sh "${RESDIR}"

exec "$@"
