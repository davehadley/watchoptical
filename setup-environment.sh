#!/usr/bin/env bash

if [ -n "$BASH_SOURCE" ]; then
  script=$BASH_SOURCE
elif [ -n "$ZSH_VERSION" ]; then
  setopt function_argzero
  script=$0
elif eval '[[ -n ${.sh.file} ]]' 2>/dev/null; then
  eval 'script=${.sh.file}'
else
  script=./
fi
scriptdir=$(dirname ${script})

if [ -z "${WORKSPACE}" ];
then
    export WATCHOPTICALWORKSPACE=$(CDPATH= cd -- "${scriptdir}" && pwd -P)
else
    export WATCHOPTICALWORKSPACE=${WORKSPACE}
fi

CONDABIN=${WATCHOPTICALWORKSPACE}/miniconda/bin
CONDAACTIVATE=${CONDABIN}/activate
CONDA=${CONDABIN}/conda

# If conda is not installed, download miniconda
if ! command -v ${CONDA} &> /dev/null
then
    echo "conda not found at ${CONDA}"
    WATCHOPTICALMINICONDA=${WATCHOPTICALWORKSPACE}/miniconda
    if [ ! -d "${WATCHOPTICALMINICONDA}" ]
    then
        echo "Downloading miniconda..."
        case "$(uname -s)" in
            Darwin*)    OSKIND=MacOSX;;
            *)          OSKIND=Linux;;
        esac
        echo "Detected OS = ${OSKIND}"
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-${OSKIND}-x86_64.sh -nv -O miniconda.sh
        bash miniconda.sh -b -p ${WATCHOPTICALMINICONDA}
        source ${WATCHOPTICALMINICONDA}/bin/activate
        ${CONDA} config --set always_yes yes
        ${CONDA} config --set env_prompt '({name}) '
        ${CONDA} update -q conda
    fi
    source ${WATCHOPTICALMINICONDA}/bin/activate
    if ! command -v ${CONDA} &> /dev/null
    then
        echo "ERROR: cannot find conda command!"
    fi
fi

# If environment does not exist, create it
WATCHOPTICALCONDAENV=${WATCHOPTICALWORKSPACE}/env/watchoptical
if [ ! -d "${WATCHOPTICALCONDAENV}" ]
then 
    ${CONDA} env create -f environment.yml --prefix ${WATCHOPTICALCONDAENV}
    # struggled to get poetry to work in the environment file so get it from pip
    pip install poetry
fi

# Activate the environment
source ${CONDAACTIVATE}
#${CONDA} activate ${WATCHOPTICALCONDAENV}
source activate ${WATCHOPTICALCONDAENV}

export RATROOT=${WATCHOPTICALWORKSPACE}/build/rat-pac
export RATSHARE=${WATCHOPTICALWORKSPACE}/external/rat-pac
export GLG4DATA=${WATCHOPTICALWORKSPACE}/external/rat-pac/data
export PATH=${WATCHOPTICALWORKSPACE}/build/bonsai:${RATROOT}/bin:${PATH}
export BONSAIDIR=${WATCHOPTICALWORKSPACE}/build/bonsai
export LD_LIBRARY_PATH=${BONSAIDIR}:${RATROOT}/lib:${LD_LIBRARY_PATH}
export WATCHENV=${WATCHOPTICALWORKSPACE}/external/watchmakers

# stop pip asking for a password 
# see: https://github.com/jaraco/keyring#disabling-keyring
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring