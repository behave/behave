#!/bin/sh
# =============================================================================
# BOOTSTRAP PROJECT: Download all requirements
# =============================================================================
# : ${PIP_INDEX_URL="https://pypi.python.org/simple"}
# test ${PIP_DOWNLOADS_DIR} || mkdir -p ${PIP_DOWNLOADS_DIR}
# tox -e init

set -e

# -- CONFIGURATION:
HERE=`dirname $0`
TOP="${HERE}/.."
: ${PIP_DOWNLOAD_DIR:="${TOP}/downloads"}
export PIP_DOWNLOAD_DIR

if [ $# -ge 1 ]; then
    PIP_DOWNLOAD_DIR="$1"
fi

# -- EXECUTE STEPS:
echo "USING: PIP_DOWNLOAD_DIR=${PIP_DOWNLOAD_DIR}"
${HERE}/toxcmd.py mkdir ${PIP_DOWNLOAD_DIR}
pip install --download=${PIP_DOWNLOAD_DIR} -r ${TOP}/requirements/all.txt
${HERE}/make_localpi.py ${PIP_DOWNLOAD_DIR}

