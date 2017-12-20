#!/bin/sh
# =============================================================================
# BOOTSTRAP PROJECT: Download all requirements
# =============================================================================
# : ${PIP_INDEX_URL="https://pypi.python.org/simple"}
# test ${PIP_DOWNLOADS_DIR} || mkdir -p ${PIP_DOWNLOADS_DIR}
# tox -e init
# export PIP_DOWNLOAD_DIR

set -e

# -- CONFIGURATION:
HERE=`dirname $0`
TOP="${HERE}/.."
: ${PIP_DOWNLOAD_DIR:="${TOP}/downloads"}
REQUIREMENTS_FILE=${TOP}/py.requirements/all.txt

if [ $# -ge 1 ]; then
    PIP_DOWNLOAD_DIR="$1"
fi
if [ $# -ge 2 ]; then
    REQUIREMENTS_FILE="$2"
fi

# -- EXECUTE STEPS:
echo "USING: PIP_DOWNLOAD_DIR=${PIP_DOWNLOAD_DIR}"
${HERE}/toxcmd.py mkdir ${PIP_DOWNLOAD_DIR}
pip install --download=${PIP_DOWNLOAD_DIR} -r ${REQUIREMENTS_FILE}
${HERE}/make_localpi.py ${PIP_DOWNLOAD_DIR}

